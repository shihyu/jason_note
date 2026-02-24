import { Modal } from './ui/Modal';
import { useConfigStore } from '../store/configStore';
import type { GoroutineState } from '../types/event';

interface GoroutineDetailModalProps {
  goroutine: GoroutineState | null;
  isOpen: boolean;
  onClose: () => void;
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

export function GoroutineDetailModal({ goroutine, isOpen, onClose }: GoroutineDetailModalProps) {
  const { state_colors } = useConfigStore();

  if (!goroutine) return null;

  // Calculate goroutine lifetime
  const timeRange = goroutine.exitedAt
    ? goroutine.exitedAt - goroutine.createdAt
    : Date.now() - goroutine.createdAt;

  // Format allocation data for table
  const allocations = [
    ...goroutine.allocations.map(alloc => {
      const typeInfo = alloc.type === 'makeslice'
        ? `Slice (len: ${alloc.length}, cap: ${alloc.capacity})`
        : `Map (hint: ${alloc.hint})`;
      return {
        timestamp: (alloc.timestamp / 1000000).toFixed(2),
        type: typeInfo,
        kind: alloc.typeKind,
      };
    }),
    ...goroutine.newobjects.map(obj => ({
      timestamp: (obj.timestamp / 1000000).toFixed(2),
      type: 'NewObject',
      kind: obj.kind,
      size: `${obj.size} bytes`,
    })),
  ].sort((a, b) => parseFloat(a.timestamp) - parseFloat(b.timestamp));

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Goroutine ${goroutine.id} Details`}
      maxWidth="max-w-6xl"
    >
      <div className="space-y-6">
        {/* Goroutine info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-bold uppercase">Parent Goroutine</p>
            <p className="text-lg font-mono">{goroutine.parentId || 'None'}</p>
          </div>
          <div>
            <p className="text-sm font-bold uppercase">Status</p>
            <p className="text-lg font-mono">
              {goroutine.exitedAt ? 'Exited' : 'Active'}
            </p>
          </div>
          <div>
            <p className="text-sm font-bold uppercase">Created At</p>
            <p className="text-lg font-mono">{(goroutine.createdAt / 1000000).toFixed(2)}ms</p>
          </div>
          {goroutine.exitedAt && (
            <div>
              <p className="text-sm font-bold uppercase">Exited At</p>
              <p className="text-lg font-mono">{(goroutine.exitedAt / 1000000).toFixed(2)}ms</p>
            </div>
          )}
        </div>

        {/* State Timeline */}
        <div>
          <h3 className="text-lg font-bold uppercase mb-3">State Timeline</h3>
          <div className="border-4 border-black bg-gray-50" style={{ minHeight: '120px' }}>
            <div className="relative p-4 overflow-x-auto">
              <div className="flex gap-2" style={{ minWidth: 'fit-content' }}>
                {goroutine.states.map((state, idx) => {
                  const nextState = goroutine.states[idx + 1];
                  const duration = nextState
                    ? nextState.timestamp - state.timestamp
                    : (goroutine.exitedAt || state.timestamp + 1000000) - state.timestamp;

                  const stateName = STATE_NAMES[state.newState] || `State ${state.newState}`;
                  const color = state_colors[state.newState.toString()] || '#94a3b8';

                  return (
                    <div
                      key={idx}
                      className="flex-shrink-0 border-3 border-black p-3 flex flex-col justify-between"
                      style={{
                        width: '150px',
                        backgroundColor: color,
                        minHeight: '80px'
                      }}
                    >
                      <div className="text-center">
                        <div className="font-bold text-sm uppercase">
                          {stateName}
                        </div>
                      </div>

                      <div className="text-[10px] font-mono space-y-1 mt-2">
                        <div className="flex justify-between">
                          <span>Start:</span>
                          <span>{(state.timestamp / 1000000).toFixed(2)}ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Duration:</span>
                          <span>{(duration / 1000000).toFixed(2)}ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span>End:</span>
                          <span>{((state.timestamp + duration) / 1000000).toFixed(2)}ms</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Memory allocations table */}
        {allocations.length > 0 && (
          <div>
            <h3 className="text-lg font-bold uppercase mb-3">Memory Allocations</h3>
            <div className="border-4 border-black overflow-x-auto">
              <table className="w-full">
                <thead className="bg-primary text-primary-foreground">
                  <tr>
                    <th className="px-4 py-2 text-left font-bold uppercase">Time (ms)</th>
                    <th className="px-4 py-2 text-left font-bold uppercase">Type</th>
                    <th className="px-4 py-2 text-left font-bold uppercase">Kind</th>
                    <th className="px-4 py-2 text-left font-bold uppercase">Size</th>
                  </tr>
                </thead>
                <tbody>
                  {allocations.map((alloc, idx) => (
                    <tr key={idx} className="border-t-2 border-black">
                      <td className="px-4 py-2 font-mono">{alloc.timestamp}</td>
                      <td className="px-4 py-2">{alloc.type}</td>
                      <td className="px-4 py-2 font-mono">{alloc.kind}</td>
                      <td className="px-4 py-2 font-mono">{alloc.size || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* State statistics */}
        <div>
          <h3 className="text-lg font-bold uppercase mb-3">State Statistics</h3>
          <div className="grid grid-cols-3 gap-4">
            {goroutine.states.length > 0 && (
              <>
                <div className="brutalist-box p-3">
                  <p className="text-sm font-bold uppercase">Total States</p>
                  <p className="text-2xl font-mono">{goroutine.states.length}</p>
                </div>
                <div className="brutalist-box p-3">
                  <p className="text-sm font-bold uppercase">Total Allocations</p>
                  <p className="text-2xl font-mono">{allocations.length}</p>
                </div>
                <div className="brutalist-box p-3">
                  <p className="text-sm font-bold uppercase">Lifetime</p>
                  <p className="text-2xl font-mono">
                    {(timeRange / 1000000).toFixed(2)}ms
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}