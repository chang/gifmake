"""A simple command-line utility for creating GIFs from directories of images."""
# -*- coding: utf-8 -*-

import os
import re
import subprocess

import click
import imageio
from gifmake.util import check_gifsicle_installation
from skimage.transform import resize
from tqdm import tqdm


class ImageIO(object):
    """Handles image reading and GIF writing.

    Attributes
    ----------
        directory : str
            Path to the directory containing images to be converted into a GIF.
        name : str
            Name of the output GIF.
        duration : int
            Duration of the GIF in seconds. Set either duration or fps.
        fps : int
            Frames Per Second.
        verbose : int
            Set to 0 to suppress verbose execution.
    """

    VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg']

    def __init__(self, directory, name=None, duration=None, fps=None, verbose=1):
        self.directory = directory
        self.name = name
        self.duration = duration
        self.fps = fps
        self.verbose = verbose
        self._images = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is None:
            _, dirname = os.path.split(self.directory)
            name = dirname

        _, ext = os.path.splitext(name)
        if ext and not ext == '.gif':
            raise ValueError('{ext} is invalid'.format(ext=ext))
        if not name.endswith('.gif'):
            name = '{name}.gif'.format(name=name)

        self._name = name

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, directory):
        if not os.path.isdir(directory):
            raise ValueError('{} is not a valid directory.'.format(directory))
        self._directory = directory

    @property
    def file_path(self):
        return os.path.join(self._directory, self._name)

    def list_images(self, verbose=True):
        """List all images in a directory.

        Parameters
        ----------
            verbose : bool
                If True, execute verbosely.

        Returns
        -------
            image_list : list of str
        """
        image_list = [os.path.join(self.directory, f) for f in os.listdir(self.directory)]

        invalid_images = [x for x in image_list if os.path.splitext(x)[1] not in self.VALID_EXTENSIONS]
        image_list = [x for x in image_list if x not in invalid_images]
        if not image_list:
            raise ValueError('No images found in directory: {}'.format(self.directory))

        if verbose:
            size = self._estimate_size(image_list)
            msg = ['',
                   'Found {n} images. Size: {size}MB'.format(n=len(image_list), size=size),
                   'Skipping {n} non-image files...'.format(n=len(invalid_images)),
                   '\n'.join(invalid_images),
                   '']
            print('\n'.join(msg))

        image_list = self.order_images(image_list)
        return image_list

    @staticmethod
    def order_images(image_list):
        """Order image files numerically, instead of lexographically.

        Parameters
        ----------
        image_list : list of str

        Returns
        -------
        ordered_image_list : list of str
        """
        ordered_image_list = []
        for image in image_list:
            matches = re.findall('[0-9]+', image)
            if len(matches) > 1:
                raise ValueError('File name numbering {file} is ambiguous.'.format(file=image))
            ordered_image_list.append((int(matches[0]), image))
        ordered_image_list = sorted(ordered_image_list)
        return [im for (_, im) in ordered_image_list]

    def _estimate_size(self, image_list):
        """Return estimated size in MB of all items in a list."""
        BYTES_IN_MB = 1024 * 1024
        total_bytes = sum([os.stat(x).st_size for x in image_list])
        return round(total_bytes / BYTES_IN_MB, 2)

    def read_images(self, image_list):
        """Read and return image data as a list of arrays."""
        print('Reading images...')
        images = []
        for image_path in tqdm(image_list):
            im = imageio.imread(image_path)
            images.append(im)
        self._images = images

    def process_images(self, processor):
        self._images = processor.process_images(images=self._images)

    def _get_fps(self, images):
        if self.fps:
            fps = self.fps
        elif self.duration:
            fps = round(len(images) / self.duration)
        else:
            fps = 30
        return fps

    def create_gif(self):
        self._verbose_print('Writing...')
        fps = self._get_fps(self._images)

        with imageio.get_writer(self.file_path, mode='I', fps=fps) as writer:
            for image in tqdm(self._images):
                writer.append_data(image)
        writer.close()
        self._verbose_print('GIF written to: {file_path}'.format(file_path=self.file_path))

    def optimize_gifsicle(self):
        """Call gifsicle's --optimize function on the output image."""
        print('Optimizing using gifsicle...')
        cmd = 'gifsicle --optimize {file_path} --colors 256 -o {file_path}'.format(file_path=self.file_path)
        with open(os.devnull, 'w') as devnull:
            subprocess.run(cmd, shell=True, stdout=devnull, stderr=devnull)

    def _verbose_print(self, msg):
        if self.verbose > 0:
            print(msg)


class ImageProcessor:
    """Base class for handling image processing.

    All image preprocessing steps should be implemented as methods and included in
    ImageProcessor.process(). ImageIO will then call process() on each image.
    """
    def process(self):
        raise NotImplementedError

    def process_images(self, images):
        processed = []
        print('Processing images...')
        for im in tqdm(images):
            processed.append(self.process(im))
        return processed


class SkimageProcessor(ImageProcessor):
    """Image processing with scikit-image.

    Attributes
    ----------
    max_size : int
        The maximum width or height in pixels of the output GIF.

    TODO: Consider using lycon for speed.
    """
    def __init__(self, max_size):
        self.max_size = max_size

    def downsize(self, img):
        if self.max_size:
            max_size = max(img.shape)
            if max_size > self.max_size:
                scale = self.max_size / max_size
                x, y, _ = img.shape
                shape = (round(x * scale), round(y * scale))
                img = resize(img, shape, mode='reflect')
        return img

    def png_to_jpg(self, img):
        _, _, channels = img.shape
        if channels == 4:
            img = img[:, :, 0:3]
        return img

    def process(self, img):
        img = self.downsize(img)
        img = self.png_to_jpg(img)
        return img


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
    """A command line utility to create GIFs from directories of images.

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
