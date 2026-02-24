import type { Event, Session, TimelineConfig } from '../types/event';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

export class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getSessions(): Promise<Session[]> {
    const response = await fetch(`${this.baseUrl}/sessions`);
    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.statusText}`);
    }
    return response.json();
  }

  async getSession(id: string): Promise<Session> {
    const response = await fetch(`${this.baseUrl}/sessions/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch session: ${response.statusText}`);
    }
    return response.json();
  }

  async getEvents(
    sessionId: string,
    filters?: {
      goroutine?: number;
      event_type?: number;
      start_time?: number;
      end_time?: number;
      limit?: number;
      offset?: number;
    }
  ): Promise<Event[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }

    const url = `${this.baseUrl}/sessions/${sessionId}/events${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.statusText}`);
    }
    return response.json();
  }

  async getGoroutines(sessionId: string): Promise<number[]> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/goroutines`);
    if (!response.ok) {
      throw new Error(`Failed to fetch goroutines: ${response.statusText}`);
    }
    return response.json();
  }

  async getConfig(): Promise<TimelineConfig> {
    const response = await fetch(`${this.baseUrl}/config`);
    if (!response.ok) {
      throw new Error(`Failed to fetch config: ${response.statusText}`);
    }
    return response.json();
  }

  async updateConfig(config: TimelineConfig): Promise<TimelineConfig> {
    const response = await fetch(`${this.baseUrl}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      throw new Error(`Failed to update config: ${response.statusText}`);
    }
    return response.json();
  }
}

export const apiClient = new APIClient();

