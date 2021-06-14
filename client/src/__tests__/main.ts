
function sum(a: number, b: number) {
  return a + b;
}

test('adds 1 + 2 to equal 3', () => {
  expect(sum(1, 2)).toBe(3);
});

function addOne(num: number) {
  return num + 1;
}

test('add 1', () => {
  expect(addOne(1)).toBe(2);
});
