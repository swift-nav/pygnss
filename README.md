# GNSS

`GNSS` is a Python library which which provides various GNSS related utilites. `GNSS` runs on both Python 2 and 3. The coordinate system transformations are implemented based on the algorithms used by `libswiftnav`.


## Installation 

It is recommended to install `gnss` in a virtualenv to avoid polluting global system state.

To install the latest version of `gnss` from git:

` $ pip install 'git+https://github.com/swift-nav/python-gnss.git'`


## Usage

Currently, `gnss` provides functions for the following coordinate transformations:
* ecef2llh
* llh2ecef
* ecef2ned
* ecef2azel


## License

Copyright (C) 2017 Swift Navigation Inc.

Contact: Swift Navigation <dev@swiftnav.com>

This source is subject to the license found in the file 'LICENSE' which must
be be distributed together with this source. All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
