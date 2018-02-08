## gifmake

[![Build Status](https://travis-ci.org/ericchang00/gifmake.svg?branch=master)](https://travis-ci.org/ericchang00/gifmake)

A simple command line utility for creating GIFs from directories of images.


![](https://github.com/ericchang00/gifmake/raw/master/img/demo.gif)

### Installation

```bash
pip install gifmake
```

Installing [gifsicle](https://www.lcdf.org/gifsicle/) is highly recommended, as output GIFs tend to be very large without compression. If on Mac using homebrew, run `brew install gifsicle`.

### Example

Running `gifmake` will discover numbered images in a directory and write them into a GIF. You can set the speed of the GIF using the `--fps` and `--duration` options.

```bash
gifmake /sample  # create a GIF called sample.gif from all image files in /sample

gifmake /sample --name output.gif --fps 30  # write to output.gif and stitch images at 30fps

gifmake /sample -n output.gif --duration 3  # set duration of GIF to 3 seconds
```
