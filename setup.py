#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


requirements = [
    'click>=6.0',
    'imageio>=2.0.0',
    'numpy>=1.13.0',
    'Pillow>=4.3.0',
    'py>=1.4',
    'six>=1.0',
    'scikit-image>=0.13',
    'tqdm>=4.0',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='gifmake',
    version='0.1.1',
    description="A simple command line utility for creating GIFs with directories of images.",
    # long_description="TODO: A long description",
    author="Eric Chang",
    author_email='ericchang00@gmail.com',
    url='https://github.com/ericchang00/gifmake',
    packages=find_packages(include=['gifmake']),
    entry_points={
        'console_scripts': [
            'gifmake=gifmake.gifmake:cli'
        ]
    },
    include_package_data=True,
    python_requires=">=3.4",  # TODO: Support Python 2
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='gifmake',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
