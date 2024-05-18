import time
import os
from PIL import Image, ImageFilter

from concurrent.futures import ProcessPoolExecutor

filenames = [
    'd:/openai_book/chap05/images/img01.jpg',
    'd:/openai_book/chap05/images/img02.jpg',
    'd:/openai_book/chap05/images/img03.jpg',
    'd:/openai_book/chap05/images/img04.jpg',
    'd:/openai_book/chap05/images/img05.jpg',
    'd:/openai_book/chap05/images/img06.jpg'
]


def create_thumbnail(filename, size=(50, 50), thumb_dir='d:/openai_book/chap05/thumbs'):
    pass


if __name__ == '__main__':
    start = time.perf_counter()

    with ProcessPoolExecutor() as executor:
        executor.map(create_thumbnail, filenames)

    elapsed = time.perf_counter() - start

    print(f"elapsed: {elapsed:.2f} sec")
