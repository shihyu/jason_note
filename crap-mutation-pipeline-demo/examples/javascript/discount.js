function calculateDiscount(price, isMember) {
  if (price < 0) {
    throw new Error("price must be non-negative");
  }
  if (isMember) {
    return price * 0.8;
  }
  return price;
}

module.exports = { calculateDiscount };
