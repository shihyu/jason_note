package discount

import "testing"

func TestMemberGets20PercentOff(t *testing.T) {
	got, err := CalculateDiscount(100, true)
	if err != nil || got != 80 {
		t.Fatalf("want 80, got %v err %v", got, err)
	}
}

func TestNonMemberPaysFullPrice(t *testing.T) {
	got, err := CalculateDiscount(100, false)
	if err != nil || got != 100 {
		t.Fatalf("want 100, got %v err %v", got, err)
	}
}

func TestNegativePriceReturnsError(t *testing.T) {
	_, err := CalculateDiscount(-1, true)
	if err == nil {
		t.Fatalf("want error, got nil")
	}
}

func TestZeroPriceBoundaryDoesNotError(t *testing.T) {
	got, err := CalculateDiscount(0, false)
	if err != nil || got != 0 {
		t.Fatalf("want 0, got %v err %v", got, err)
	}
}
