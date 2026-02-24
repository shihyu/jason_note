import type { Event } from '../types/event';

type EventCallback = (event: Event) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private callbacks: Set<EventCallback> = new Set();
  private isIntentionallyClosed = false;

  constructor(url: string) {
    this.url = url;
  }

  connect() {
    this.isIntentionallyClosed = false;
    
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          // Handle multiple events in one message (separated by newlines)
          const messages = event.data.split('\n').filter((msg: string) => msg.trim());
          for (const message of messages) {
            const parsed = JSON.parse(message);

            // Check if this is a batch message
            if (parsed.type === 'batch' && Array.isArray(parsed.events)) {
              // Handle batch of events
              for (const evt of parsed.events) {
                this.callbacks.forEach(callback => callback(evt));
              }
            } else {
              // Handle single event
              this.callbacks.forEach(callback => callback(parsed));
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.ws = null;
        
        if (!this.isIntentionallyClosed) {
          this.reconnect();
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.reconnect();
    }
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  disconnect() {
    this.isIntentionallyClosed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onEvent(callback: EventCallback) {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

