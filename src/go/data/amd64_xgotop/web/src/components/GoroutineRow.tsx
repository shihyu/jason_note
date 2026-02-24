import type { GoroutineState } from '../types/event';
import { StateBox } from './StateBox';
import { AllocBox } from './AllocBox';
import { useConfigStore } from '../store/configStore';
import { useEventStore } from '../store/eventStore';

interface GoroutineRowProps {
  goroutine: GoroutineState;
  onClick?: () => void;
}

const KIND_NAMES: Record<number, string> = {
  0: 'Invalid', 1: 'bool', 2: 'int', 3: 'int8', 4: 'int16', 5: 'int32', 6: 'int64',
  7: 'uint', 8: 'uint8', 9: 'uint16', 10: 'uint32', 11: 'uint64', 12: 'uintptr',
  13: 'float32', 14: 'float64', 15: 'complex64', 16: 'complex128',
  17: 'Array', 18: 'Chan', 19: 'Func', 20: 'Interface', 21: 'Map', 22: 'Ptr',
  23: 'Slice', 24: 'String', 25: 'Struct', 26: 'UnsafePtr',
};

// Abbreviated type names for small boxes
const KIND_ABBR: Record<number, string> = {
  0: '?', 1: 'b', 2: 'i', 3: 'i8', 4: 'i16', 5: 'i32', 6: 'i64',
  7: 'u', 8: 'u8', 9: 'u16', 10: 'u32', 11: 'u64', 12: 'uptr',
  13: 'f32', 14: 'f64', 15: 'c64', 16: 'c128',
  17: 'A', 18: 'C', 19: 'F', 20: 'I', 21: 'M', 22: 'P',
  23: 'S', 24: 'str', 25: 'st', 26: 'UP',
};

export function GoroutineRow({ goroutine, onClick }: GoroutineRowProps) {
  const { nanoseconds_per_pixel, boxHeights } = useConfigStore();
  const { viewport } = useEventStore();
  
  return (
    <div className="border-b-3 border-black bg-background">
      {/* Goroutine header */}
      <div className="flex items-center border-b-2 border-black bg-secondary px-3 py-1">
        <span className="font-bold text-sm uppercase tracking-wide">
          Goroutine {goroutine.id}
        </span>
        {goroutine.parentId > 0 && (
          <span className="ml-2 text-xs font-mono">
            (parent: {goroutine.parentId})
          </span>
        )}
        {goroutine.exitedAt && (
          <span className="ml-auto text-xs font-mono text-red-600 font-bold">
            EXITED
          </span>
        )}
      </div>
      
      {/* States row */}
      <div className={`relative ${boxHeights.states} border-b-2 border-black overflow-hidden`}>
        <div className="absolute left-0 top-1 right-0 bottom-1">
          {goroutine.states.map((state, idx) => (
            <StateBox
              key={idx}
              state={state}
              nextState={goroutine.states[idx + 1]}
              onClick={onClick}
            />
          ))}
        </div>
      </div>
      
      {/* Allocations row */}
      <div className={`relative ${boxHeights.allocations} border-b-2 border-black overflow-hidden`}>
        <div className="absolute left-0 top-1 right-0 bottom-1">
          {goroutine.allocations.map((alloc, idx) => (
            <AllocBox
              key={idx}
              alloc={alloc}
              nextAlloc={goroutine.allocations[idx + 1]}
              onClick={onClick}
            />
          ))}
        </div>
      </div>
      
      {/* NewObject sub-row */}
      {goroutine.newobjects.length > 0 && (
        <div className={`relative ${boxHeights.newobjects} border-b-2 border-black bg-gray-50 overflow-hidden`}>
          <div className="absolute left-0 top-0.5 right-0 bottom-0.5">
            {goroutine.newobjects.map((obj, idx) => {
              // Apply zoom to position relative to viewport start
              const left = ((obj.timestamp - viewport.timeStart) / nanoseconds_per_pixel) * viewport.zoom;

              // Calculate width with zoom - use size as a rough indicator
              const width = Math.max((obj.size / 1000) * viewport.zoom, 10);

              const kindName = KIND_NAMES[obj.kind] || `Kind ${obj.kind}`;
              const kindAbbr = KIND_ABBR[obj.kind] || obj.kind.toString();

              // Choose display based on width
              let displayText;
              if (width < 20) {
                displayText = '•';
              } else if (width < 40) {
                displayText = kindAbbr;
              } else if (width < 60) {
                displayText = `${obj.size}`;
              } else {
                displayText = `${obj.size}B ${kindName}`;
              }

              return (
                <div
                  key={idx}
                  className="absolute h-5 border-2 border-black bg-cyan-400 flex items-center justify-center text-[9px] font-mono font-bold overflow-hidden cursor-pointer hover:brightness-110"
                  style={{
                    left: `${left}px`,
                    width: `${width}px`,
                    minWidth: '10px'
                  }}
                  title={`NewObject\nType: ${kindName}\nSize: ${obj.size} bytes\nTimestamp: ${(obj.timestamp / 1000000).toFixed(2)}ms`}
                  onClick={onClick}
                >
                  <span className="truncate px-0.5">{displayText}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}


