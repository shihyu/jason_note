import { useConfigStore } from '../store/configStore';
import { useEventStore } from '../store/eventStore';
import type { StateEvent } from '../types/event';

interface StateBoxProps {
  state: StateEvent;
  nextState?: StateEvent;
  onClick?: () => void;
}

const STATE_NAMES: Record<number, string> = {
  0: 'Idle',
  1: 'Runnable',
  2: 'Running',
  3: 'Syscall',
  4: 'Waiting',
  5: 'Moribund',
  6: 'Dead',
  7: 'Enqueue',
  8: 'CopyStack',
  9: 'Preempted',
};

// State abbreviations for small boxes
const STATE_ABBR: Record<number, string> = {
  0: 'I',  // Idle
  1: 'R',  // Runnable
  2: 'RN', // Running
  3: 'S',  // Syscall
  4: 'W',  // Waiting
  5: 'M',  // Moribund
  6: 'D',  // Dead
  7: 'E',  // Enqueue
  8: 'C',  // CopyStack
  9: 'P',  // Preempted
};

export function StateBox({ state, nextState, onClick }: StateBoxProps) {
  const { nanoseconds_per_pixel, state_colors, boxHeights } = useConfigStore();
  const { viewport } = useEventStore();

  // Calculate position relative to viewport start
  const left = ((state.timestamp - viewport.timeStart) / nanoseconds_per_pixel) * viewport.zoom;

  // Special handling for DEAD state - use constant width
  const isDead = state.newState === 6; // G_STATUS_DEAD

  let duration;
  let width;

  if (isDead) {
    // DEAD state gets a constant visual width of 30 pixels (not affected by zoom)
    width = 30;
    duration = (width / viewport.zoom) * nanoseconds_per_pixel; // Back-calculate duration for display
  } else {
    // Normal duration calculation for non-dead states
    duration = state.duration ||
      (nextState ? nextState.timestamp - state.timestamp :
       viewport.timeEnd > state.timestamp ? viewport.timeEnd - state.timestamp : 1000000);

    width = Math.max((duration / nanoseconds_per_pixel) * viewport.zoom, 10); // Minimum 10px width
  }

  const color = state_colors[state.newState.toString()] || '#94a3b8';
  const stateName = STATE_NAMES[state.newState] || `State ${state.newState}`;
  const stateAbbr = STATE_ABBR[state.newState] || state.newState.toString();

  // Choose text based on box width
  let displayText = stateName;
  if (width < 30) {
    displayText = stateAbbr;
  } else if (width < 60) {
    displayText = stateName.slice(0, 4);
  }

  return (
    <div
      className={`absolute ${boxHeights.stateBox} border-3 border-black flex items-center justify-center overflow-hidden group cursor-pointer hover:brightness-110`}
      style={{
        left: `${left}px`,
        width: `${width}px`,
        backgroundColor: color,
      }}
      title={`${stateName}\nDuration: ${(duration / 1000000).toFixed(2)}ms\nFrom: ${STATE_NAMES[state.oldState] || state.oldState}\nTo: ${stateName}`}
      onClick={onClick}
    >
      <span className="text-xs font-bold uppercase truncate px-1">
        {displayText}
      </span>
      {width > 80 && (
        <span className="absolute bottom-0 right-1 text-[10px] font-mono">
          {(duration / 1000000).toFixed(1)}ms
        </span>
      )}
    </div>
  );
}


