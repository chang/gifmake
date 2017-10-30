# -*- coding: utf-8 -*-

"""Console script for gifmake."""

import os
import click
from .gifmake import ImageIO, ImageProcessor


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--name', type=str, help='The name of the output file.')
@click.option('--max-size', type=int, default=600,
              help='The maximum length in pixels of the longest edge.')
@click.option('--fps', type=int, help='Frames per second for the GIF.')
@click.option('--duration', help='Time in seconds for the duration of the .gif. Specify only a duration or an fps.')
@click.option('--verbose', type=bool)
def main(directory, name, max_size, fps, duration, verbose):
    """A command line application to create GIFs from directories of images."""
    full_dir_path = os.path.realpath(directory)

    # read images
    io = ImageIO(directory=full_dir_path, name=name)
    image_list = io.list_images(verbose=verbose)
    images = io.read_images(image_list=image_list)

    # process images
    processor = ImageProcessor(max_size=max_size)
    processed_images = processor.process_images(images=images)

    # create name and write
    io.create_gif(images=processed_images)

    # optimize with gifsicle
    io.optimize_gifsicle()


if __name__ == "__main__":
    main()
