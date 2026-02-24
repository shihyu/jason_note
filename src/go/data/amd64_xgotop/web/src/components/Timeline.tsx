import { useEffect, useRef, useState } from 'react';
import { useEventStore } from '../store/eventStore';
import { useConfigStore } from '../store/configStore';
import { GoroutineRow } from './GoroutineRow';
import { TimelineRuler } from './TimelineRuler';
import { StateLegend } from './StateLegend';
import { GoroutineDetailModal } from './GoroutineDetailModal';
import type { GoroutineState } from '../types/event';

export function Timeline() {
  const { goroutines, viewport, setViewport, cleanupExitedGoroutines } = useEventStore();
  const { nanoseconds_per_pixel, exitedGoroutineCleanupTime } = useConfigStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const lastTimeEndRef = useRef(viewport.timeEnd);
  const [followTimeline, setFollowTimeline] = useState(true);
  const [preserveExitedGoroutines, setPreserveExitedGoroutines] = useState(true); // Changed to true by default
  const [selectedGoroutine, setSelectedGoroutine] = useState<GoroutineState | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Handle scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      setViewport({ scrollX: container.scrollLeft });

      // If user manually scrolls, disable follow timeline
      if (followTimeline) {
        const scrollRight = container.scrollLeft + container.clientWidth;
        const totalWidth = container.scrollWidth;
        const nearEnd = scrollRight >= totalWidth - 100; // Within 100px of end

        if (!nearEnd && container.scrollLeft > 0) {
          setFollowTimeline(false);
        }
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [setViewport, followTimeline]);

  // Auto-scroll when new events extend the timeline
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Only auto-scroll if timeEnd has increased and follow timeline is enabled
    if (viewport.timeEnd > lastTimeEndRef.current && followTimeline) {
      // Calculate the new scroll position to show the latest events
      const timeRange = viewport.timeEnd - viewport.timeStart;
      const viewportWidthNs = (container.clientWidth * nanoseconds_per_pixel) / viewport.zoom;

      // Scroll to show the last portion of the timeline
      const targetScrollNs = Math.max(0, timeRange - viewportWidthNs);
      const targetScrollPx = (targetScrollNs / nanoseconds_per_pixel) * viewport.zoom;

      // Smooth scroll to the new position
      container.scrollTo({
        left: targetScrollPx,
        behavior: 'smooth'
      });
    }

    lastTimeEndRef.current = viewport.timeEnd;
  }, [viewport.timeEnd, viewport.timeStart, viewport.zoom, nanoseconds_per_pixel, followTimeline]);

  // Handle zoom with mouse wheel
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        setViewport({ zoom: viewport.zoom * delta });
      }
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => container.removeEventListener('wheel', handleWheel);
  }, [viewport.zoom, setViewport]);
  
  // Cleanup exited goroutines periodically if preserve is disabled
  useEffect(() => {
    if (!preserveExitedGoroutines) {
      const interval = setInterval(() => {
        cleanupExitedGoroutines(exitedGoroutineCleanupTime);
      }, 1000); // Check every second

      return () => clearInterval(interval);
    }
  }, [preserveExitedGoroutines, exitedGoroutineCleanupTime, cleanupExitedGoroutines]);

  // Convert Map to array and sort by goroutine ID
  const goroutineArray = Array.from(goroutines.values()).sort((a, b) => a.id - b.id);

  // Calculate total timeline width
  // For 60 seconds at 1x zoom, we want it to fit in roughly the screen width
  const timelineWidth = Math.max(
    window.innerWidth,
    ((viewport.timeEnd - viewport.timeStart) / nanoseconds_per_pixel) * viewport.zoom
  );

  // Handle goroutine click
  const handleGoroutineClick = (goroutine: GoroutineState) => {
    setSelectedGoroutine(goroutine);
    setIsModalOpen(true);
  };
  
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Timeline controls and legend */}
      <div className="px-4 py-2 border-b-2 border-black flex items-start gap-4">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="follow-timeline"
              checked={followTimeline}
              onChange={(e) => setFollowTimeline(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="follow-timeline" className="text-sm font-bold uppercase cursor-pointer">
              Follow Timeline
            </label>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="preserve-exited"
              checked={preserveExitedGoroutines}
              onChange={(e) => setPreserveExitedGoroutines(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="preserve-exited" className="text-sm font-bold uppercase cursor-pointer">
              Preserve Exited Goroutines
            </label>
          </div>
        </div>
        <div className="flex-1">
          <StateLegend />
        </div>
      </div>

      <TimelineRuler />

      <div
        ref={containerRef}
        className="flex-1 overflow-auto"
      >
        <div style={{ width: `${timelineWidth}px`, minHeight: '100%' }}>
          {goroutineArray.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="brutalist-box p-8">
                <p className="font-bold text-lg uppercase text-center">
                  No goroutines yet
                </p>
                <p className="text-sm text-center mt-2">
                  Waiting for events...
                </p>
              </div>
            </div>
          ) : (
            goroutineArray.map((goroutine) => (
              <GoroutineRow
                key={goroutine.id}
                goroutine={goroutine}
                onClick={() => handleGoroutineClick(goroutine)}
              />
            ))
          )}
        </div>
      </div>

      {/* Goroutine Detail Modal */}
      <GoroutineDetailModal
        goroutine={selectedGoroutine}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}


