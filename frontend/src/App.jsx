import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './layouts/Layout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Monitor from './pages/Monitor';
import Analysis from './pages/Analysis';
import Simulator from './pages/Simulator';
import Analytics from './pages/Analytics';
import History from './pages/History';
import ThreatDetail from './pages/ThreatDetail';
import Models from './pages/Models';
import Data from './pages/Data';
import Architecture from './pages/Architecture';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/monitor" element={<Monitor />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/history" element={<History />} />
          <Route path="/threat/:id" element={<ThreatDetail />} />
          <Route path="/models" element={<Models />} />
          <Route path="/data" element={<Data />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}