import { create } from 'zustand';
import type { TimelineConfig } from '../types/event';

export type BoxHeightSize = 'compact' | 'normal' | 'large';

interface BoxHeightConfig {
  states: string;      // Tailwind height class for states row
  allocations: string; // Tailwind height class for allocations row
  newobjects: string;  // Tailwind height class for newobjects row
  stateBox: string;    // Tailwind height class for state box
  allocBox: string;    // Tailwind height class for alloc box
}

const BOX_HEIGHT_CONFIGS: Record<BoxHeightSize, BoxHeightConfig> = {
  compact: {
    states: 'h-6',       // 24px
    allocations: 'h-5',  // 20px
    newobjects: 'h-4',   // 16px
    stateBox: 'h-5',     // 20px
    allocBox: 'h-4',     // 16px
  },
  normal: {
    states: 'h-10',      // 40px (current)
    allocations: 'h-8',  // 32px (current)
    newobjects: 'h-6',   // 24px (current)
    stateBox: 'h-8',     // 32px (current)
    allocBox: 'h-6',     // 24px (current)
  },
  large: {
    states: 'h-14',      // 56px
    allocations: 'h-12', // 48px
    newobjects: 'h-10',  // 40px
    stateBox: 'h-12',    // 48px
    allocBox: 'h-10',    // 40px
  },
};

interface ConfigStoreState extends TimelineConfig {
  boxHeightSize: BoxHeightSize;
  boxHeights: BoxHeightConfig;
  exitedGoroutineCleanupTime: number; // in seconds
  setNanosecondsPerPixel: (value: number) => void;
  setStateColor: (state: string, color: string) => void;
  setTypeColor: (type: string, color: string) => void;
  setBoxHeightSize: (size: BoxHeightSize) => void;
  setExitedGoroutineCleanupTime: (seconds: number) => void;
  updateConfig: (config: Partial<TimelineConfig>) => void;
}

const DEFAULT_STATE_COLORS: Record<string, string> = {
  '0': '#22c55e', // Gidle -> green
  '1': '#3b82f6', // Grunnable -> blue
  '2': '#eab308', // Grunning -> yellow
  '3': '#f97316', // Gsyscall -> orange
  '4': '#ef4444', // Gwaiting -> red
  '5': '#a855f7', // Gmoribund_unused -> purple
  '6': '#64748b', // Gdead -> gray
  '7': '#ec4899', // Genqueue_unused -> pink
  '8': '#14b8a6', // Gcopystack -> teal
  '9': '#f59e0b', // Gpreempted -> amber
};

const DEFAULT_TYPE_COLORS: Record<string, string> = {
  makeslice: '#3b82f6',
  makemap: '#8b5cf6',
  newobject: '#06b6d4',
};

export const useConfigStore = create<ConfigStoreState>((set) => ({
  nanoseconds_per_pixel: 60000000, // 60ms per pixel by default (60 seconds = 1000 pixels)
  state_colors: DEFAULT_STATE_COLORS,
  type_colors: DEFAULT_TYPE_COLORS,
  boxHeightSize: 'compact' as BoxHeightSize,
  boxHeights: BOX_HEIGHT_CONFIGS.compact,
  exitedGoroutineCleanupTime: 5, // 5 seconds default

  setNanosecondsPerPixel: (value) => {
    set({ nanoseconds_per_pixel: value });
  },

  setStateColor: (state, color) => {
    set((prev) => ({
      state_colors: { ...prev.state_colors, [state]: color },
    }));
  },

  setTypeColor: (type, color) => {
    set((prev) => ({
      type_colors: { ...prev.type_colors, [type]: color },
    }));
  },

  setBoxHeightSize: (size) => {
    set({
      boxHeightSize: size,
      boxHeights: BOX_HEIGHT_CONFIGS[size],
    });
  },

  setExitedGoroutineCleanupTime: (seconds) => {
    set({ exitedGoroutineCleanupTime: seconds });
  },

  updateConfig: (config) => {
    set(config);
  },
}));

