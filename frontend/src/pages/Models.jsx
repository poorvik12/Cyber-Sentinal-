import { useEffect, useState } from 'react';
import { getModelInfo, retrain } from '../services/api';
import { Panel, LoadingSpinner, ErrorState } from '../components/ui';

export default function Models() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const load = () => {
    getModelInfo()
      .then((r) => setInfo(r.data))
      .catch((err) => {
        console.error("Failed to load model info:", err);
        setError(true);
      });
  };

  useEffect(() => {
    load();
  }, []);

  const run = () => {
    setLoading(true);
    retrain()
      .then((r) =>
        setInfo({
          trained: true,
          random_forest: r.data.random_forest,
          isolation_forest: r.data.isolation_forest,
        })
      )
      .catch((err) => {
        console.error("Failed to retrain models:", err);
        setError(true);
      })
      .finally(() => setLoading(false));
  };

  if (error && !info) {
    return (
      <ErrorState
        message="Backend unavailable. Start FastAPI server."
        onRetry={() => {
          setError(false);
          load();
        }}
      />
    );
  }

  if (!info) return <LoadingSpinner />;

  const rf = info.random_forest;
  const iso = info.isolation_forest;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Model operations</p>
          <h1 className="page-title">ML Models</h1>
          <p className="page-subtitle">
            These metrics and status values come from the actual training artifacts.
          </p>
        </div>
        <button disabled={loading} onClick={run} className="btn-primary">
          {loading ? 'Retraining...' : 'Retrain Models'}
        </button>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ModelCard
          title="Random Forest"
          status={rf ? 'TRAINED' : 'NOT TRAINED'}
        >
          <Info label="Model type" value="Supervised Random Forest classifier" />
          <Info label="Training samples" value={rf?.training_samples} />
          <Info label="Features" value={rf?.features?.length} />
          <Info label="Accuracy" value={rf ? `${rf.accuracy * 100}%` : '—'} />
          <Info label="Precision" value={rf ? `${rf.precision * 100}%` : '—'} />
          <Info label="Recall" value={rf ? `${rf.recall * 100}%` : '—'} />
          <Info label="F1 Score" value={rf ? `${rf.f1 * 100}%` : '—'} />
          <Info label="Classes" value={rf?.classes?.join(', ') || '—'} />
        </ModelCard>

        <ModelCard
          title="Isolation Forest"
          status={iso ? 'TRAINED' : 'NOT TRAINED'}
        >
          <Info label="Method" value={iso?.method} />
          <Info label="Training samples" value={iso?.training_samples} />
          <Info label="Features" value={iso?.features?.length} />
          <Info label="Contamination" value={iso?.contamination} />
          <Info
            label="Purpose"
            value="Detect deviation from learned normal behavior"
          />
        </ModelCard>
      </div>
    </div>
  );
}

function ModelCard({ title, status, children }) {
  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span
          className={`rounded-full px-3 py-1 text-[10px] font-bold ${
            status === 'TRAINED'
              ? 'bg-emerald-400/10 text-emerald-300'
              : 'bg-red-400/10 text-red-300'
          }`}
        >
          {status}
        </span>
      </div>
      <div className="mt-5 grid gap-2">{children}</div>
    </Panel>
  );
}

function Info({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-white/[.03] py-2 text-xs">
      <span className="text-slate-500">{label}</span>
      <span className="max-w-[65%] text-right text-slate-300">
        {value ?? '—'}
      </span>
    </div>
  );
}