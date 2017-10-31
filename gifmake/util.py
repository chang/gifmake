#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import warnings


def gifsicle_installed():
    """Returns boolean indicating if gifsicle is available as a shell command"""
    with open(os.devnull, 'w') as devnull:
        out = subprocess.run('gifsicle', shell=True, stdout=devnull, stderr=devnull)

    if out.returncode == 127:
        return False
    elif out.returncode == 1:
        return True
    else:
        print('Unknown gifsicle return code: {}'.format(out.returncode))


def check_gifsicle_installation():
    installed = gifsicle_installed()
    if not installed:
        msg = ['No gifsicle installation found.',
               '',
               'Installing gifsicle is highly recommended, as without compression,',
               'GIFs can become very large. Install using your package manager: https://www.lcdf.org/gifsicle/',
               '']
        msg = '\n'.join(msg)
        warnings.warn(msg, UserWarning)
    return installed
