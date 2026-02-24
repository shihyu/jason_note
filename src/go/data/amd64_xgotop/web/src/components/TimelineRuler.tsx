import { useConfigStore } from '../store/configStore';
import { useEventStore } from '../store/eventStore';

export function TimelineRuler() {
  const { nanoseconds_per_pixel } = useConfigStore();
  const { viewport } = useEventStore();
  
  // Calculate time range in view
  const viewWidthNs = window.innerWidth * nanoseconds_per_pixel / viewport.zoom;
  const startTime = viewport.timeStart + (viewport.scrollX * nanoseconds_per_pixel / viewport.zoom);
  const endTime = startTime + viewWidthNs;
  
  // Calculate tick interval (aim for ~100px between ticks)
  const targetTickSpacing = 100; // pixels
  const tickIntervalNs = targetTickSpacing * nanoseconds_per_pixel / viewport.zoom;
  
  // Round to nice numbers
  const magnitude = Math.pow(10, Math.floor(Math.log10(tickIntervalNs)));
  const normalizedInterval = tickIntervalNs / magnitude;
  let roundedInterval = 1;
  if (normalizedInterval > 5) roundedInterval = 10;
  else if (normalizedInterval > 2) roundedInterval = 5;
  else if (normalizedInterval > 1) roundedInterval = 2;
  const finalTickInterval = roundedInterval * magnitude;
  
  // Generate ticks
  const ticks = [];
  const firstTick = Math.ceil(startTime / finalTickInterval) * finalTickInterval;
  for (let t = firstTick; t <= endTime; t += finalTickInterval) {
    const x = ((t - startTime) / nanoseconds_per_pixel) * viewport.zoom;
    ticks.push({ time: t, x });
  }
  
  const formatTime = (ns: number) => {
    const ms = ns / 1000000;
    const s = ms / 1000;
    if (s >= 1) return `${s.toFixed(2)}s`;
    if (ms >= 1) return `${ms.toFixed(2)}ms`;
    const us = ns / 1000;
    if (us >= 1) return `${us.toFixed(2)}μs`;
    return `${ns.toFixed(0)}ns`;
  };
  
  return (
    <div className="h-12 border-b-4 border-black bg-background sticky top-0 z-50">
      <div className="relative h-full">
        {ticks.map(({ time, x }) => (
          <div
            key={time}
            className="absolute top-0 bottom-0 flex flex-col items-center"
            style={{ left: `${x}px` }}
          >
            <div className="h-3 w-0.5 bg-black" />
            <div className="text-xs font-mono font-bold mt-1">
              {formatTime(time)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


