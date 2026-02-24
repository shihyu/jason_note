export interface Event {
  timestamp: number;
  event_type: number;
  goroutine: number;
  parent_goroutine: number;
  attributes: [number, number, number, number, number];
}

export interface Session {
  id: string;
  start_time: string;
  end_time?: string;
  pid?: number;
  binary_path: string;
  event_count: number;
}

export interface TimelineConfig {
  nanoseconds_per_pixel: number;
  state_colors: Record<string, string>;
  type_colors: Record<string, string>;
}

export const EventType = {
  CasGStatus: 0,
  MakeSlice: 1,
  MakeMap: 2,
  NewObject: 3,
  NewGoroutine: 4,
  GoExit: 5,
} as const;

export interface GoroutineState {
  id: number;
  parentId: number;
  states: StateEvent[];
  allocations: AllocationEvent[];
  newobjects: NewObjectEvent[];
  createdAt: number;
  exitedAt?: number;
  exitedAtRealTime?: number; // Real time (Date.now()) when goroutine exited
}

export interface StateEvent {
  timestamp: number;
  oldState: number;
  newState: number;
  duration?: number;
}

export interface AllocationEvent {
  timestamp: number;
  type: 'makeslice' | 'makemap';
  typeKind: number;
  typeKind2?: number; // For makemap elem type
  size?: number;
  length?: number;
  capacity?: number;
  hint?: number;
}

export interface NewObjectEvent {
  timestamp: number;
  size: number;
  kind: number;
}

