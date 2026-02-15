package model

type User struct {
	ID   string
	Name string
}

type Order struct {
	ID      string
	UserID  string
	Product string
	Amount  float64
	Status  string
}
