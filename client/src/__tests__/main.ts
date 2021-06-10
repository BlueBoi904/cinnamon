type SumArgs = {
  a: number;
  b: number;
};

function sum(a, b): SumArgs {
  return a + b;
}

test('adds 1 + 2 to equal 3', () => {
  expect(sum(1, 2)).toBe(3);
});

type AddOneArgs = {
  num: number;
};

function addOne(num): AddOneArgs {
  return num + 1;
}

test('add 1', () => {
  expect(addOne(1)).toBe(2);
});
