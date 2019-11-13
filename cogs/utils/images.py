import numpy as np
import random

from PIL import Image
from math import ceil
from loguru import logger


async def get_random_image(x: int = 800, y: int = 500):
    discord_gray = "#2C2F33"  # 44, 47, 51
    array = np.zeros([y, x, 3], dtype=np.uint8)
    array[:, :] = [181, 47, 51]
    img = Image.fromarray(array)
    return img


async def get_random_image2(x: int = 800, y: int = 500):
    x_array = np.linspace(0.0, 1.0, x).reshape((1, x, 1))
    y_array = np.linspace(0.0, 1.0, y).reshape((y, 1, 1))

    def rand_color():
        return np.array([random.random(), random.random(), random.random()]).reshape((1, 1, 3))

    def get_x(): return x_array
    def get_y(): return y_array

    def safe_divide(a, b):
        return np.divide(a, np.maximum(b, 0.001))

    functions = [(0, rand_color),
                 (0, get_x),
                 (0, get_y),
                 (1, np.sin),
                 (1, np.cos),
                 (2, np.add),
                 (2, np.subtract),
                 (2, np.multiply),
                 (2, safe_divide),
                 ]

    min_depth = 2
    max_depth = 10

    def build_image(depth=0):
        funcs = [f for f in functions if
                 (f[0] > 0 and depth < max_depth) or
                 (f[0] == 0 and depth >= min_depth)]
        n_args, func = random.choice(funcs)
        args = [build_image(depth + 1) for n in range(n_args)]
        return func(*args)

    img = build_image()
    # img = np.tile(img, (ceil(x / img.shape[0]), ceil(y / img.shape[1]), ceil(3 / img.shape[2])))
    img_8bit = np.uint8(np.rint(img.clip(0.0, 1.0) * 255.0))
    return Image.fromarray(img_8bit)
