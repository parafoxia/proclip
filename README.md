# Proclip

[![PyPi version](https://img.shields.io/pypi/v/proclip.svg)](https://pypi.python.org/pypi/proclip/)
[![PyPI - Status](https://img.shields.io/pypi/status/proclip)](https://pypi.python.org/pypi/proclip/)
[![Downloads](https://pepy.tech/badge/proclip)](https://pepy.tech/project/proclip)
[![GitHub last commit](https://img.shields.io/github/last-commit/parafoxia/proclip)](https://github.com/parafoxia/proclip)
[![License](https://img.shields.io/github/license/parafoxia/proclip.svg)](https://github.com/parafoxia/proclip/blob/main/LICENSE)

<!-- [![CI](https://github.com/parafoxia/proclip/actions/workflows/ci.yml/badge.svg)](https://github.com/parafoxia/proclip/actions/workflows/ci.yml)
[![Read the Docs](https://img.shields.io/readthedocs/proclip)](https://proclip.readthedocs.io/en/latest/index.html)
[![Maintainability](https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/maintainability)](https://codeclimate.com/github/parafoxia/proclip/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/test_coverage)](https://codeclimate.com/github/parafoxia/proclip/test_coverage) -->

A powerful templating tool for your projects.

CPython versions 3.7 through 3.11-dev and PyPy versions 3.7 through 3.9 are officially supported.

Windows, MacOS, and Linux are all supported.

## Installation

To install the latest stable version of Proclip, use the following command:
```sh
pip install proclip
```

You can also install the latest development version using the following command:
```sh
pip install git+https://github.com/parafoxia/proclip
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration.

## Creating clips

You can create clips using the following command:

```sh
clip new <name> <file> [-o output-dir]
```

Use `clip new --help` for more information on what each option does.

To create a clip, first create a file, and code it how you want it to look.
You can also include variables that Proclip can replace when you paste the clip.
Variables use a slightly modified Jinja syntax, which additionally allows for default values to be provided.

Take the following example:

```py
class {{ cls = MyClass }}:
    def __init__(self, n: int) -> None:
        self.{{ attr }} = n

    @property
    def number(self) -> int:
        return self.{{ attr }}

if __name__ == "__main__":
    c = {{ cls }}(5)
    print(c.number)
```

In this example, you have two distinct variables: `cls`, and `attr`.
`cls` has a default value (`MyClass`), so when you paste the clip, that value will be used if you don't supply one.
Note that only the first instance of `cls` needs a default value.
Keep in mind that only one default value can be assigned per variable; others will be overwritten.

## Pasting clips

You can paste clips using the following command:

```sh
clip paste <name> [-i input-dir] [-o output] [-v variables]
```

Use `clip paste --help` for more information on what each option does.

You can use the `-v` flag to insert values for variables when pasting.
Variables that were not assigned default values when the clip was created need a value supplied to them.
Default values can be overridden if you choose to do so.

Variables are passed as strings, where a value needs to be assigned to a key (for example, `key=value`).
You can use commas to separate multiple variable assignments (`key1=value1,key2=value2`).
In the above example, passing `-v "attr=n"` produces the following file:

```py
class MyClass:
    def __init__(self, n: int) -> None:
        self.n = n

    @property
    def number(self) -> int:
        return self.n

if __name__ == "__main__":
    c = MyClass(5)
    print(c.number)
```

## Contributing

Contributions are very much welcome! To get started:

* Familiarise yourself with the [code of conduct](https://github.com/parafoxia/proclip/blob/main/CODE_OF_CONDUCT.md)
* Have a look at the [contributing guide](https://github.com/parafoxia/proclip/blob/main/CONTRIBUTING.md)

## License

The Proclip module for Python is licensed under the [BSD 3-Clause License](https://github.com/parafoxia/proclip/blob/main/LICENSE).
