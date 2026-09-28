import { useEffect, useState } from 'react';
import { generateData, getSampleData } from '../services/api';
import { Panel, LoadingSpinner, ErrorState } from '../components/ui';

export default function Data() {
  const [data, setData] = useState(null);
  const [sample, setSample] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const load = () => {
    getSampleData()
      .then((r) => setSample(r.data))
      .catch((err) => {
        console.error("Failed to load sample data:", err);
        setError(true);
      });
  };

  useEffect(() => {
    load();
  }, []);

  const regen = () => {
    setLoading(true);
    generateData()
      .then(() => load())
      .catch((err) => {
        console.error("Failed to generate data:", err);
        setError(true);
      })
      .finally(() => setLoading(false));
  };

  const files = Object.entries(sample);
  
  const download = () =>
    window.open(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/data/download/training_dataset.csv`,
      '_blank'
    );

  const counts = {
    normal: sample.normal_behavior?.length || 0,
    known: sample.known_attacks?.length || 0,
    unknown: sample.unknown_behavior?.length || 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <p className="eyebrow">Synthetic behavioral corpus</p>
        <h1 className="page-title">Synthetic Data</h1>
        <p className="page-subtitle">
          Generated locally for defensive ML training and safe demonstrations.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Panel className="p-5">
          <p className="eyebrow">Normal records</p>
          <p className="mt-2 text-3xl font-semibold">10,000</p>
        </Panel>
        <Panel className="p-5">
          <p className="eyebrow">Known attack records</p>
          <p className="mt-2 text-3xl font-semibold">3,000</p>
        </Panel>
        <Panel className="p-5">
          <p className="eyebrow">Unknown anomaly records</p>
          <p className="mt-2 text-3xl font-semibold">1,000</p>
        </Panel>
      </div>

      <div className="flex flex-wrap gap-3">
        <button disabled={loading} onClick={regen} className="btn-primary">
          {loading ? 'Generating...' : 'Generate Dataset'}
        </button>
        <button onClick={download} className="btn-secondary">
          Download Dataset
        </button>
        <button onClick={regen} className="btn-secondary">
          Regenerate
        </button>
        <button onClick={load} className="btn-secondary">
          Refresh Sample
        </button>
      </div>

      {error ? (
        <ErrorState message="Backend unavailable. Start FastAPI server." />
      ) : (
        <Panel>
          <div className="border-b border-white/5 p-5">
            <p className="section-title">Sample records</p>
            <p className="section-sub">
              Showing up to 20 rows from each generated CSV.
            </p>
          </div>
          {files.length ? (
            <div className="overflow-auto">
              <table className="min-w-[1100px] text-xs">
                <thead className="text-left text-[10px] uppercase tracking-wider text-slate-500">
                  <tr>
                    {Object.keys(files[0][1][0] || {}).map((k) => (
                      <th key={k} className="px-3 py-3">
                        {k}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(files[0][1] || []).map((row, i) => (
                    <tr key={i} className="border-t border-white/[.03]">
                      {Object.values(row).map((v, j) => (
                        <td
                          key={j}
                          className="max-w-40 truncate px-3 py-2 text-slate-400"
                        >
                          {String(v)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <LoadingSpinner text="Generate the dataset to populate samples." />
          )}
        </Panel>
      )}
    </div>
  );
}