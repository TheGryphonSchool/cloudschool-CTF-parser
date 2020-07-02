# cloudschool-CTF-parser
Fix formatting in Common Transfer Files before importing into CloudSchool (or other CMS)

## Installation
To *use* the parser, you only need to download and use the file `parse_CTFs.py`. These instructions are for *contributing* to the project
### Install pipenv
Python's Pipenv package manager is used to manage dependancies. Getting in a position to use it is slightly different between Windows and Unix:
**Unix**
1. Install pyenv [following these instructions](https://github.com/pyenv/pyenv#installation)
2. Install Pipenv [following these instructions](https://pypi.org/project/pipenv/)
**Windows**
1. On Windows you you'll first need an [installation of Python](https://www.python.org/downloads/), version 2.7.9+ or 3.4+.
2. Install pyenv-win [following these instructions](https://github.com/pyenv-win/pyenv-win#installation)
3. In Powershell run `pip install pipenv`

### Git Clone
Use HTTP (or SSH if you prefer) to clone this remote.

### pipenv virtual environment
**Unix**
1. Install pyenv [following these instructions](https://github.com/pyenv/pyenv#installation)
2. In you terminal: `pipenv install`
3. Optionally use `pipenv shell` to send commands in this shell session to the virtual environment.
**Windows**
1. Install pyenv-win [following these instructions](https://github.com/)
2. In you terminal, try: `pipenv install`. Depending on your installation you may have to use `py -m pipenv install` or `python -m pipenv install` instead.
3. Optionally use `pipenv shell` (or `py -m pipenv shell`, etc) to send commands in this shell session to the virtual environment.
