package consumer

func retryProcess(fn func() error) error {
	return fn()
}
