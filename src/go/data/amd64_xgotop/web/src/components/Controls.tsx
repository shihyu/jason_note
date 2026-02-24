import { Button } from './ui/Button';
import { MetricsDisplay } from './MetricsDisplay';
import { useEventStore } from '../store/eventStore';

export function Controls() {
  const { viewport, setViewport, isConnected } = useEventStore();
  
  const handleZoomIn = () => {
    setViewport({ zoom: viewport.zoom * 1.5 });
  };
  
  const handleZoomOut = () => {
    setViewport({ zoom: viewport.zoom / 1.5 });
  };
  
  const handleResetZoom = () => {
    setViewport({ zoom: 1, scrollX: 0 });
  };
  
  return (
    <div className="brutalist-box p-4 mb-4">
      <div className="flex items-center gap-4 flex-wrap">
        {/* Connection status */}
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 border-2 border-black ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="font-bold text-sm uppercase">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        {/* Zoom controls */}
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm uppercase">Zoom:</span>
          <Button onClick={handleZoomOut}>-</Button>
          <span className="font-mono font-bold min-w-[60px] text-center">
            {viewport.zoom.toFixed(2)}x
          </span>
          <Button onClick={handleZoomIn}>+</Button>
          <Button onClick={handleResetZoom} variant="secondary">Reset</Button>
        </div>

        {/* Metrics */}
        <div className="ml-auto">
          <MetricsDisplay />
        </div>
      </div>
    </div>
  );
}


