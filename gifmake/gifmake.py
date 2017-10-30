# -*- coding: utf-8 -*-

import os
import re
import subprocess

import click
import imageio

from skimage.transform import resize
from tqdm import tqdm

VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg']


class ImageProcessor(object):
    def __init__(self, max_size=500):
        self.max_size = max_size

    def downsize(self, img):
        x, y, _ = img.shape
        max_size = max(img.shape)
        if max_size > self.max_size:
            scale = self.max_size / max_size
            shape = (round(x * scale), round(y * scale))
            img = resize(img, shape)
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

    def process_images(self, images):
        processed = []
        print('Processing images...')
        for im in tqdm(images):
            processed.append(self.process(im))
        return processed


class ImageIO(object):
    def __init__(self, directory, name=None):
        self.directory = directory
        self.name = name

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

    def list_images(self, verbose=True):
        """Lists all images in a directory"""
        if not os.path.isdir(self.directory):
            raise ValueError('{directory} is not a valid directory.'.format(directory=self.directory))
        image_list = [os.path.join(self.directory, f) for f in os.listdir(self.directory)]

        invalid_images = [x for x in image_list if os.path.splitext(x)[1] not in VALID_EXTENSIONS]
        msg = '\nExcluding {n} non-image files. '.format(n=len(invalid_images))
        if not verbose:
            msg += 'To display, set the --verbose flag.'
        else:
            msg += '\n'.join(invalid_images)
        print(msg)

        image_list = [x for x in image_list if x not in invalid_images]
        if not image_list:
            raise ValueError('No images found in directory: {}'.format(self.directory))

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

    def estimate_size(self, image_list):
        """Returns estimated size in MB of all items in a list"""
        bytes_in_mb = 1024 * 1024
        total_bytes = sum([os.stat(x).st_size for x in image_list])
        return round(total_bytes / bytes_in_mb, 2)

    def read_images(self, image_list):
        """Reads and returns image data as a list of arrays"""
        print('Total file size: {}MB. Reading...'.format(self.estimate_size(image_list)))
        images = []
        for image_path in tqdm(image_list):
            im = imageio.imread(image_path)
            images.append(im)
        return images

    def create_gif(self, images):
        print('Writing...')
        file_path = os.path.join(self.directory, self.name)
        with imageio.get_writer(file_path, mode='I', fps=30) as writer:
            for image in tqdm(images):
                writer.append_data(image)
        writer.close()
        print('GIF written to: {file_path}'.format(file_path=file_path))

    def optimize_gifsicle(self):
        file_path = os.path.join(self.directory, self.name)
        print('Optimizing using gifsicle...')
        cmd = 'gifsicle --optimize {file_path} --colors 256 -o {file_path}'.format(file_path=file_path)
        subprocess.run(cmd, shell=True)


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--name', type=str, help='The name of the output file.')
@click.option('--max-size', type=int, default=600,
              help='The maximum length in pixels of the longest edge.')
@click.option('--fps', type=int, help='Frames per second for the GIF.')
@click.option('--duration', help='Time in seconds for the duration of the .gif. Specify only a duration or an fps.')
@click.option('--optimize', type=bool, default=True,
              help='If True, use gifsicle to compress the output.')
@click.option('--verbose', type=bool)
def cli(directory, name, max_size, fps, duration, optimize, verbose):
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
    if optimize:
        io.optimize_gifsicle()


if __name__ == "__main__":
    cli()
