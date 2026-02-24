// Package main_test contains unit tests for the xgotop main package,
// specifically testing the sampling rate parsing functionality.
package main

import (
	"testing"

	"go.sazak.io/xgotop/cmd/xgotop/storage"
)

func TestParseSamplingRates(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected map[storage.EventType]uint32
		wantErr  bool
		errMsg   string
	}{
		// Valid cases
		{
			name:  "single event with 1% rate",
			input: "makemap:0.01",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 1,
			},
			wantErr: false,
		},
		{
			name:  "single event with 10% rate",
			input: "newgoroutine:0.1",
			expected: map[storage.EventType]uint32{
				storage.EventTypeNewGoroutine: 10,
			},
			wantErr: false,
		},
		{
			name:  "single event with 50% rate",
			input: "makeslice:0.5",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeSlice: 50,
			},
			wantErr: false,
		},
		{
			name:  "single event with 100% rate",
			input: "newobject:1.0",
			expected: map[storage.EventType]uint32{
				storage.EventTypeNewObject: 100,
			},
			wantErr: false,
		},
		{
			name:  "multiple events with different rates",
			input: "makemap:0.01,newgoroutine:0.5,makeslice:0.99",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap:      1,
				storage.EventTypeNewGoroutine: 50,
				storage.EventTypeMakeSlice:    99,
			},
			wantErr: false,
		},
		{
			name:  "all events with various rates",
			input: "casgstatus:0.05,makeslice:0.1,makemap:0.2,newobject:0.5,newgoroutine:0.8,goexit:0.95",
			expected: map[storage.EventType]uint32{
				storage.EventTypeCasGStatus:   5,
				storage.EventTypeMakeSlice:    10,
				storage.EventTypeMakeMap:      20,
				storage.EventTypeNewObject:    50,
				storage.EventTypeNewGoroutine: 80,
				storage.EventTypeGoExit:       95,
			},
			wantErr: false,
		},
		{
			name:     "empty string",
			input:    "",
			expected: map[storage.EventType]uint32{},
			wantErr:  false,
		},
		{
			name:  "zero rate",
			input: "makemap:0",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 0,
			},
			wantErr: false,
		},
		{
			name:  "very small rate (0.001 -> 0.1%)",
			input: "makemap:0.001",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 0, // Rounds down
			},
			wantErr: false,
		},
		{
			name:  "rate that rounds up (0.005 -> 0.5%)",
			input: "makemap:0.005",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 1, // Rounds up due to math.Round
			},
			wantErr: false,
		},
		{
			name:  "rate with many decimals",
			input: "makemap:0.123456789",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 12, // 12.3456789 rounds to 12
			},
			wantErr: false,
		},
		{
			name:  "spaces around values",
			input: " makemap : 0.5 , newgoroutine : 0.1 ",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap:      50,
				storage.EventTypeNewGoroutine: 10,
			},
			wantErr: false,
		},
		// Error cases
		{
			name:    "invalid format - missing colon",
			input:   "makemap0.5",
			wantErr: true,
			errMsg:  "invalid sampling rate format",
		},
		{
			name:    "invalid format - empty value",
			input:   "makemap:",
			wantErr: true,
			errMsg:  "invalid rate for makemap",
		},
		{
			name:    "invalid format - empty event name",
			input:   ":0.5",
			wantErr: true,
			errMsg:  "unknown event name: ",
		},
		{
			name:    "invalid event name",
			input:   "nonexistent:0.5",
			wantErr: true,
			errMsg:  "unknown event name: nonexistent",
		},
		{
			name:    "invalid rate - not a number",
			input:   "makemap:abc",
			wantErr: true,
			errMsg:  "invalid rate for makemap",
		},
		{
			name:    "rate too high",
			input:   "makemap:1.1",
			wantErr: true,
			errMsg:  "sampling rate must be between 0 and 1",
		},
		{
			name:    "negative rate",
			input:   "makemap:-0.1",
			wantErr: true,
			errMsg:  "sampling rate must be between 0 and 1",
		},
		{
			name:    "multiple colons",
			input:   "makemap:0.5:extra",
			wantErr: true,
			errMsg:  "invalid sampling rate format",
		},
		{
			name:  "duplicate event",
			input: "makemap:0.1,makemap:0.5",
			expected: map[storage.EventType]uint32{
				storage.EventTypeMakeMap: 50, // Last value wins
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := parseSamplingRates(tt.input)

			if tt.wantErr {
				if err == nil {
					t.Errorf("expected error containing '%s', got nil", tt.errMsg)
					return
				}
				if tt.errMsg != "" && !contains(err.Error(), tt.errMsg) {
					t.Errorf("expected error containing '%s', got '%s'", tt.errMsg, err.Error())
				}
				return
			}

			if err != nil {
				t.Errorf("unexpected error: %v", err)
				return
			}

			if len(result) != len(tt.expected) {
				t.Errorf("expected %d rates, got %d", len(tt.expected), len(result))
				return
			}

			for eventType, expectedRate := range tt.expected {
				actualRate, ok := result[eventType]
				if !ok {
					t.Errorf("missing rate for event type %d", eventType)
					continue
				}
				if actualRate != expectedRate {
					t.Errorf("for event type %d: expected rate %d%%, got %d%%",
						eventType, expectedRate, actualRate)
				}
			}
		})
	}
}

func TestGetEventName(t *testing.T) {
	tests := []struct {
		eventType storage.EventType
		expected  string
	}{
		{storage.EventTypeCasGStatus, "casgstatus"},
		{storage.EventTypeMakeSlice, "makeslice"},
		{storage.EventTypeMakeMap, "makemap"},
		{storage.EventTypeNewObject, "newobject"},
		{storage.EventTypeNewGoroutine, "newgoroutine"},
		{storage.EventTypeGoExit, "goexit"},
		{storage.EventType(999), "unknown(999)"}, // Invalid event type
	}

	for _, tt := range tests {
		t.Run(tt.expected, func(t *testing.T) {
			result := getEventName(tt.eventType)
			if result != tt.expected {
				t.Errorf("expected '%s', got '%s'", tt.expected, result)
			}
		})
	}
}

// Helper function
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && (s[:len(substr)] == substr || contains(s[1:], substr)))
}

// Benchmark tests
func BenchmarkParseSamplingRates(b *testing.B) {
	testCases := []struct {
		name  string
		input string
	}{
		{"single", "makemap:0.5"},
		{"multiple", "makemap:0.1,newgoroutine:0.5,makeslice:0.9"},
		{"all_events", "casgstatus:0.05,makeslice:0.1,makemap:0.2,newobject:0.5,newgoroutine:0.8,goexit:0.95"},
	}

	for _, tc := range testCases {
		b.Run(tc.name, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				_, _ = parseSamplingRates(tc.input)
			}
		})
	}
}
