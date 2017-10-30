# -*- coding: utf-8 -*-

import os
import re
import subprocess
from abc import ABC, abstractmethod

import click
import imageio


from skimage.transform import resize
from tqdm import tqdm

VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg']


class ImageIO(object):
    def __init__(self, directory, name=None, duration=None, fps=None):
        self.directory = directory
        self.name = name
        self.duration = duration
        self.fps = fps
        self._images = None

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

    def list_images(self, verbose=True):
        """Lists all images in a directory"""
        image_list = [os.path.join(self.directory, f) for f in os.listdir(self.directory)]

        invalid_images = [x for x in image_list if os.path.splitext(x)[1] not in VALID_EXTENSIONS]
        image_list = [x for x in image_list if x not in invalid_images]
        if not image_list:
            raise ValueError('No images found in directory: {}'.format(self.directory))

        if verbose:
            size = self._estimate_size(image_list)
            msg = ['',
                   'Found {n} images. Size: {size}MB'.format(n=len(image_list), size=size),
                   'Excluding {n} non-image files:'.format(n=len(invalid_images)),
                   '\n'.join(invalid_images),
                   '']
            print('\n'.join(msg))

        image_list = self.order_images(image_list)
        return image_list

    def order_images(self, image_list):
        """Orders image files numerically instead of lexographically"""
        numbered_imgs = []
        for image in image_list:
            matches = re.findall('[0-9]+', image)
            if len(matches) > 1:
                raise ValueError('File name numbering {file} is ambiguous.'.format(file=image))
            numbered_imgs.append((int(matches[0]), image))
        numbered_imgs = sorted(numbered_imgs)
        return [im for (_, im) in numbered_imgs]

    def _estimate_size(self, image_list):
        """Returns estimated size in MB of all items in a list"""
        bytes_in_mb = 1024 * 1024
        total_bytes = sum([os.stat(x).st_size for x in image_list])
        return round(total_bytes / bytes_in_mb, 2)

    def read_images(self, image_list):
        """Reads and returns image data as a list of arrays"""
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
        print('Writing...')
        file_path = os.path.join(self.directory, self.name)
        fps = self._get_fps(self._images)

        with imageio.get_writer(file_path, mode='I', fps=fps) as writer:
            for image in tqdm(self._images):
                writer.append_data(image)
        writer.close()
        print('GIF written to: {file_path}'.format(file_path=file_path))

    def optimize_gifsicle(self):
        file_path = os.path.join(self.directory, self.name)
        print('Optimizing using gifsicle...')
        cmd = 'gifsicle --optimize {file_path} --colors 256 -o {file_path}'.format(file_path=file_path)
        subprocess.run(cmd, shell=True)


class AbstractImageProcessor(ABC):
    @abstractmethod
    def process(self):
        pass

    def process_images(self, images):
        processed = []
        print('Processing images...')
        for im in tqdm(images):
            processed.append(self.process(im))
        return processed


class SkimageProcessor(AbstractImageProcessor):
    def __init__(self, max_size=500):
        self.max_size = max_size

    def downsize(self, img):
        x, y, _ = img.shape
        max_size = max(img.shape)
        if max_size > self.max_size:
            scale = self.max_size / max_size
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


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--name', type=str, help='The name of the output file.')
@click.option('--max-size', type=int, default=600,
              help='The maximum length in pixels of the longest edge.')
@click.option('--fps', type=int, help='Frames per second for the GIF. Specify either a duration or an fps.')
@click.option('--duration', type=int,
              help='Time in seconds for the duration of the .gif. Specify either a duration or an fps.')
@click.option('--optimize', type=bool, default=True,
              help='If True, use gifsicle to compress the output.')
@click.option('--verbose', type=bool, default=True)
def cli(directory, name, max_size, fps, duration, optimize, verbose):
    """A command line application to create GIFs from directories of images."""
    full_dir_path = os.path.realpath(directory)

    if duration and fps:
        raise ValueError('Cannot specify both a duration and an FPS.')

    # read images
    io = ImageIO(directory=full_dir_path, name=name, duration=duration, fps=fps)
    image_list = io.list_images(verbose=verbose)
    io.read_images(image_list=image_list)

    # process images
    processor = SkimageProcessor(max_size=max_size)
    io.process_images(processor=processor)

    # create name and write
    io.create_gif()

    # optimize with gifsicle
    if optimize:
        io.optimize_gifsicle()


if __name__ == "__main__":
    cli()
