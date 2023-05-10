package Interface

type WSReqData interface {
	GetType() int
	Len() int
	ToString() string
}
