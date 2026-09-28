from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import FRONTEND_ORIGIN
from backend.api.routes import router

app=FastAPI(title='AI-Driven Multi-Layer Cybersecurity System',version='1.0.0',description='Defensive synthetic behavioral analytics platform')
app.add_middleware(CORSMiddleware,allow_origins=[FRONTEND_ORIGIN,'http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router)

@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    return JSONResponse(status_code=500,content={'detail':'The server could not complete the request. Check the backend logs for diagnostic details.'})
