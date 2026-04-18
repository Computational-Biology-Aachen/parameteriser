# Parameteriser

[![pipeline status](https://gitlab.com/marvin.vanaalst/parameteriser/badges/main/pipeline.svg)](https://gitlab.com/marvin.vanaalst/parameteriser/-/commits/main)
[![coverage report](https://gitlab.com/marvin.vanaalst/parameteriser/badges/main/coverage.svg)](https://gitlab.com/marvin.vanaalst/parameteriser/-/commits/main)
[![Documentation](https://img.shields.io/badge/Documentation-Gitlab-success)](https://marvin.vanaalst.gitlab.io/parameteriser/)
[![PyPi](https://img.shields.io/pypi/v/parameteriser)](https://pypi.org/project/parameteriser/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Downloads](https://pepy.tech/badge/parameteriser)](https://pepy.tech/project/parameteriser)


## Installation

### Basic

If you just want to interface the brenda database, you can use [uv](https://astral.sh/blog/uv)

`uv sync` or `uv sync --extra dev` if you also want to install e.g. jupyter notebook.

Then choose the resulting virtual environment in `.venv/bin/python`


### Full

**This is currently broken due to a numpy 1 / 2 version mismatch**

If you also want to enable experimental features, such as interfacing the [deepmolecules package](), use [pixi](https://pixi.sh/latest/).

`pixi install`

The choose the resulting virtual environment in `.pixi/envs/default/bin/python`


## License

[GPL 3](https://gitlab.com/marvin.vanaalst/parameteriser/blob/main/LICENSE)

## Documentation

The official documentation is hosted [here on gitlab](https://marvin.vanaalst.gitlab.io/parameteriser/).

## Issues and support

If you experience issues using the software please contact us through our [issues](gitlab.com/marvin.vanaalst/parameteriser/issues) page.

## Contributing

All contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome. See our [contribution guide](gitlab.com/marvin.vanaalst/parameteriser/blob/main/CONTRIBUTING.md) for more information.

## Tool family 🏠

`Parameteriser` is part of a larger family of tools that are designed with a similar set of abstractions. Check them out!

- [MxlPy](https://github.com/Computational-Biology-Aachen/MxlPy) is a Python package for mechanistic learning (Mxl)
- [MxlBricks](https://github.com/Computational-Biology-Aachen/mxl-bricks) is built on top of `MxlPy` to build mechanistic models composed of pre-defined reactions (bricks)
- [MxlModels](https://github.com/Computational-Biology-Aachen/mxl-models) supplies flat, single-file versions of MxlBricks models for easy inspection
- [MxlWeb](https://github.com/Computational-Biology-Aachen/mxl-web) brings simulation of mechanistic models to the browser!
- [pysbml](https://github.com/Computational-Biology-Aachen/pysbml) simplifies SBML models for import/export with MxlPy
