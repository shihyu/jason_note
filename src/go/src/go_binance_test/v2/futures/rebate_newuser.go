package futures

import (
	"context"
	"encoding/json"
	"github.com/fcamel/golang-practice/utils"
	"net/http"
)

// GetRebateNewUserService
type GetRebateNewUserService struct {
	c           *Client
	brokerageID string
	type_future int
}

// BrokerageID setting
func (s *GetRebateNewUserService) BrokerageID(brokerageID string) *GetRebateNewUserService {
	utils.Trace("")
	s.brokerageID = brokerageID
	return s
}

// Type future setting
func (s *GetRebateNewUserService) Type(type_future int) *GetRebateNewUserService {
	utils.Trace("")
	s.type_future = type_future
	return s
}

// Do send request
func (s *GetRebateNewUserService) Do(ctx context.Context, opts ...RequestOption) (res *RebateNewUser, err error) {
	utils.Trace("")
	r := &request{
		method:   http.MethodGet,
		endpoint: "/fapi/v1/apiReferral/ifNewUser",
		secType:  secTypeSigned,
	}

	if s.brokerageID != "" {
		r.setParam("brokerId", s.brokerageID)
	}
	if s.type_future != 0 {
		r.setParam("type", s.type_future)
	}

	data, _, err := s.c.callAPI(ctx, r, opts...)
	if err != nil {
		return &RebateNewUser{}, err
	}

	err = json.Unmarshal(data, &res)
	if err != nil {
		return &RebateNewUser{}, err
	}
	return res, nil
}

// PositionRisk define position risk info
type RebateNewUser struct {
	BrokerId      string `json:"brokerId"`
	RebateWorking bool   `json:"rebateWorking"`
	IfNewUser     bool   `json:"ifNewUser"`
}
