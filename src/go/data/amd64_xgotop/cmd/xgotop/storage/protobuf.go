package storage

import (
	"bufio"
	"context"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sync"

	"google.golang.org/protobuf/proto"
)

type ProtobufStore struct {
	baseDir    string
	sessionID  string
	file       *os.File
	writer     *bufio.Writer
	session    *Session
	eventCount int64
	mu         sync.RWMutex
}

func NewProtobufStore(baseDir string, session *Session) (EventStore, error) {
	sessionDir := filepath.Join(baseDir, session.ID)
	if err := os.MkdirAll(sessionDir, 0755); err != nil {
		return nil, fmt.Errorf("create session directory: %w", err)
	}

	if err := saveSessionMetadata(sessionDir, session); err != nil {
		return nil, fmt.Errorf("save session metadata: %w", err)
	}

	eventsPath := filepath.Join(sessionDir, "events.pb")
	file, err := os.OpenFile(eventsPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("create events file: %w", err)
	}

	store := &ProtobufStore{
		baseDir:   baseDir,
		sessionID: session.ID,
		file:      file,
		writer:    bufio.NewWriterSize(file, 64*1024),
		session:   session,
	}

	return store, nil
}

func OpenProtobufStore(baseDir, sessionID string) (EventStore, error) {
	sessionDir := filepath.Join(baseDir, sessionID)

	session, err := loadSessionMetadata(sessionDir)
	if err != nil {
		return nil, fmt.Errorf("load session metadata: %w", err)
	}

	eventsPath := filepath.Join(sessionDir, "events.pb")
	file, err := os.OpenFile(eventsPath, os.O_RDWR|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("open events file: %w", err)
	}

	eventCount, err := countProtobufEvents(eventsPath)
	if err != nil {
		file.Close()
		return nil, fmt.Errorf("count events: %w", err)
	}

	store := &ProtobufStore{
		baseDir:    baseDir,
		sessionID:  sessionID,
		file:       file,
		writer:     bufio.NewWriterSize(file, 64*1024),
		session:    session,
		eventCount: eventCount,
	}

	return store, nil
}

func (s *ProtobufStore) WriteEvent(event *Event) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	pbEvent := &RuntimeEvent{
		Timestamp:       event.Timestamp,
		EventType:       uint64(event.EventType),
		Goroutine:       event.Goroutine,
		ParentGoroutine: event.ParentGoroutine,
		Attributes:      event.Attributes[:],
	}

	data, err := proto.Marshal(pbEvent)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}

	lengthBuf := make([]byte, 4)
	binary.LittleEndian.PutUint32(lengthBuf, uint32(len(data)))
	if _, err := s.writer.Write(lengthBuf); err != nil {
		return fmt.Errorf("write length: %w", err)
	}

	if _, err := s.writer.Write(data); err != nil {
		return fmt.Errorf("write event: %w", err)
	}

	s.eventCount++
	return nil
}

func (s *ProtobufStore) WriteBatch(events []*Event) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	batch := &RuntimeEventBatch{
		Events: make([]*RuntimeEvent, len(events)),
	}

	for i, event := range events {
		batch.Events[i] = &RuntimeEvent{
			Timestamp:       event.Timestamp,
			EventType:       uint64(event.EventType),
			Goroutine:       event.Goroutine,
			ParentGoroutine: event.ParentGoroutine,
			Attributes:      event.Attributes[:],
		}
	}

	data, err := proto.Marshal(batch)
	if err != nil {
		return fmt.Errorf("marshal batch: %w", err)
	}

	batchMarker := make([]byte, 4)
	binary.LittleEndian.PutUint32(batchMarker, 0xFFFFFFFF)
	if _, err := s.writer.Write(batchMarker); err != nil {
		return fmt.Errorf("write batch marker: %w", err)
	}

	lengthBuf := make([]byte, 4)
	binary.LittleEndian.PutUint32(lengthBuf, uint32(len(data)))
	if _, err := s.writer.Write(lengthBuf); err != nil {
		return fmt.Errorf("write batch length: %w", err)
	}

	if _, err := s.writer.Write(data); err != nil {
		return fmt.Errorf("write batch: %w", err)
	}

	if err := s.writer.Flush(); err != nil {
		return fmt.Errorf("flush writer: %w", err)
	}

	s.eventCount += int64(len(events))
	return nil
}

func (s *ProtobufStore) ReadEvents(ctx context.Context, filter *EventFilter) ([]*Event, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	file, err := os.Open(filepath.Join(s.baseDir, s.sessionID, "events.pb"))
	if err != nil {
		return nil, fmt.Errorf("open file for reading: %w", err)
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	var events []*Event
	offset := 0

	for {
		select {
		case <-ctx.Done():
			return events, ctx.Err()
		default:
		}

		lengthBuf := make([]byte, 4)
		if _, err := io.ReadFull(reader, lengthBuf); err != nil {
			if err == io.EOF {
				break
			}
			return nil, fmt.Errorf("read length: %w", err)
		}

		length := binary.LittleEndian.Uint32(lengthBuf)

		// Check if this is a batch marker
		if length == 0xFFFFFFFF {
			// Read batch length
			if _, err := io.ReadFull(reader, lengthBuf); err != nil {
				return nil, fmt.Errorf("read batch length: %w", err)
			}
			length = binary.LittleEndian.Uint32(lengthBuf)

			data := make([]byte, length)
			if _, err := io.ReadFull(reader, data); err != nil {
				return nil, fmt.Errorf("read batch data: %w", err)
			}

			batch := &RuntimeEventBatch{}
			if err := proto.Unmarshal(data, batch); err != nil {
				return nil, fmt.Errorf("unmarshal batch: %w", err)
			}

			for _, pbEvent := range batch.Events {
				if shouldIncludeEvent(pbEvent, filter, offset, len(events)) {
					events = append(events, convertFromProto(pbEvent))
				}
				offset++
				if filter != nil && filter.Limit > 0 && len(events) >= filter.Limit {
					return events, nil
				}
			}
		} else {
			data := make([]byte, length)
			if _, err := io.ReadFull(reader, data); err != nil {
				return nil, fmt.Errorf("read event data: %w", err)
			}

			pbEvent := &RuntimeEvent{}
			if err := proto.Unmarshal(data, pbEvent); err != nil {
				return nil, fmt.Errorf("unmarshal event: %w", err)
			}

			if shouldIncludeEvent(pbEvent, filter, offset, len(events)) {
				events = append(events, convertFromProto(pbEvent))
			}
			offset++

			if filter != nil && filter.Limit > 0 && len(events) >= filter.Limit {
				return events, nil
			}
		}
	}

	return events, nil
}

func (s *ProtobufStore) GetGoroutines(ctx context.Context) ([]uint32, error) {
	events, err := s.ReadEvents(ctx, nil)
	if err != nil {
		return nil, err
	}

	goroutineMap := make(map[uint32]bool)
	for _, event := range events {
		goroutineMap[event.Goroutine] = true
	}

	goroutines := make([]uint32, 0, len(goroutineMap))
	for gid := range goroutineMap {
		goroutines = append(goroutines, gid)
	}

	return goroutines, nil
}

func (s *ProtobufStore) Close() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.writer != nil {
		if err := s.writer.Flush(); err != nil {
			return fmt.Errorf("flush writer: %w", err)
		}
	}

	if s.file != nil {
		if err := s.file.Close(); err != nil {
			return fmt.Errorf("close file: %w", err)
		}
	}

	return nil
}

func (s *ProtobufStore) GetSession() *Session {
	s.mu.RLock()
	defer s.mu.RUnlock()

	sessionCopy := *s.session
	sessionCopy.EventCount = s.eventCount
	return &sessionCopy
}

func (s *ProtobufStore) UpdateSession(session *Session) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.session = session
	sessionDir := filepath.Join(s.baseDir, s.sessionID)
	return saveSessionMetadata(sessionDir, session)
}

func countProtobufEvents(path string) (int64, error) {
	file, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return 0, nil
		}
		return 0, err
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	count := int64(0)

	for {
		lengthBuf := make([]byte, 4)
		if _, err := io.ReadFull(reader, lengthBuf); err != nil {
			if err == io.EOF {
				break
			}
			return 0, fmt.Errorf("read length: %w", err)
		}

		length := binary.LittleEndian.Uint32(lengthBuf)

		// Check if this is a batch marker
		if length == 0xFFFFFFFF {
			// Read batch length
			if _, err := io.ReadFull(reader, lengthBuf); err != nil {
				return 0, fmt.Errorf("read batch length: %w", err)
			}
			length = binary.LittleEndian.Uint32(lengthBuf)

			data := make([]byte, length)
			if _, err := io.ReadFull(reader, data); err != nil {
				return 0, fmt.Errorf("read batch data: %w", err)
			}

			batch := &RuntimeEventBatch{}
			if err := proto.Unmarshal(data, batch); err != nil {
				return 0, fmt.Errorf("unmarshal batch: %w", err)
			}

			count += int64(len(batch.Events))
		} else {
			if _, err := reader.Discard(int(length)); err != nil {
				return 0, fmt.Errorf("skip event data: %w", err)
			}
			count++
		}
	}

	return count, nil
}

func shouldIncludeEvent(pbEvent *RuntimeEvent, filter *EventFilter, offset int, currentCount int) bool {
	if filter == nil {
		return true
	}

	if filter.Offset > 0 && offset < filter.Offset {
		return false
	}

	if filter.Goroutine != nil && pbEvent.Goroutine != *filter.Goroutine {
		return false
	}

	if filter.EventType != nil && EventType(pbEvent.EventType) != *filter.EventType {
		return false
	}

	if filter.StartTime != nil && pbEvent.Timestamp < *filter.StartTime {
		return false
	}

	if filter.EndTime != nil && pbEvent.Timestamp > *filter.EndTime {
		return false
	}

	return true
}

func convertFromProto(pbEvent *RuntimeEvent) *Event {
	event := &Event{
		Timestamp:       pbEvent.Timestamp,
		EventType:       EventType(pbEvent.EventType),
		Goroutine:       pbEvent.Goroutine,
		ParentGoroutine: pbEvent.ParentGoroutine,
	}

	copy(event.Attributes[:], pbEvent.Attributes)

	return event
}
