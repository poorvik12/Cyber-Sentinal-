import { useState } from 'react';
import { analyzeEvent } from '../services/api';
import { Panel, ResultBanner, LoadingSpinner } from '../components/ui';

const fields = [
  ['requests_per_minute', 'Requests/minute', 40],
  ['failed_logins', 'Failed logins', 0],
  ['files_accessed', 'Files accessed', 5],
  ['cpu_usage', 'CPU usage', 25],
  ['memory_usage', 'Memory usage', 45],
  ['unique_ports', 'Unique ports', 4],
  ['unique_ips', 'Unique IPs', 3],
  ['api_requests', 'API requests', 30],
  ['session_duration', 'Session duration', 900],
  ['error_rate', 'Error rate', 0.02],
  ['request_frequency', 'Request frequency', 3],
  ['endpoint_count', 'Endpoint count', 4],
  ['unusual_endpoints', 'Unusual endpoints', 0],
  ['authentication_failures', 'Authentication failures', 0],
  ['privilege_changes', 'Privilege changes', 0],
  ['new_processes', 'New processes', 2],
  ['file_modifications', 'File modifications', 4],
];

export default function Analysis() {
  const initial = Object.fromEntries(fields.map(([k, , v]) => [k, v]));
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    analyzeEvent(form)
      .then((r) => setResult(r.data))
      .catch(() =>
        setError('Backend unavailable. Start FastAPI and try again.')
      )
      .finally(() => setLoading(false));
  };

  return (
    <div className="space-y-6">
      <div>
        <p className="eyebrow">Manual behavioral investigation</p>
        <h1 className="page-title">AI Analysis</h1>
        <p className="page-subtitle">
          Enter behavioral telemetry and send it through both ML detectors and
          the risk engine.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <Panel className="p-5">
          <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
            {fields.map(([k, label]) => (
              <label key={k} className="block">
                <span className="mb-2 block text-xs text-slate-500">
                  {label}
                </span>
                <input
                  className="input"
                  type="number"
                  step="any"
                  min="0"
                  max="1000000"
                  value={form[k]}
                  onChange={(e) =>
                    setForm({ ...form, [k]: Number(e.target.value) })
                  }
                />
              </label>
            ))}
            <button disabled={loading} className="btn-primary sm:col-span-2">
              {loading ? 'Analyzing...' : 'Analyze Behavior'}
            </button>
            {error && (
              <p className="text-sm text-red-300 sm:col-span-2">{error}</p>
            )}
          </form>
        </Panel>

        <Panel className="p-5">
          {loading ? (
            <LoadingSpinner text="Running Random Forest + Isolation Forest..." />
          ) : (
            <AnalysisResult result={result} />
          )}
        </Panel>
      </div>
    </div>
  );
}

function AnalysisResult({ result }) {
  if (!result)
    return (
      <div className="flex min-h-96 items-center justify-center text-center text-sm text-slate-500">
        Submit an event to view the ML decision, anomaly score, risk layers and
        explanation.
      </div>
    );
  return (
    <div className="space-y-5">
      <ResultBanner result={result} />
      <div className="grid grid-cols-2 gap-3">
        <Metric label="Risk score" value={`${Math.round(result.risk_score)}%`} />
        <Metric
          label="Anomaly score"
          value={`${Math.round(result.anomaly_score * 100)}%`}
        />
        <Metric label="RF prediction" value={result.event?.rf_prediction} />
        <Metric
          label="Confidence"
          value={`${Math.round(result.confidence * 100)}%`}
        />
      </div>
      <div>
        <p className="section-title mb-3">Layer analysis</p>
        <div className="grid grid-cols-2 gap-3">
          {[
            ['Network', result.network_score],
            ['User', result.user_score],
            ['System', result.system_score],
            ['Application', result.application_score],
          ].map(([n, v]) => (
            <div
              key={n}
              className="rounded-xl border border-white/5 bg-white/[.02] p-3"
            >
              <p className="text-xs text-slate-500">{n}</p>
              <p className="mt-1 text-xl font-semibold">{Math.round(v)}%</p>
            </div>
          ))}
        </div>
      </div>
      <div>
        <p className="section-title mb-3">Why was this event flagged?</p>
        <ul className="space-y-2">
          {result.explanation.map((x) => (
            <li
              key={x}
              className="rounded-lg border border-white/5 bg-white/[.02] p-3 text-sm leading-5 text-slate-300"
            >
              {x}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[.02] p-3">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </p>
      <p className="mt-1 truncate text-lg font-semibold">{value}</p>
    </div>
  );
}