import os
import shutil
import sys

# Resolve gifmake source path.
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gifmake')
sys.path = [src_path] + sys.path
print(sys.path)

from click.testing import CliRunner
from image_processor import ImageIO
from cli import cli

import pytest


@pytest.fixture(scope='module')
def sample_files():
    return ['1.png', '10.png', '2.png', '100.png']


@pytest.fixture(scope='module')
def image_directory(sample_files):
    """Creates a temporary test .env file in the base directory."""
    dirname = 'gifmake_pytest_dir'
    assert not os.path.exists(dirname)

    # create directory and populate with files
    os.mkdir(dirname)
    for file in sample_files:
        with open(os.path.join(dirname, file), 'w') as fp:
            fp.write('')

    yield dirname

    # teardown
    shutil.rmtree(dirname)


@pytest.fixture(scope='module')
def empty_directory():
    dirname = 'gifmake_pytest_empty_dir'
    assert not os.path.exists(dirname)

    os.mkdir(dirname)
    yield dirname
    shutil.rmtree(dirname)


@pytest.fixture(scope='module')
def large_image_directory():
    """Creates a temporary test .env file in the base directory."""
    dirname = 'gifmake_pytest_large_dir'
    assert not os.path.exists(dirname)

    # create directory and populate with files
    os.mkdir(dirname)
    files = ['{}.png'.format(i) for i in range(200)]
    for file in files:
        with open(os.path.join(dirname, file), 'w') as fp:
            fp.write('')

    yield dirname

    # teardown
    shutil.rmtree(dirname)


def test_command_line_interface(image_directory):
    """Test the CLI."""
    runner = CliRunner()

    result = runner.invoke(cli)
    assert result.exit_code == 2, 'Should fail if no directory argument is provided'

    result = runner.invoke(cli, ['test'])
    assert result.exit_code == 2, 'Should fail if invalid directory path is provided'

    # result = runner.invoke(cli, [dirname])
    # assert result.exit_code == 0, 'Should exit with error code 0 when called with valid path'

    help_result = runner.invoke(cli, ['--help'])
    assert help_result.exit_code == 0


def test_set_name(image_directory):
    io = ImageIO(directory=image_directory, name=None)
    assert io.name == image_directory + '.gif', 'When called with no name, use directory name as output file name'

    io = ImageIO(directory=image_directory, name='test')
    assert 'test.gif' == io.name, 'Should automatically append .gif to a filename'

    with pytest.raises(ValueError):
        # should raise ValueError if non .gif extension is passed
        io = ImageIO(directory=image_directory, name='test.blah')


def test_order_images(sample_files, image_directory):
    io = ImageIO(directory=image_directory)
    assert ['1.png', '2.png', '10.png', '100.png'] == io.order_images(sample_files)

    with pytest.raises(ValueError):
        # throw an error if numbering is ambiguous
        io.order_images(['test_00_11.png'])


def test_list_images(image_directory, sample_files):
    io = ImageIO(directory=image_directory)
    sample_files = [os.path.join(image_directory, f) for f in sample_files]
    listed_files = io.list_images()
    assert sorted(sample_files) == sorted(listed_files)


def test_list_images_empty_directory(empty_directory):
    io = ImageIO(directory=empty_directory)
    with pytest.raises(ValueError):
        io.list_images()


def test_get_fps(large_image_directory):
    io = ImageIO(directory=large_image_directory, duration=5)
    assert 40 == io._get_fps(io.list_images())
