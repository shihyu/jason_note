package main

import (
	"fmt"
	"math"
	"strconv"
	"strings"

	"go.sazak.io/xgotop/cmd/xgotop/storage"
)

// parseSamplingRates parses the sampling rates from the command line flag
func parseSamplingRates(ratesStr string) (map[storage.EventType]uint32, error) {
	rates := make(map[storage.EventType]uint32)
	if ratesStr == "" {
		return rates, nil
	}
	pairs := strings.Split(ratesStr, ",")
	for _, pair := range pairs {
		parts := strings.Split(pair, ":")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid sampling rate format: %s", pair)
		}

		eventName := strings.TrimSpace(parts[0])
		eventType, ok := eventNameToType[eventName]
		if !ok {
			return nil, fmt.Errorf("unknown event name: %s", eventName)
		}

		rate, err := strconv.ParseFloat(strings.TrimSpace(parts[1]), 64)
		if err != nil {
			return nil, fmt.Errorf("invalid rate for %s: %v", eventName, err)
		}

		if rate < 0 || rate > 1 {
			return nil, fmt.Errorf("sampling rate must be between 0 and 1, got %f", rate)
		}

		percentage := uint32(math.Round(rate * 100))
		rates[eventType] = percentage
	}

	return rates, nil
}
