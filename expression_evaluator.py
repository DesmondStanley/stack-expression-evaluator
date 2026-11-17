
from pathlib import Path

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"


# Stack data structure

class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


# Expression evaluation

class ExpressionError(Exception):
    """Raised when an expression is invalid or cannot be evaluated."""


PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3}  # u- = unary minus


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses."""
    tokens = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            start = i
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            text = expression[start:i]
            try:
                tokens.append(float(text))
            except ValueError:
                raise ExpressionError(f"Invalid number '{text}'")
        elif ch in "+-*/()":
            if ch == "-" and (not tokens or tokens[-1] in ("(", "+", "-", "*", "/", "u-")):
                tokens.append("u-")  # a minus with no left operand is unary
            else:
                tokens.append(ch)
            i += 1
        else:
            raise ExpressionError(f"Invalid character '{ch}'")
    return tokens


def apply_operator(operators, values):
    """Pop one operator and its operand(s), then push the result."""
    op = operators.pop()
    if op == "u-":
        if values.is_empty():
            raise ExpressionError("Invalid expression")
        values.push(-values.pop())
        return
    if values.size() < 2:
        raise ExpressionError("Invalid expression")
    right = values.pop()
    left = values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ExpressionError("Division by zero")
        values.push(left / right)


def evaluate_expression(expression):
    """Evaluate an expression using a value stack and an operator stack."""
    tokens = tokenize(expression)
    if not tokens:
        raise ExpressionError("Empty expression")

    values = Stack()
    operators = Stack()

    for token in tokens:
        if isinstance(token, float):
            values.push(token)
        elif token == "(":
            operators.push(token)
        elif token == ")":
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, values)
            if operators.is_empty():
                raise ExpressionError("Mismatched parentheses")
            operators.pop()  # discard the "("
        elif token == "u-":
            operators.push(token)  # prefix operator: nothing to reduce yet
        else:  # + - * /
            while (
                not operators.is_empty()
                and operators.peek() != "("
                and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]
            ):
                apply_operator(operators, values)
            operators.push(token)

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ExpressionError("Mismatched parentheses")
        apply_operator(operators, values)

    if values.size() != 1:
        raise ExpressionError("Invalid expression")
    return values.pop()


def format_result(value):
    """Show whole numbers without a decimal point (13 instead of 13.0)."""
    if value == int(value):
        return str(int(value))
    return str(round(value, 10))


# File handling

def is_separator(line):
    """A separator line has no digits/parentheses and is made of _ - = * # and spaces."""
    text = line.strip()
    return len(text.replace(" ", "")) >= 3 and all(c in "_-=*# " for c in text)


def process_file(input_path, output_path):
    """Read expressions, evaluate them, and write results in the same layout."""
    output_lines = []
    with open(input_path, "r", encoding="utf-8") as infile:
        for raw in infile:
            line = raw.rstrip("\n")
            if line.strip() == "" or is_separator(line):
                output_lines.append(line)  # keep blank lines and separators
                continue
            try:
                output_lines.append(format_result(evaluate_expression(line)))
            except ExpressionError as err:
                output_lines.append(f"Error: {err}")
            except Exception as err:  # safety net for unexpected problems
                output_lines.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines) + "\n")


def main():
    base = Path(__file__).resolve().parent  # files live next to this script
    input_path = base / INPUT_FILE
    output_path = base / OUTPUT_FILE

    if not input_path.exists():
        print(f"Could not find {input_path}. Create input.txt next to this script.")
        return

    process_file(input_path, output_path)
    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    main()