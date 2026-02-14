package main

import "testing"

var inputs []Input

func init() {
	const n = 10_000_000
	inputs = make([]Input, n)
	for i := range inputs {
		inputs[i] = Input{a: int64(i), b: int64(i * 2)}
	}
}

func BenchmarkCountBad(b *testing.B) {
	for i := 0; i < b.N; i++ {
		countBad(inputs)
	}
}

func BenchmarkCountGood(b *testing.B) {
	for i := 0; i < b.N; i++ {
		countGood(inputs)
	}
}
