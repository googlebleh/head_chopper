#!/usr/bin/env python3

import pprint

from PIL import Image
im = Image.open("11_0_1_face.png")

pixels = list(im.getdata())
width, height = im.size
# pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

def getpixel(row, col):
    assert(0 <= row < height)
    assert(0 <= col < width)
    return pixels[width * row + col]

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

base_row = 130
left_start = 30 # - 130
nheads = 5

calculated_head_width = None
for guess in range(190, width // nheads + 3):
    segments = []
    for head_i in range(5):
        segments.append([getpixel(base_row, left_start+(head_i*guess)+j) for j in range(100)])

    if all_almost_eq(segments):
        print(f"guessed skip = {guess}")
        calculated_head_width = guess

for head_i in range(nheads):
    new_image = []
    for row in range(height):
        for col in range(calculated_head_width):
            new_image.append(getpixel(row, head_i*calculated_head_width + col))


    image = Image.new("RGBA", (calculated_head_width, height))
    image.putdata(new_image)
    image.save(f"output-{head_i}.png")
