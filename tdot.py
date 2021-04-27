import json
import sys
import shutil
import itertools
from enum import Enum


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


CORNERS = {
    (Direction.UP, Direction.RIGHT): '\u250c',
    (Direction.UP, Direction.LEFT): '\u2510',
    (Direction.RIGHT, Direction.DOWN): '\u2510',
    (Direction.RIGHT, Direction.UP): '\u2518',
    (Direction.DOWN, Direction.LEFT): '\u2518',
    (Direction.DOWN, Direction.RIGHT): '\u2514',
    (Direction.LEFT, Direction.UP): '\u2514',
    (Direction.LEFT, Direction.DOWN): '\u250c',
}


class Layout:
    def __init__(self, width):
        self.width = width
        self.contents = []

    def _extend(self, height):
        new_lines = height - len(self.contents)
        if new_lines > 0:
            for _ in range(new_lines):
                self.contents.append([' '] * self.width)

    def print(self, x, y, s):
        self._extend(y + 1)
        width = min(len(s), self.width - x + 1)
        self.contents[y][x:x + width] = list(s[:width])

    def print_vert(self, x, y, s):
        self._extend(y + len(s))
        for i, c in enumerate(s):
            self.contents[y + i][x] = c

    def line(self, x1, y1, x2, y2):
        self._extend(y1 + 1)
        self._extend(y2 + 1)
        if x1 == x2:
            # Vertical.
            self.print_vert(x1, min(y1, y2), '\u2502' * abs(y1 - y2))
        elif y1 == y2:
            # Horizontal.
            self.print(min(x1, x2), y1, '\u2500' * abs(x1 - x2))
        else:
            assert False, "I only know how to draw orthogonal lines"

    def path(self, points):
        """Draw a sequence of lines given as a sequence of their
        intermediate points.
        """
        last_dir = None

        for (x1, y1), (x2, y2) in pairwise(points):
            if x1 == x2 and y1 == y2:
                continue
            self.line(x1, y1, x2, y2)

            # Which direction did we just move?
            if x2 < x1:
                dir = Direction.LEFT
            elif x2 > x1:
                dir = Direction.RIGHT
            elif y2 < y1:
                dir = Direction.UP
            else:
                dir = Direction.DOWN

            # Draw a corner.
            if last_dir is not None and (last_dir, dir) in CORNERS:
                self.print(x1, y1, CORNERS[(last_dir, dir)])

            last_dir = dir

    def display(self):
        return '\n'.join(''.join(ln) for ln in self.contents)

    def __str__(self):
        return self.display()


def parse_spline(pos):
    for coord in pos.split():
        if coord.startswith('e,') or coord.startswith('s,'):
            continue  # Not sure what to do with these yet.
        yield [float(n) for n in coord.split(',')]


def pairwise(iterable):
    """From itertools recipes."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def tdot(dot):
    term_w, term_h = shutil.get_terminal_size()
    term_h -= 3  # For prompt and such.

    bb = [float(n) for n in dot['bb'].split(',')]
    assert bb[0] == bb[1] == 0
    _, _, bb_w, bb_h = bb

    scale_x = bb_w / term_w
    scale_y = bb_h / term_h

    def _x(dot_x):
        return int(dot_x / scale_x)

    def _y(dot_y):
        return int((bb_h - dot_y) / scale_y)

    layout = Layout(term_w)

    # Draw edges.
    for edge in dot['edges']:
        layout.path((_x(x), _y(y)) for x, y in parse_spline(edge['pos']))

    # Draw objects.
    for obj in dot['objects']:
        obj_x, obj_y = [float(n) for n in obj['pos'].split(',')]
        obj_w = float(obj['width'])
        obj_h = float(obj['height'])
        layout.print(_x(obj_x - obj_w), _y(obj_y - obj_h), obj['name'])

    print(layout)


if __name__ == '__main__':
    tdot(json.load(sys.stdin))
