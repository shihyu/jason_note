import { useConfigStore } from '../store/configStore';
import { useEventStore } from '../store/eventStore';
import type { AllocationEvent } from '../types/event';

interface AllocBoxProps {
  alloc: AllocationEvent;
  nextAlloc?: AllocationEvent;
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

export function AllocBox({ alloc, nextAlloc, onClick }: AllocBoxProps) {
  const { nanoseconds_per_pixel, type_colors, boxHeights } = useConfigStore();
  const { viewport } = useEventStore();

  // Calculate position relative to viewport start
  const left = ((alloc.timestamp - viewport.timeStart) / nanoseconds_per_pixel) * viewport.zoom;

  // For allocations, use either the next allocation time or a small fixed duration
  // Allocations are instant events, so we give them a small visual width
  const duration = nextAlloc ?
    Math.min(nextAlloc.timestamp - alloc.timestamp, 5000000) : // Cap at 5ms for visibility
    500000; // Default 0.5ms for last allocation

  const width = Math.max((duration / nanoseconds_per_pixel) * viewport.zoom, 10); // Minimum 10px width

  const color = type_colors[alloc.type] || '#06b6d4';
  const kindName = KIND_NAMES[alloc.typeKind] || `Kind ${alloc.typeKind}`;
  const kindAbbr = KIND_ABBR[alloc.typeKind] || alloc.typeKind.toString();

  let label = '';
  let shortLabel = '';
  let info = '';
  let tooltipDetails = '';

  if (alloc.type === 'makeslice') {
    label = `[]${kindName}`;
    shortLabel = `[]${kindAbbr}`;
    info = `len:${alloc.length} cap:${alloc.capacity}`;
    tooltipDetails = `Type: Slice\nElement: ${kindName}\nLength: ${alloc.length}\nCapacity: ${alloc.capacity}`;
  } else if (alloc.type === 'makemap') {
    const elemKind = KIND_NAMES[alloc.typeKind2 || 0] || `Kind ${alloc.typeKind2}`;
    const elemAbbr = KIND_ABBR[alloc.typeKind2 || 0] || (alloc.typeKind2?.toString() || '?');
    label = `map[${kindName}]${elemKind}`;
    shortLabel = `m[${kindAbbr}]${elemAbbr}`;
    info = `hint:${alloc.hint}`;
    tooltipDetails = `Type: Map\nKey: ${kindName}\nValue: ${elemKind}\nHint: ${alloc.hint}`;
  }

  // Choose display based on width
  let displayContent;
  if (width < 20) {
    displayContent = <span className="text-[8px]">{alloc.type === 'makeslice' ? 'S' : 'M'}</span>;
  } else if (width < 40) {
    displayContent = <span className="text-[9px]">{shortLabel}</span>;
  } else if (width < 60) {
    displayContent = <span className="truncate">{label}</span>;
  } else {
    displayContent = (
      <div className="flex flex-col items-center leading-tight">
        <span className="truncate">{label}</span>
        {width > 80 && <span className="text-[8px]">{info}</span>}
      </div>
    );
  }

  return (
    <div
      className={`absolute ${boxHeights.allocBox} border-2 border-black flex items-center justify-center overflow-hidden text-[10px] font-mono font-bold cursor-pointer hover:brightness-110`}
      style={{
        left: `${left}px`,
        width: `${width}px`,
        backgroundColor: color,
      }}
      title={`${tooltipDetails}\nDuration: ${(duration / 1000000).toFixed(2)}ms`}
      onClick={onClick}
    >
      {displayContent}
    </div>
  );
}


