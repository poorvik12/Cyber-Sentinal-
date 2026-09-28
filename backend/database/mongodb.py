import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    MongoClient = None
    class PyMongoError(Exception):
        pass
from backend.config import MONGODB_URI, MONGODB_DB, FALLBACK_DIR

COLLECTIONS = ['security_events', 'threats', 'alerts', 'simulation_results', 'model_metrics']

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.use_mongo = False
        if MONGODB_URI and MongoClient is not None:
            try:
                self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=1500)
                self.client.admin.command('ping')
                self.db = self.client[MONGODB_DB]
                self.use_mongo = True
            except PyMongoError:
                self.use_mongo = False
        for name in COLLECTIONS:
            path = FALLBACK_DIR / f'{name}.json'
            if not path.exists():
                path.write_text('[]', encoding='utf-8')

    def _path(self, collection):
        return FALLBACK_DIR / f'{collection}.json'

    @staticmethod
    def _jsonable(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: Database._jsonable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [Database._jsonable(v) for v in obj]
        return obj

    def insert(self, collection: str, document: Dict[str, Any]):
        doc = self._jsonable(document)
        if self.use_mongo:
            return str(self.db[collection].insert_one(doc).inserted_id)
        data = json.loads(self._path(collection).read_text(encoding='utf-8'))
        data.append(doc)
        self._path(collection).write_text(json.dumps(data, indent=2), encoding='utf-8')
        return doc.get('event_id') or doc.get('alert_id') or str(len(data))

    def find(self, collection: str, query: Optional[Dict[str, Any]] = None, limit: int = 200):
        query = query or {}
        if self.use_mongo:
            docs = list(self.db[collection].find(query).sort('timestamp', -1).limit(limit))
            for d in docs:
                d['_id'] = str(d['_id'])
            return docs
        data = json.loads(self._path(collection).read_text(encoding='utf-8'))
        def matches(d):
            return all(d.get(k) == v for k, v in query.items())
        data = [d for d in data if matches(d)]
        data.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
        return data[:limit]

    def get(self, collection: str, key: str, value: str):
        if self.use_mongo:
            d = self.db[collection].find_one({key: value})
            if d:
                d['_id'] = str(d['_id'])
            return d
        for d in json.loads(self._path(collection).read_text(encoding='utf-8')):
            if d.get(key) == value:
                return d
        return None

    def count(self, collection: str):
        if self.use_mongo:
            return self.db[collection].count_documents({})
        return len(json.loads(self._path(collection).read_text(encoding='utf-8')))

    def clear(self):
        if self.use_mongo:
            for c in COLLECTIONS:
                self.db[c].delete_many({})
        else:
            for c in COLLECTIONS:
                self._path(c).write_text('[]', encoding='utf-8')

    def status(self):
        return {'mode': 'mongodb' if self.use_mongo else 'local-json', 'database': MONGODB_DB if self.use_mongo else 'runtime JSON fallback'}

db = Database()
