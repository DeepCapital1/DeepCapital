# Contributing to Crypto Sentiment Analyzer

We love your input! We want to make contributing to Crypto Sentiment Analyzer as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the docs/ folder with any new documentation or changes to existing docs.
3. The PR will be merged once you have the sign-off of at least one other developer.

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/DeepCapital1/DeepCapital/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/DeepCapital1/DeepCapital/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Code Style

* Use [Black](https://github.com/psf/black) for Python code formatting
* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
* Use type hints for function parameters and return values
* Maximum line length is 100 characters
* Write docstrings for all public methods and classes

## Testing

* Write unit tests for all new code
* Use pytest for testing
* Maintain test coverage above 80%
* Run tests before submitting PR: `python -m pytest`

## Documentation

* Update documentation for any changed functionality
* Follow Google style for docstrings
* Keep API documentation up to date
* Include docstring examples where appropriate

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/DeepCapital1/DeepCapital.git
cd DeepCapital
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

3. Install development dependencies
```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks
```bash
pre-commit install
```

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## References

* [General GitHub documentation](https://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/articles/about-pull-requests/)
* [Python Testing with pytest](https://docs.pytest.org/en/latest/)
* [Black Code Style](https://black.readthedocs.io/en/stable/)
* [Type Hints in Python](https://docs.python.org/3/library/typing.html)

## Questions?

Feel free to contact the project maintainers if you have any questions or need help getting started. 