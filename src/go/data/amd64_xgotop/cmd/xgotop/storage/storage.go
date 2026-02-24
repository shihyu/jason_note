package storage

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"
)

type EventType uint64

const (
	EventTypeCasGStatus   EventType = 0
	EventTypeMakeSlice    EventType = 1
	EventTypeMakeMap      EventType = 2
	EventTypeNewObject    EventType = 3
	EventTypeNewGoroutine EventType = 4
	EventTypeGoExit       EventType = 5
)

type Event struct {
	Timestamp       uint64    `json:"timestamp"`
	EventType       EventType `json:"event_type"`
	Goroutine       uint32    `json:"goroutine"`
	ParentGoroutine uint32    `json:"parent_goroutine"`
	Attributes      [5]uint64 `json:"attributes"`
}

type Session struct {
	ID         string     `json:"id"`
	StartTime  time.Time  `json:"start_time"`
	EndTime    *time.Time `json:"end_time,omitempty"`
	PID        int        `json:"pid,omitempty"`
	BinaryPath string     `json:"binary_path"`
	EventCount int64      `json:"event_count"`
}

type EventFilter struct {
	Goroutine *uint32
	EventType *EventType
	StartTime *uint64
	EndTime   *uint64
	Limit     int
	Offset    int
}

type EventStore interface {
	WriteEvent(event *Event) error
	WriteBatch(events []*Event) error
	ReadEvents(ctx context.Context, filter *EventFilter) ([]*Event, error)
	GetGoroutines(ctx context.Context) ([]uint32, error)
	Close() error
	GetSession() *Session
	UpdateSession(session *Session) error
}

type SessionStore interface {
	ListSessions(ctx context.Context) ([]*Session, error)
	GetSession(ctx context.Context, id string) (*Session, error)
	OpenSession(ctx context.Context, id string) (EventStore, error)
	CreateSession(ctx context.Context, session *Session, format string) (EventStore, error)
	DeleteSession(ctx context.Context, id string) error
	io.Closer
}

func saveSessionMetadata(sessionDir string, session *Session) error {
	metadataPath := filepath.Join(sessionDir, "metadata.json")
	data, err := json.MarshalIndent(session, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal session metadata: %w", err)
	}

	if err := os.WriteFile(metadataPath, data, 0644); err != nil {
		return fmt.Errorf("write session metadata: %w", err)
	}

	return nil
}

func loadSessionMetadata(sessionDir string) (*Session, error) {
	metadataPath := filepath.Join(sessionDir, "metadata.json")
	data, err := os.ReadFile(metadataPath)
	if err != nil {
		return nil, fmt.Errorf("read session metadata: %w", err)
	}

	var session Session
	if err := json.Unmarshal(data, &session); err != nil {
		return nil, fmt.Errorf("unmarshal session metadata: %w", err)
	}

	return &session, nil
}
