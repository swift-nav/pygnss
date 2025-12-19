# PyGNSS

[![Build Status](https://travis-ci.org/swift-nav/pygnss.svg?branch=master)](https://travis-ci.org/swift-nav/pygnss)

`PyGNSS` is a Python library which which provides various GNSS related utilites.  The coordinate system transformations are implemented based on the algorithms used by `libswiftnav`.

## Installation

It is recommended to install `pygnss` in a virtual environment to avoid polluting global system state.

To install the latest version of `pygnss` from PyPI:

```bash
pip install swiftnav-gnss
```

To install from git:

```bash
pip install 'git+https://github.com/swift-nav/pygnss.git'
```

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management and [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and set up the development environment:

```bash
git clone https://github.com/swift-nav/pygnss.git
cd pygnss
uv pip install -e ".[dev]"
```

Run tests and checks:

```bash
# Run tests
pytest

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy gnss/ tests/
```

## Usage

Currently, `pygnss` provides functions for the following coordinate transformations:

* `llh_from_ecef`
* `ecef_from_llh`
* `ned_from_ecef`
* `azimuth_elevation_from_ecef`

## Publishing to PyPI

Tag a release:

```bash
git tag v0.5.2
git push origin v0.5.2
```

Build the package:

```bash
uv build
```

This creates wheel and source distributions in the `dist/` directory.

Publish to PyPI using `uv publish` or `twine`:

```bash
# Using uv (recommended)
uv publish

# Or using twine
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-pypi-token>
twine upload dist/*
```

## License

Copyright (C) 2017 Swift Navigation Inc.

Contact: Swift Navigation <dev@swiftnav.com>

This source is subject to the license found in the file 'LICENSE' which must
be be distributed together with this source. All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
