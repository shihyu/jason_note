package storage

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

type Manager struct {
	baseDir string
	mu      sync.RWMutex
}

func NewManager(baseDir string) (*Manager, error) {
	if err := os.MkdirAll(baseDir, 0755); err != nil {
		return nil, fmt.Errorf("create base directory: %w", err)
	}

	return &Manager{
		baseDir: baseDir,
	}, nil
}

func (m *Manager) ListSessions(ctx context.Context) ([]*Session, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	entries, err := os.ReadDir(m.baseDir)
	if err != nil {
		return nil, fmt.Errorf("read directory: %w", err)
	}

	var sessions []*Session
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}

		sessionDir := filepath.Join(m.baseDir, entry.Name())
		session, err := loadSessionMetadata(sessionDir)
		if err != nil {
			continue
		}

		sessions = append(sessions, session)
	}

	return sessions, nil
}

func (m *Manager) GetSession(ctx context.Context, id string) (*Session, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	sessionDir := filepath.Join(m.baseDir, id)
	return loadSessionMetadata(sessionDir)
}

func (m *Manager) OpenSession(ctx context.Context, id string) (EventStore, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	sessionDir := filepath.Join(m.baseDir, id)

	if _, err := os.Stat(filepath.Join(sessionDir, "events.pb")); err == nil {
		return OpenProtobufStore(m.baseDir, id)
	}
	if _, err := os.Stat(filepath.Join(sessionDir, "events.jsonl")); err == nil {
		return OpenJSONLStore(m.baseDir, id)
	}

	return nil, fmt.Errorf("no event store found for session %s", id)
}

func (m *Manager) CreateSession(ctx context.Context, session *Session, format string) (EventStore, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	sessionDir := filepath.Join(m.baseDir, session.ID)
	if err := os.MkdirAll(sessionDir, 0755); err != nil {
		return nil, fmt.Errorf("create session directory: %w", err)
	}

	if err := saveSessionMetadata(sessionDir, session); err != nil {
		return nil, fmt.Errorf("save session metadata: %w", err)
	}

	format = strings.ToLower(format)
	switch format {
	case "jsonl", "json":
		return NewJSONLStore(m.baseDir, session)
	case "protobuf", "pb", "proto":
		return NewProtobufStore(m.baseDir, session)
	default:
		return nil, fmt.Errorf("unknown format: %s (supported: jsonl, protobuf)", format)
	}
}

func (m *Manager) DeleteSession(ctx context.Context, id string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	sessionDir := filepath.Join(m.baseDir, id)
	return os.RemoveAll(sessionDir)
}

func (m *Manager) Close() error {
	return nil
}
