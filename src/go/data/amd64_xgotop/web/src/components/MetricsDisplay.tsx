import { useEffect, useState } from 'react';

interface BackendMetrics {
  rps: number;
  pps: number;
  ewp: number;
  lat: number;
  prc: number;
  bfl: number;
  qwl: number;
}

interface Metric {
  value: number | string;
  label: string;
  fullName: string;
  unit: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export function MetricsDisplay() {
  const [metrics, setMetrics] = useState<Record<string, Metric>>({
    rps: { value: 0, label: 'RPS', fullName: 'Read Events Per Second', unit: '' },
    pps: { value: 0, label: 'PPS', fullName: 'Processed Events Per Second', unit: '' },
    ewp: { value: 0, label: 'EWP', fullName: 'Events Waiting Processing', unit: '' },
    lat: { value: 0, label: 'LAT', fullName: 'Average Latency', unit: '' },
    prc: { value: 0, label: 'PRC', fullName: 'Processing Time', unit: '' },
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${API_URL}/api/metrics`);
        if (!response.ok) return;

        const data: BackendMetrics = await response.json();

        setMetrics({
          rps: {
            value: data.rps > 0 ? `${data.rps.toFixed(0)}/s` : '0/s',
            label: 'RPS',
            fullName: 'Read Events Per Second',
            unit: ''
          },
          pps: {
            value: data.pps > 0 ? `${data.pps.toFixed(0)}/s` : '0/s',
            label: 'PPS',
            fullName: 'Processed Events Per Second',
            unit: ''
          },
          ewp: {
            value: data.ewp,
            label: 'EWP',
            fullName: 'Events Waiting Processing',
            unit: ''
          },
          lat: {
            value: data.lat > 0 ?
              data.lat < 1000 ? `${data.lat.toFixed(0)}ns` :
              data.lat < 1000000 ? `${(data.lat / 1000).toFixed(1)}μs` :
              `${(data.lat / 1000000).toFixed(2)}ms` : 'N/A',
            label: 'LAT',
            fullName: 'Average Latency',
            unit: ''
          },
          prc: {
            value: data.prc > 0 ?
              data.prc < 1000 ? `${data.prc.toFixed(0)}ns` :
              data.prc < 1000000 ? `${(data.prc / 1000).toFixed(1)}μs` :
              `${(data.prc / 1000000).toFixed(2)}ms` : 'N/A',
            label: 'PRC',
            fullName: 'Average Processing Time',
            unit: ''
          },
        });
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    // Fetch immediately and then every second
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-6 font-mono text-sm">
      {Object.values(metrics).map((metric) => (
        <div
          key={metric.label}
          className="flex items-center gap-2"
          title={metric.fullName}
        >
          <span className="font-bold uppercase">{metric.label}:</span>
          <span className="text-green-600 font-bold">
            {metric.value}{metric.unit}
          </span>
        </div>
      ))}
    </div>
  );
}