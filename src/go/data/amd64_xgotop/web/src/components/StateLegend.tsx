import { useConfigStore } from '../store/configStore';

const STATE_NAMES: Record<string, string> = {
  '0': 'Idle',
  '1': 'Runnable',
  '2': 'Running',
  '3': 'Syscall',
  '4': 'Waiting',
  '5': 'Moribund',
  '6': 'Dead',
  '7': 'Enqueue',
  '8': 'CopyStack',
  '9': 'Preempted',
};

export function StateLegend() {
  const { state_colors } = useConfigStore();

  return (
    <div className="brutalist-box p-3 mb-4">
      <h3 className="text-sm font-bold uppercase mb-2">State Colors</h3>
      <div className="flex flex-wrap gap-2">
        {Object.entries(STATE_NAMES).map(([stateId, stateName]) => (
          <div key={stateId} className="flex items-center gap-1">
            <div
              className="w-4 h-4 border-2 border-black"
              style={{ backgroundColor: state_colors[stateId] || '#94a3b8' }}
            />
            <span className="text-xs font-mono">{stateName}</span>
          </div>
        ))}
      </div>
    </div>
  );
}