const test = require("node:test");
const assert = require("node:assert");
const { calculateDiscount } = require("./discount");

test("member gets 20 percent off", () => {
  assert.strictEqual(calculateDiscount(100, true), 80);
});

test("non-member pays full price", () => {
  assert.strictEqual(calculateDiscount(100, false), 100);
});

test("negative price throws", () => {
  assert.throws(() => calculateDiscount(-1, true));
});
