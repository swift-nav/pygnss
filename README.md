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
