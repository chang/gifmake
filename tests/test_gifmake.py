#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `gifmake` package."""

import pytest

from click.testing import CliRunner

from gifmake import gifmake
from gifmake import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'gifmake.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_order_images_numerically():
    image_list = ['1.png', '100.png', '2.png']
    assert ['1.png', '2.png', '100.png'] == gifmake.order_images(image_list)
