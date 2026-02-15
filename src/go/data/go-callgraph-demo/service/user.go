package service

import (
	"fmt"

	"github.com/demo/go-callgraph-demo/model"
	"github.com/demo/go-callgraph-demo/util"
)

type UserService struct {
	users map[string]*model.User
}

func NewUserService() *UserService {
	return &UserService{
		users: make(map[string]*model.User),
	}
}

func (s *UserService) CreateUser(name string) *model.User {
	id := util.GenerateID("user")
	user := &model.User{
		ID:   id,
		Name: name,
	}
	s.users[id] = user
	s.validate(user)
	return user
}

func (s *UserService) GetUser(id string) (*model.User, error) {
	user, ok := s.users[id]
	if !ok {
		return nil, fmt.Errorf("user not found: %s", id)
	}
	return user, nil
}

func (s *UserService) validate(user *model.User) {
	if user.Name == "" {
		panic("user name cannot be empty")
	}
}
