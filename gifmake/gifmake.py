# -*- coding: utf-8 -*-

import re
import os
import imageio
from tqdm import tqdm
from argparse import ArgumentParser

VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg']


def list_images(directory):
    """Lists all images in a directory"""
    if not os.path.isdir(directory):
        raise ValueError('{directory} is not a valid directory.'.format(directory=directory))
    image_list = [os.path.join(directory, f) for f in os.listdir(directory)]
    image_list = filter(lambda x: os.path.splitext(x)[1] in VALID_EXTENSIONS, image_list)
    image_list = order_images(image_list)
    return image_list


def order_images(image_list):
    """Orders image files numerically instead of lexographically"""
    numbered_imgs = []
    for image in image_list:
        matches = re.findall('[0-9]+', image)
        if len(matches) > 1:
            raise ValueError('File name numbering {file} is ambiguous.'.format(file=image))
        numbered_imgs.append((int(matches[0]), image))
    numbered_imgs = sorted(numbered_imgs)
    return [im for (_, im) in numbered_imgs]


def create_gif(image_list, directory):
    _, dirname = os.path.split(directory)
    file_path = os.path.join(directory, '{dirname}.gif'.format(dirname=dirname))

    print('Reading...')
    images = []
    for image_path in tqdm(image_list):
        im = imageio.imread(image_path)
        images.append(im)

    print('Writing...')
    with imageio.get_writer(file_path, mode='I', fps=30) as writer:
        for image in tqdm(images):
            writer.append_data(image)
    writer.close()


def main(directory, **kwargs):
    image_list = list_images(directory)
    create_gif(image_list=image_list, directory=directory)


if __name__ == "__main__":
    parser = ArgumentParser(description='Creates a .gif from a directory of images')
    parser.add_argument('directory', type=str, help='Directory containing the images')
    parser.add_argument('--name', type=str, help='Name of the output .gif')
    parser.add_argument(
        '--duration', type=int, default=None,
        help='Time in seconds for the duration of the .gif. Specify only a duration or an fps.'
    )
    parser.add_argument(
        '--fps', type=int, default=None,
        help='Frames per second for the .gif. Specify only a duration or an fps.'
    )
    kwargs = vars(parser.parse_args())

    if kwargs['duration'] and kwargs['fps']:
        raise ValueError('Cannot specify both --duration and --fps.')

    main(**kwargs)
