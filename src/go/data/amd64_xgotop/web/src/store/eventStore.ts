import { create } from 'zustand';
import type { Event, GoroutineState } from '../types/event';

interface ViewportState {
  scrollX: number;
  zoom: number;
  timeStart: number;
  timeEnd: number;
}

interface EventStoreState {
  events: Event[];
  goroutines: Map<number, GoroutineState>;
  viewport: ViewportState;
  isConnected: boolean;
  baseTimestamp: number | null; // First event timestamp for normalization

  addEvent: (event: Event) => void;
  addEvents: (events: Event[]) => void;
  clearEvents: () => void;
  setConnected: (connected: boolean) => void;
  setViewport: (viewport: Partial<ViewportState>) => void;
  getGoroutine: (id: number) => GoroutineState | undefined;
  cleanupExitedGoroutines: (maxAge: number) => void; // maxAge in seconds
}

function processEvent(goroutines: Map<number, GoroutineState>, event: Event, baseTimestamp: number): Map<number, GoroutineState> {
  const newMap = new Map(goroutines);

  // Normalize the timestamp relative to the first event
  const normalizedEvent = {
    ...event,
    timestamp: event.timestamp - baseTimestamp
  };

  switch (normalizedEvent.event_type) {
    case 0: { // CasGStatus
      const goroutineId = normalizedEvent.attributes[2];
      const oldState = normalizedEvent.attributes[0];
      const newState = normalizedEvent.attributes[1];
      
      let goroutine = newMap.get(goroutineId);
      if (!goroutine) {
        goroutine = {
          id: goroutineId,
          parentId: normalizedEvent.parent_goroutine,
          states: [],
          allocations: [],
          newobjects: [],
          createdAt: normalizedEvent.timestamp,
        };
        newMap.set(goroutineId, goroutine);
      }
      
      // Calculate duration of previous state
      if (goroutine.states.length > 0) {
        const prevState = goroutine.states[goroutine.states.length - 1];
        prevState.duration = normalizedEvent.timestamp - prevState.timestamp;
      }
      
      goroutine.states.push({
        timestamp: normalizedEvent.timestamp,
        oldState,
        newState,
      });
      
      // Check if goroutine is dead
      if (newState === 6) { // G_STATUS_DEAD
        goroutine.exitedAt = normalizedEvent.timestamp;
        goroutine.exitedAtRealTime = Date.now(); // Track real time when goroutine died
      }
      break;
    }
    
    case 1: { // MakeSlice
      const goroutineId = normalizedEvent.goroutine;
      let goroutine = newMap.get(goroutineId);
      if (!goroutine) {
        goroutine = {
          id: goroutineId,
          parentId: normalizedEvent.parent_goroutine,
          states: [],
          allocations: [],
          newobjects: [],
          createdAt: normalizedEvent.timestamp,
        };
        newMap.set(goroutineId, goroutine);
      }

      goroutine.allocations.push({
        timestamp: normalizedEvent.timestamp,
        type: 'makeslice',
        typeKind: normalizedEvent.attributes[1],
        length: normalizedEvent.attributes[2],
        capacity: normalizedEvent.attributes[3],
      });
      break;
    }
    
    case 2: { // MakeMap
      const goroutineId = normalizedEvent.goroutine;
      let goroutine = newMap.get(goroutineId);
      if (!goroutine) {
        goroutine = {
          id: goroutineId,
          parentId: normalizedEvent.parent_goroutine,
          states: [],
          allocations: [],
          newobjects: [],
          createdAt: normalizedEvent.timestamp,
        };
        newMap.set(goroutineId, goroutine);
      }

      goroutine.allocations.push({
        timestamp: normalizedEvent.timestamp,
        type: 'makemap',
        typeKind: normalizedEvent.attributes[1], // key kind
        typeKind2: normalizedEvent.attributes[2], // elem kind
        hint: normalizedEvent.attributes[3],
      });
      break;
    }
    
    case 3: { // NewObject
      const goroutineId = normalizedEvent.goroutine;
      let goroutine = newMap.get(goroutineId);
      if (!goroutine) {
        goroutine = {
          id: goroutineId,
          parentId: normalizedEvent.parent_goroutine,
          states: [],
          allocations: [],
          newobjects: [],
          createdAt: normalizedEvent.timestamp,
        };
        newMap.set(goroutineId, goroutine);
      }
      goroutine.newobjects.push({
        timestamp: normalizedEvent.timestamp,
        size: normalizedEvent.attributes[0],
        kind: normalizedEvent.attributes[1],
      });
      break;
    }
    
    case 4: { // NewGoroutine
      const parentId = normalizedEvent.attributes[0];
      const newId = normalizedEvent.attributes[1];
      
      let goroutine = newMap.get(newId);
      if (!goroutine) {
        goroutine = {
          id: newId,
          parentId: parentId,
          states: [],
          allocations: [],
          newobjects: [],
          createdAt: normalizedEvent.timestamp,
        };
        newMap.set(newId, goroutine);
      }
      break;
    }
    
    case 5: { // GoExit
      const goroutineId = normalizedEvent.attributes[0];
      const goroutine = newMap.get(goroutineId);
      if (goroutine) {
        goroutine.exitedAt = normalizedEvent.timestamp;
        goroutine.exitedAtRealTime = Date.now(); // Track real time when goroutine died
      }
      break;
    }
  }
  
  return newMap;
}

export const useEventStore = create<EventStoreState>((set, get) => ({
  events: [],
  goroutines: new Map(),
  viewport: {
    scrollX: 0,
    zoom: 1,
    timeStart: 0,
    timeEnd: 60000000000, // 60 seconds in nanoseconds
  },
  isConnected: false,
  baseTimestamp: null,
  
  addEvent: (event) => {
    set((state) => {
      // Set base timestamp if this is the first event
      const baseTimestamp = state.baseTimestamp ?? event.timestamp;

      const events = [...state.events, event];
      const goroutines = processEvent(state.goroutines, event, baseTimestamp);

      // Update time bounds with normalized timestamps
      const normalizedTimestamp = event.timestamp - baseTimestamp;
      const timeEnd = Math.max(state.viewport.timeEnd, normalizedTimestamp);
      const timeStart = state.viewport.timeStart === 0 ? 0 : state.viewport.timeStart;

      return {
        events,
        goroutines,
        baseTimestamp,
        viewport: {
          ...state.viewport,
          timeStart,
          timeEnd,
        },
      };
    });
  },
  
  addEvents: (newEvents) => {
    set((state) => {
      if (newEvents.length === 0) return state;

      // Set base timestamp if this is the first event
      const baseTimestamp = state.baseTimestamp ?? newEvents[0].timestamp;

      let goroutines = state.goroutines;
      for (const event of newEvents) {
        goroutines = processEvent(goroutines, event, baseTimestamp);
      }

      const events = [...state.events, ...newEvents];

      // Update time bounds with normalized timestamps
      const normalizedTimestamps = newEvents.map(e => e.timestamp - baseTimestamp);
      const timeEnd = Math.max(state.viewport.timeEnd, ...normalizedTimestamps);
      const timeStart = state.viewport.timeStart === 0 ? 0 : state.viewport.timeStart;

      return {
        events,
        goroutines,
        baseTimestamp,
        viewport: {
          ...state.viewport,
          timeStart,
          timeEnd,
        },
      };
    });
  },
  
  clearEvents: () => {
    set({
      events: [],
      goroutines: new Map(),
      baseTimestamp: null,
      viewport: {
        scrollX: 0,
        zoom: 1,
        timeStart: 0,
        timeEnd: 0,
      },
    });
  },
  
  setConnected: (connected) => {
    set({ isConnected: connected });
  },
  
  setViewport: (viewport) => {
    set((state) => ({
      viewport: { ...state.viewport, ...viewport },
    }));
  },
  
  getGoroutine: (id) => {
    return get().goroutines.get(id);
  },

  cleanupExitedGoroutines: (maxAge) => {
    set((state) => {
      const newGoroutines = new Map(state.goroutines);
      const currentTimeMs = Date.now();

      // Remove goroutines that have been exited for longer than maxAge
      newGoroutines.forEach((goroutine, id) => {
        if (goroutine.exitedAt && goroutine.exitedAtRealTime) {
          const timeSinceExitMs = currentTimeMs - goroutine.exitedAtRealTime;
          const timeSinceExitSec = timeSinceExitMs / 1000;
          if (timeSinceExitSec > maxAge) {
            newGoroutines.delete(id);
          }
        }
      });

      return { ...state, goroutines: newGoroutines };
    });
  },
}));

