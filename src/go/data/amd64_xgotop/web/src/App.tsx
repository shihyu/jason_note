import { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { Controls } from './components/Controls';
import { Timeline } from './components/Timeline';
import { MemoryView } from './components/MemoryView';
import { Tabs, type TabView } from './components/Tabs';
import { SettingsModal } from './components/SettingsModal';
import { useEventStore } from './store/eventStore';
import { WebSocketClient } from './services/websocket';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws';

function App() {
  const { addEvent, setConnected } = useEventStore();
  const [wsClient] = useState(() => new WebSocketClient(WS_URL));
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState<TabView>('timeline');

  // Setup WebSocket connection
  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.onEvent((event) => {
      addEvent(event);
    });

    // Check connection status periodically
    const interval = setInterval(() => {
      setConnected(wsClient.isConnected());
    }, 1000);

    return () => {
      unsubscribe();
      clearInterval(interval);
      wsClient.disconnect();
      setConnected(false);
    };
  }, [wsClient, addEvent, setConnected]);
  
  return (
    <div className="h-screen flex flex-col bg-background">
      <Header onSettingsClick={() => setShowSettings(true)} />
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
      
      {/* Controls */}
      <div className="p-4">
        <Controls />
      </div>

      {/* Tabs */}
      <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main View */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {activeTab === 'timeline' ? <Timeline /> : <MemoryView />}
      </div>
      
      {/* Footer */}
      <footer className="border-t-4 border-black p-2 bg-secondary text-center text-xs font-mono">
        <p>
          Use <span className="font-bold">Ctrl+Scroll</span> to zoom • <span className="font-bold">Scroll</span> to pan
        </p>
      </footer>
    </div>
  );
}

export default App;
