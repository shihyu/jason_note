import { useEventStore } from '../store/eventStore';
import { useConfigStore } from '../store/configStore';
import { useMemo, useState } from 'react';
import { GoroutineDetailModal } from './GoroutineDetailModal';
import type { GoroutineState } from '../types/event';

interface GoroutineMemoryInfo {
  id: number;
  totalAllocated: number;
  allocCount: number;
  sliceAllocations: number;
  mapAllocations: number;
  newObjectAllocations: number;
  lastState: number;
  isAlive: boolean;
}

export function MemoryView() {
  const { goroutines } = useEventStore();
  const { state_colors } = useConfigStore();
  const [selectedGoroutine, setSelectedGoroutine] = useState<GoroutineState | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const memoryData = useMemo(() => {
    const data: GoroutineMemoryInfo[] = [];

    goroutines.forEach((goroutine) => {
      let totalAllocated = 0;
      let sliceAllocations = 0;
      let mapAllocations = 0;
      let newObjectAllocations = 0;

      // Calculate slice allocations
      goroutine.allocations.forEach((alloc) => {
        if (alloc.type === 'makeslice') {
          const size = (alloc.capacity || 0) * 8; // Approximate size based on capacity
          sliceAllocations += size;
          totalAllocated += size;
        } else if (alloc.type === 'makemap') {
          const size = (alloc.hint || 1) * 16; // Approximate size based on hint
          mapAllocations += size;
          totalAllocated += size;
        }
      });

      // Calculate newobject allocations
      goroutine.newobjects.forEach((obj) => {
        newObjectAllocations += obj.size;
        totalAllocated += obj.size;
      });

      const lastState = goroutine.states.length > 0
        ? goroutine.states[goroutine.states.length - 1].newState
        : 0;

      data.push({
        id: goroutine.id,
        totalAllocated,
        allocCount: goroutine.allocations.length + goroutine.newobjects.length,
        sliceAllocations,
        mapAllocations,
        newObjectAllocations,
        lastState,
        isAlive: !goroutine.exitedAt,
      });
    });

    // Sort by total allocated memory (descending)
    return data.sort((a, b) => b.totalAllocated - a.totalAllocated);
  }, [goroutines]);

  const maxAllocation = Math.max(...memoryData.map(d => d.totalAllocated), 1);

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
  };

  const handleGoroutineClick = (goroutineId: number) => {
    const goroutine = goroutines.get(goroutineId);
    if (goroutine) {
      setSelectedGoroutine(goroutine);
      setIsModalOpen(true);
    }
  };

  return (
    <div className="flex-1 overflow-auto p-4">
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2">
        {memoryData.map((goroutine) => {
          const bgColor = state_colors[goroutine.lastState.toString()] || '#94a3b8';
          // Calculate opacity based on memory allocation
          const opacityFactor = Math.sqrt(goroutine.totalAllocated / maxAllocation);
          const opacity = 0.2 + 0.6 * opacityFactor; // 20% to 80% opacity

          return (
            <div
              key={goroutine.id}
              className="brutalist-box p-2 flex flex-col justify-between transition-transform hover:translate-x-0.5 hover:translate-y-0.5 cursor-pointer"
              style={{
                width: '120px',
                height: '120px',
                backgroundColor: `${bgColor}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`,
                borderColor: bgColor,
                borderWidth: '3px',
              }}
              onClick={() => handleGoroutineClick(goroutine.id)}
            >
              <div>
                <div className="font-bold text-xs uppercase mb-1">
                  G{goroutine.id}
                  {!goroutine.isAlive && (
                    <span className="ml-1 text-red-600 text-[10px]">(X)</span>
                  )}
                </div>
                <div className="text-[10px] space-y-0.5">
                  <div className="font-mono">
                    {formatBytes(goroutine.totalAllocated)}
                  </div>
                  <div className="font-mono">
                    {goroutine.allocCount} allocs
                  </div>
                </div>
              </div>

              <div className="text-[9px] font-mono space-y-0 mt-1">
                {goroutine.sliceAllocations > 0 && (
                  <div>S: {formatBytes(goroutine.sliceAllocations)}</div>
                )}
                {goroutine.mapAllocations > 0 && (
                  <div>M: {formatBytes(goroutine.mapAllocations)}</div>
                )}
                {goroutine.newObjectAllocations > 0 && (
                  <div>O: {formatBytes(goroutine.newObjectAllocations)}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {memoryData.length === 0 && (
        <div className="flex items-center justify-center h-64">
          <div className="brutalist-box p-8">
            <p className="font-bold text-lg uppercase text-center">
              No memory allocations yet
            </p>
            <p className="text-sm text-center mt-2">
              Waiting for goroutine memory events...
            </p>
          </div>
        </div>
      )}

      {/* Goroutine Detail Modal */}
      <GoroutineDetailModal
        goroutine={selectedGoroutine}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}