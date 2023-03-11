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
    segment_len = 60
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
                segment = [self.getpixel(base_row, segment_start_col + x) for x in range(self.segment_len)]
                segments.append(segment)

            if all_almost_eq(segments):
                print(f"guessed skip = {guess}")
                head_width = guess

        return head_width

    def guess_left_start(self, base_row):
        width, _ = self.input_image.size

        for indent in range(width - self.segment_len):
            head_width = self.calculate_head_width(base_row, indent)
            if head_width is not None:
                return head_width

    def calculate_head_height(self, base_col, top_start):
        _, height = self.input_image.size
        head_height = None

        # guess == 0 is vacuously true
        for guess in range(1, math.ceil(height / self.heads_tall)):
            segments = []
            for head_i in range(self.heads_tall):
                segment_start_row = top_start + (head_i * guess)
                segment = [self.getpixel(segment_start_row + y, base_col) for y in range(self.segment_len)]
                segments.append(segment)

            if all_almost_eq(segments):
                print(f"guessed vertical skip = {guess}")
                head_height = guess

        return head_height

    def save_heads(self, head_width, head_height, fname_prefix="output-"):
        _, height = self.input_image.size
        for head_x in range(self.heads_wide):
            for head_y in range(self.heads_tall):
                new_image = []
                for head_row in range(head_height):
                    for head_col in range(head_width):
                        row = head_y * head_height + head_row
                        col = head_x * head_width + head_col
                        p = self.getpixel(row, col)
                        new_image.append(p)

                image = Image.new("RGBA", (head_width, head_height))
                image.putdata(new_image)
                image.save(f"{fname_prefix}{head_y:02}.{head_x:02}.png")


def getargs():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input-file", help="input sprite file")
    ap.add_argument("-o", "--output-file", help="output sprite file prefix")
    return ap.parse_args()


def main():
    args = getargs()
    c = Chopper(args.input_file, 5, 9)
    head_width = c.guess_left_start(130)
    head_height = c.calculate_head_height(130, 3)
    c.save_heads(head_width, head_height)


if __name__ == "__main__":
    main()
