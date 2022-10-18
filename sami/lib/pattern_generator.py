# -*- coding: utf-8 -*-
"""
Original file is located at
    https://colab.research.google.com/drive/1g70UPa40Gdh8vPqUFlGv1YsTUl0FHCp5
"""

import random
from typing import List, Tuple

import numpy as np
from PIL.Image import Image, fromarray
from PIL.Image import new as new_image
from PIL.ImageDraw import Draw, ImageDraw
from shapely.affinity import rotate as rt
from shapely.geometry import Polygon
from skimage.transform import rotate


def convert_hex_to_rgb(hx: str) -> Tuple[int, ...]:
    """
    Takes a string with format "#FFFFFF" and converts the value
    into a proper hexadecimal value, usable for images.

    Parameters
    ----------
    hx: str
        The hexadecimal value.

    Returns
    -------
    Tuple[int, ...]
        A tuple of three integers corresponding
        respectively to the Red-Green-Blue (RGB) values.

    """
    h = hx.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def get_poly_from_two_rectangle_points(loc_a, loc_b):
    arr = np.array((loc_a, [loc_b[0], loc_a[1]], loc_b, [loc_a[0], loc_b[1]]))
    return arr


def stroke_poly(
    img: Image, draw: ImageDraw, points, color: Tuple[int, ...], width: int
):
    draw.line(points, fill=color, width=width)
    for point in points:
        draw.ellipse(
            (
                point[0] - (int(width / 2) - 1),
                point[1] - (int(width / 2) - 1),
                point[0] + (int(width / 2) - 1),
                point[1] + (int(width / 2) - 1),
            ),
            fill=color,
        )
    return draw, img


def stackarr(img: np.array, times: int, func: callable, v: int) -> callable:
    mir = []
    on = False
    for _ in range(times):
        if on:
            mir.append(img)
            on = False
        else:
            if v == 1:
                mir.append(img[::-1, ::-1, :])
            elif v == 2:
                mir.append(img[::-1, :, :])
            elif v == 3:
                mir.append(img[:, ::-1, ::])
            on = True
    return func(mir)


def get_random_points(img: Image, sides: int = 4) -> list:
    rnd = random.randint(0, 6)
    points = []
    # For each side
    for _ in range(sides):
        if rnd == 0:
            rn_x = random.randint(0, int(img.width / 2))
            rn_y = random.randint(0, int(img.height / 2))
        elif rnd == 1:
            rn_x = random.randint(int(img.width / 2), img.width)
            rn_y = random.randint(int(img.height / 2), img.height)
        elif rnd == 2:
            rn_x = random.randint(0, int(img.width / 2))
            rn_y = random.randint(int(img.height / 2), img.height)
        elif rnd == 3:
            rn_x = random.randint(int(img.width / 2), img.width)
            rn_y = random.randint(0, int(img.height / 2))
        elif rnd == 4:
            rn_x = random.randint(int(img.width * 0.05), int(img.width * 0.95))
            rn_y = random.randint(int(img.height * 0.05), int(img.height * 0.95))
        else:
            rn_x = random.randint(-int(img.width * 0.15), int(img.width * 1.15))
            rn_y = random.randint(-int(img.height * 0.15), int(img.height * 1.15))
        points.append((rn_x, rn_y))
    return points


def create_pattern(
    seed: int,
    colors: List[str],
    back_color: str = None,
    line: Tuple[str, int] = ("36382E", 3),
    wanted_size: int = 256,
    x_times: int = 10,
    y_times: int = 10,
    break_down: dict = None,
    shapes_count: int = 10,
    angles: list = np.arange(0, 180, 45),
) -> Image:
    """
    Creates an image following a process.
    Returns the Image object.

    Parameters
    ----------
    seed: int
        A seed for the random generator.
        By passing seed, the same parameters will be selected,
        and therefore the same figure shall be generated.
    colors: List[str]
        A list of hexadecimal values, corresponding to colours.
    back_color: str
        Background color, as a hexadecimal value.
    line: Tuple[str, int]
        A tuple of two elements:
            - str: Hexadecimal color of the line. e.g "#123456".
            - int: Width of the line.
    wanted_size: int
        Size of each side of a pattern, in pixels.
    x_times: int
    y_times: int
    break_down: dict
        Percentages of polygons, rectangles and circles.
    shapes_count: int
        How much unique shapes we want in the pattern.
    angles: list

    Returns
    -------
    Image
        An Image object.

    """

    random.seed(seed)

    colors = list(map(convert_hex_to_rgb, colors))
    random.shuffle(colors)

    if back_color:
        # If argument is set, convert to RGC tuple
        back_color = convert_hex_to_rgb(back_color)
    else:
        back_color = random.choice(colors)

    if not break_down:
        break_down = {"polygons": 0.4, "rectangles": 0.3, "circles": 0.3}

    line_colour = convert_hex_to_rgb(line[0])
    line_width = line[1]

    start = (int(wanted_size / x_times), int(wanted_size / y_times))

    # Create the new Image object.
    img = new_image("RGB", start, back_color)
    # and the new ImageDraw object.
    draw = Draw(img)

    for _ in range(shapes_count):
        # Chooses a random integer between 0 and 99 included.
        rnd_type = random.randint(0, 99)

        # Creates three ranges: polygons, rectangles, and circles.
        # polygons[0] = 0 and circles[-1] = 99.
        # By selecting rnd_type above, we will land in one of these three
        # ranges, defining the shape we are going to use.
        polygons = list(range(0, int(100 * break_down["polygons"])))
        rectangles = [
            x + polygons[-1] + 1
            for x in list(range(0, int(100 * break_down["rectangles"])))
        ]
        circles = [
            x + rectangles[-1] + 1
            for x in list(range(0, int(100 * break_down["circles"])))
        ]

        if rnd_type in polygons:
            polygon = Polygon(get_random_points(img, random.randint(4, 10)))
            points = polygon.convex_hull.exterior.coords
            draw, img = stroke_poly(img, draw, points, line_colour, line_width * 2)
            draw.polygon(points, fill=random.choice(colors))
        elif rnd_type in rectangles:
            polygon = Polygon(
                get_poly_from_two_rectangle_points(*get_random_points(img, 2)[:2])
            )
            polygon = rt(polygon, random.randint(10, 100))
            points = polygon.exterior.coords
            draw.rectangle(
                (points[0], points[2]),
                fill=random.choice(colors),
                outline=line_colour,
                width=line_width,
            )
        elif rnd_type in circles:
            polygon = Polygon(
                get_poly_from_two_rectangle_points(*get_random_points(img, 2)[:2])
            )
            polygon = rt(polygon, random.randint(10, 100))
            points = polygon.exterior.coords
            draw.ellipse(
                (points[0], points[2]),
                fill=random.choice(colors),
                outline=line_colour,
                width=line_width,
            )

    img = np.array(img)

    rand_h = random.randint(1, 3)
    rand_v = random.randint(1, 3)

    img = stackarr(img, x_times, np.hstack, rand_h)
    img = stackarr(img, y_times, np.vstack, rand_v)

    img = rotate(
        img.astype(np.float32), random.choice(angles), mode="wrap", resize=False
    )

    img = fromarray(img.astype(np.uint8))

    return img


if __name__ == "__main__":
    seed = random.randint(0, 9999)
    create_pattern(
        seed=seed,
        wanted_size=512,
        colors=["8d1f73", "150511", "d643b3", "FFFFFF"],
        shapes_count=10,
    ).show()
    print(seed)
