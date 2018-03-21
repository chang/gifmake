import os

import click

from gifmake.image_processor import ImageIO, SkimageProcessor
from gifmake.util import check_gifsicle_installation


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('directory', type=click.Path(exists=True), nargs=1)
@click.option('-n', '--name', type=str, help='The name of the output file.')
@click.option('--max-size', type=int, default=None,
              help='The maximum length in pixels of the longest edge.')
@click.option('--fps', type=int, help='Frames per second for the GIF. Specify either a duration or an fps.')
@click.option('--d', '--duration', type=int,
              help='Time in seconds for the duration of the GIF. Specify either a duration or an fps.')
@click.option('--optimize', type=bool, default=True,
              help='If True, use gifsicle to compress the output.')
@click.option('--verbose', type=bool, default=True)
def cli(directory, name, max_size, fps, duration, optimize, verbose):
    """A command line utility for creating GIFs from directories of images.

    Ex: gifmake /directory_of_images --max-size 600 --fps 30
    """
    full_dir_path = os.path.realpath(directory)

    if duration and fps:
        raise ValueError('Cannot specify both a duration and an FPS.')
    if optimize:
        check_gifsicle_installation()

    # read images
    io = ImageIO(directory=full_dir_path, name=name, duration=duration, fps=fps)
    image_list = io.list_images(verbose=verbose)
    io.read_images(image_list=image_list)

    # process images
    processor = SkimageProcessor(max_size=max_size)
    io.process_images(processor=processor)

    # create gif and optimize with gifsicle
    io.create_gif()
    if optimize:
        io.optimize_gifsicle()


if __name__ == "__main__":
    cli()
