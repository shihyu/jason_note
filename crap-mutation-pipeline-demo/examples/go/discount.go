package discount

import "errors"

func CalculateDiscount(price float64, isMember bool) (float64, error) {
	if price < 0 {
		return 0, errors.New("price must not be negative")
	}
	if isMember {
		return price * 0.8, nil
	}
	return price, nil
}
