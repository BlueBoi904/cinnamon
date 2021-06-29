// @ts-ignore
function sum(a, b) {
  return a + b;
}

test("adds 1 + 2 to equal 3", () => {
  expect(sum(1, 2)).toBe(3);
});

function add_one(num) {
  return num + 1;
}

test("adds 1 to a number", () => {
  expect(add_one(6)).toBe(7);
});
