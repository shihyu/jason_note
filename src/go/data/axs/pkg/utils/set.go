package utils

type Set[T comparable] struct {
	m map[T]struct{}
	s []T
}

func NewSet[T comparable]() *Set[T] {
	return &Set[T]{
		m: make(map[T]struct{}),
		s: make([]T, 0, 10),
	}
}

func (set *Set[T]) Add(item T) {
	if _, exists := set.m[item]; !exists {
		set.m[item] = struct{}{}
		set.s = append(set.s, item)
	}
}

func (set *Set[T]) Contains(item T) bool {
	_, exists := set.m[item]
	return exists
}

func (set *Set[T]) ToSlice() []T {
	return set.s
}
