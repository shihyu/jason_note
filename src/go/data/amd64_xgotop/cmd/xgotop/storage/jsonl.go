package storage

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
)

type JSONLStore struct {
	file       *os.File
	writer     *bufio.Writer
	session    *Session
	mu         sync.RWMutex
	eventCount int64
	baseDir    string
}

func NewJSONLStore(baseDir string, session *Session) (*JSONLStore, error) {
	if err := os.MkdirAll(baseDir, 0755); err != nil {
		return nil, fmt.Errorf("create base directory: %w", err)
	}

	sessionDir := filepath.Join(baseDir, session.ID)
	if err := os.MkdirAll(sessionDir, 0755); err != nil {
		return nil, fmt.Errorf("create session directory: %w", err)
	}

	filePath := filepath.Join(sessionDir, "events.jsonl")
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("open jsonl file: %w", err)
	}

	store := &JSONLStore{
		file:    file,
		writer:  bufio.NewWriter(file),
		session: session,
		baseDir: baseDir,
	}

	return store, nil
}

func OpenJSONLStore(baseDir string, sessionID string) (*JSONLStore, error) {
	sessionDir := filepath.Join(baseDir, sessionID)
	filePath := filepath.Join(sessionDir, "events.jsonl")

	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("open jsonl file: %w", err)
	}

	store := &JSONLStore{
		file:    file,
		baseDir: baseDir,
	}

	session, err := loadSessionMetadata(sessionDir)
	if err != nil {
		file.Close()
		return nil, fmt.Errorf("load session metadata: %w", err)
	}
	store.session = session

	return store, nil
}

func (s *JSONLStore) WriteEvent(event *Event) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}

	if _, err := s.writer.Write(data); err != nil {
		return fmt.Errorf("write event: %w", err)
	}

	if err := s.writer.WriteByte('\n'); err != nil {
		return fmt.Errorf("write newline: %w", err)
	}

	s.eventCount++
	return nil
}

func (s *JSONLStore) WriteBatch(events []*Event) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, event := range events {
		data, err := json.Marshal(event)
		if err != nil {
			return fmt.Errorf("marshal event: %w", err)
		}

		if _, err := s.writer.Write(data); err != nil {
			return fmt.Errorf("write event: %w", err)
		}

		if err := s.writer.WriteByte('\n'); err != nil {
			return fmt.Errorf("write newline: %w", err)
		}

		s.eventCount++
	}

	if err := s.writer.Flush(); err != nil {
		return fmt.Errorf("flush writer: %w", err)
	}

	return nil
}

func (s *JSONLStore) ReadEvents(ctx context.Context, filter *EventFilter) ([]*Event, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if _, err := s.file.Seek(0, 0); err != nil {
		return nil, fmt.Errorf("seek to start: %w", err)
	}

	scanner := bufio.NewScanner(s.file)
	var events []*Event
	count := 0
	skipped := 0

	for scanner.Scan() {
		select {
		case <-ctx.Done():
			return events, ctx.Err()
		default:
		}

		var event Event
		if err := json.Unmarshal(scanner.Bytes(), &event); err != nil {
			return nil, fmt.Errorf("unmarshal event: %w", err)
		}

		// Apply filters
		if filter != nil {
			if filter.Goroutine != nil && event.Goroutine != *filter.Goroutine {
				continue
			}
			if filter.EventType != nil && event.EventType != *filter.EventType {
				continue
			}
			if filter.StartTime != nil && event.Timestamp < *filter.StartTime {
				continue
			}
			if filter.EndTime != nil && event.Timestamp > *filter.EndTime {
				continue
			}
			if filter.Offset > 0 && skipped < filter.Offset {
				skipped++
				continue
			}
		}

		events = append(events, &event)
		count++

		if filter != nil && filter.Limit > 0 && count >= filter.Limit {
			break
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("scan file: %w", err)
	}

	return events, nil
}

func (s *JSONLStore) GetGoroutines(ctx context.Context) ([]uint32, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if _, err := s.file.Seek(0, 0); err != nil {
		return nil, fmt.Errorf("seek to start: %w", err)
	}

	scanner := bufio.NewScanner(s.file)
	goroutineMap := make(map[uint32]bool)

	for scanner.Scan() {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		default:
		}

		var event Event
		if err := json.Unmarshal(scanner.Bytes(), &event); err != nil {
			return nil, fmt.Errorf("unmarshal event: %w", err)
		}

		goroutineMap[event.Goroutine] = true
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("scan file: %w", err)
	}

	goroutines := make([]uint32, 0, len(goroutineMap))
	for gid := range goroutineMap {
		goroutines = append(goroutines, gid)
	}

	return goroutines, nil
}

func (s *JSONLStore) Close() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.writer != nil {
		if err := s.writer.Flush(); err != nil {
			return err
		}
	}

	if s.file != nil {
		return s.file.Close()
	}

	return nil
}

func (s *JSONLStore) GetSession() *Session {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.session
}

func (s *JSONLStore) UpdateSession(session *Session) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.session = session
	sessionDir := filepath.Join(s.baseDir, session.ID)
	return saveSessionMetadata(sessionDir, session)
}
