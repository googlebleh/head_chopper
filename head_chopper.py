#!/usr/bin/env python3

import argparse
import math

from PIL import Image


def row_difference(a, b):
    assert(len(a) == len(b))
    r = []
    for pixel_a, pixel_b in zip(a, b):
        r1, g1, b1, a1 = pixel_a
        r2, g2, b2, a2 = pixel_b
        r.append((r1-r2, g1-g2, b1-b2, a1-a2))
    return r


def almost_zero(pixel):
    epsilon = 50
    r, g, b, a = pixel
    return (abs(r) < epsilon
            and abs(g) < epsilon
            and abs(b) < epsilon
            and abs(a) < epsilon)


def almost_eq(a, b):
    return all(almost_zero(pixel_diff) for pixel_diff in row_difference(a, b))


def all_almost_eq(segments):
    assert(len(segments) > 0)
    first = segments[0]
    for e in segments[1:]:
        if not almost_eq(first, e):
            return False
    return True


class Chopper:
    segment_len = 100
    def __init__(self, input_fpath, heads_wide, heads_tall):
        self.input_image = Image.open(input_fpath)
        self.input_rgba = self.input_image.getdata()

        self.heads_wide = heads_wide
        self.heads_tall = heads_tall

    def getpixel(self, row, col):
        width, height = self.input_image.size
        assert(0 <= row < height)
        assert(0 <= col < width)
        return self.input_rgba[width * row + col]

    def calculate_head_width(self, base_row, left_start):
        width, _ = self.input_image.size
        head_width = None

        # guess == 0 is vacuously true
        for guess in range(1, math.ceil(width / self.heads_wide)):
            segments = []
            for head_i in range(self.heads_wide):
                segment_start_col = left_start + (head_i * guess)
                segment = [self.getpixel(base_row, segment_start_col + j) for j in range(self.segment_len)]
                segments.append(segment)

            if all_almost_eq(segments):
                print(f"guessed skip = {guess}")
                head_width = guess

        return head_width

    def save_heads(self, head_width, fname_prefix="output-"):
        _, height = self.input_image.size
        for head_i in range(self.heads_wide):
            new_image = []
            for row in range(height):
                for head_col in range(head_width):
                    col = head_i * head_width + head_col
                    p = self.getpixel(row, col)
                    new_image.append(p)

            image = Image.new("RGBA", (head_width, height))
            image.putdata(new_image)
            image.save(f"{fname_prefix}{head_i}.png")


def getargs():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input-file", help="input sprite file")
    ap.add_argument("-o", "--output-file", help="output sprite file prefix")
    return ap.parse_args()


def main():
    args = getargs()
    c = Chopper(args.input_file, 5, 9)
    head_width = c.calculate_head_width(130, 30)
    c.save_heads(head_width)


if __name__ == "__main__":
    main()
