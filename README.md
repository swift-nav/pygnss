# PyGNSS

[![Build Status](https://travis-ci.org/swift-nav/pygnss.svg?branch=master)](https://travis-ci.org/swift-nav/pygnss)

`PyGNSS` is a Python library which which provides various GNSS related utilites.  The coordinate system transformations are implemented based on the algorithms used by `libswiftnav`.

## Installation

It is recommended to install `pygnss` in a virtualenv to avoid polluting global system state.

To install the latest version of `pygnss` from git:

`$ pip install 'git+https://github.com/swift-nav/pygnss.git'`

## Usage

Currently, `pygnss` provides functions for the following coordinate transformations:

* `llh_from_ecef`
* `ecef_from_llh`
* `ned_from_ecef`
* `azimuth_elevation_from_ecef`

## License

Copyright (C) 2017 Swift Navigation Inc.

Contact: Swift Navigation <dev@swiftnav.com>

This source is subject to the license found in the file 'LICENSE' which must
be be distributed together with this source. All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
