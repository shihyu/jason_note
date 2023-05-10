package binance

import (
	"fmt"
	"github.com/fcamel/golang-practice/utils"
	"net/http"
	"testing"

	"github.com/adshao/go-binance/v2/common"
	"github.com/stretchr/testify/suite"
)

type serverServiceTestSuite struct {
	baseTestSuite
}

func TestServerService(t *testing.T) {
	utils.Trace("")
	suite.Run(t, new(serverServiceTestSuite))
}

func (s *serverServiceTestSuite) TestPing() {
	utils.Trace("")
	data := []byte(`{}`)
	s.mockDo(data, nil)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})

	err := s.client.NewPingService().Do(newContext())
	s.r().NoError(err)
}

func (s *serverServiceTestSuite) TestServerTime() {
	utils.Trace("")
	data := []byte(`{
        "serverTime": 1499827319559
    }`)
	s.mockDo(data, nil)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})

	serverTime, err := s.client.NewServerTimeService().Do(newContext())
	s.r().NoError(err)
	s.r().EqualValues(1499827319559, serverTime)
}

func (s *serverServiceTestSuite) TestServerTimeError() {
	utils.Trace("")
	s.mockDo([]byte("{}"), fmt.Errorf("dummy error"), http.StatusInternalServerError)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})
	_, err := s.client.NewServerTimeService().Do(newContext())
	s.r().Error(err)
	s.r().Contains(err.Error(), "dummy error")
}

func (s *serverServiceTestSuite) TestServerTimeBadRequest() {
	utils.Trace("")
	s.mockDo([]byte(`{
        "code": -1121,
        "msg": "Invalid symbol."
    }`), nil, http.StatusBadRequest)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})
	_, err := s.client.NewServerTimeService().Do(newContext())
	s.r().Error(err)
	s.r().True(common.IsAPIError(err))
}

func (s *serverServiceTestSuite) TestInvalidResponseBody() {
	utils.Trace("")
	s.mockDo([]byte(``), nil)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})
	_, err := s.client.NewServerTimeService().Do(newContext())
	s.r().Error(err)
	s.r().False(common.IsAPIError(err))
}

func (s *serverServiceTestSuite) TestSetServerTime() {
	utils.Trace("")
	data := []byte(`1399827319559`)
	s.mockDo(data, nil)
	defer s.assertDo()

	s.assertReq(func(r *request) {
		e := newRequest()
		s.assertRequestEqual(e, r)
	})

	timeOffset, err := s.client.NewSetServerTimeService().Do(newContext())
	s.r().NoError(err)
	s.r().NotZero(s.client.TimeOffset)
	s.r().EqualValues(timeOffset, s.client.TimeOffset)
}
