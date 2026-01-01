import React, { useState, useEffect, useRef } from 'react';

interface MonitorEvent {
  timestamp: number;
  pid: number;
  ppid: number;
  comm: string;
  type: 'EXEC' | 'EXIT' | 'OOM';
  exit_code: number;
  target_pid: number;
}

const App: React.FC = () => {
  const [events, setEvents] = useState<MonitorEvent[]>([]);
  const [status, setStatus] = useState<'Connecting' | 'Connected' | 'Disconnected'>('Connecting');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8080/ws`);

    ws.onopen = () => setStatus('Connected');
    ws.onclose = () => setStatus('Disconnected');
    ws.onmessage = (event) => {
      try {
        const data: MonitorEvent = JSON.parse(event.data);
        setEvents((prev) => [data, ...prev].slice(0, 100));
      } catch (err) {
        console.error("Failed to parse event:", err);
      }
    };

    return () => ws.close();
  }, []);

  const getEventStyle = (type: string) => {
    switch (type) {
      case 'OOM': return { color: '#ff4d4d', fontWeight: 'bold' as const, borderLeft: '4px solid #ff4d4d' };
      case 'EXEC': return { color: '#4dff4d', borderLeft: '4px solid #4dff4d' };
      case 'EXIT': return { color: '#aaaaaa', borderLeft: '4px solid #888' };
      default: return {};
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #444', paddingBottom: '10px' }}>
        <h1>C/C++ Process Monitor</h1>
        <div style={{ color: status === 'Connected' ? '#4dff4d' : '#ff4d4d' }}>
          ● {status}
        </div>
      </header>

      <div style={{ marginTop: '20px' }}>
        {events.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#888' }}>Waiting for events...</p>
        ) : (
          <div ref={scrollRef} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {events.map((ev, i) => (
              <div key={i} style={{ 
                background: '#2a2a2a', 
                padding: '10px', 
                borderRadius: '4px',
                ...getEventStyle(ev.type)
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                  <span>[{ev.type}] <strong>{ev.comm}</strong> (PID: {ev.pid})</span>
                  <span style={{ color: '#888' }}>{new Date(ev.timestamp / 1000000).toLocaleTimeString()}</span>
                </div>
                <div style={{ fontSize: '0.8em', marginTop: '4px', color: '#ccc' }}>
                  {ev.type === 'OOM' ? (
                    <span style={{ color: '#ff4d4d' }}>OOM KILLER victim! Target PID: {ev.target_pid}</span>
                  ) : ev.type === 'EXIT' ? (
                    <span>Exited with code: {ev.exit_code} (Parent PID: {ev.ppid})</span>
                  ) : (
                    <span>Started (Parent PID: {ev.ppid})</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
