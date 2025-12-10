package utils

import "github.com/shopspring/decimal"

func DecimalFromString(strs ...string) ([]decimal.Decimal, error) {
	result := make([]decimal.Decimal, 0, len(strs))
	for _, s := range strs {
		d, err := decimal.NewFromString(s)
		if err != nil {
			return nil, err
		}
		result = append(result, d)
	}
	return result, nil
}
