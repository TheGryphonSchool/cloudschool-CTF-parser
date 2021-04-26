# cloudschool-CTF-parser
Fix formatting in Common Transfer Files before importing into CloudSchool 
(or other LMS)

## Usage
To *use* the parser, you must have python installed on your machine. To run it:
1. Download the file `parse_CTFs.py`
2. *Optional step*:  By default, parsed CTFs are saved in one of 3* 
   sub-folders under 'T:/CMIS/CTF Files/'. But this parent output folder is 
   configurable. To configure it, download the file `CTF_parser_config.json` 
   and update the value of the `destinationParentDir` property. Save the 
   result in the same folder as `parse_CTFs.py`.
3. Double-click `parse_CTFs.py` to execute it.

\* The three sub-folders in which parsed CTFs are saved are:
* `CTF_Year07_2020_2021` for incoming year-7s
* `CTF_Year12_2020_2021` for incoming year-12s
* `CTF_In` for all other imports

Clearly the cohort years will be inferred automatically. If the required output 
  folder for a CTD does not exist, it will be created. 

## Contributing
### Install pipenv
Python's Pipenv package manager is used to manage dependancies. Getting in 
a position to use it is slightly different between Windows and Unix:
#### Unix
1. Install pyenv [following these instructions](https://github.com/pyenv/pyenv#installation)
2. Install Pipenv [following these instructions](https://pypi.org/project/pipenv/)
#### Windows
1. On Windows you'll first need an [installation of Python](https://www.python.org/downloads/), version 2.7.9+ or 3.4+.
2. Install pyenv-win [following these instructions](https://github.com/pyenv-win/pyenv-win#installation)
3. In Powershell run `pip install pipenv`

### Git Clone
Use HTTPS (or SSH if you prefer) to clone this repository.

### pipenv virtual environment
#### Unix
1. Install pyenv [following these instructions](https://github.com/pyenv/pyenv#installation)
2. In you terminal: `pipenv install`
3. Optionally use `pipenv shell` to send commands in this shell session to the
   virtual environment.
#### Windows
1. Install pyenv-win [following these instructions](https://github.com/)
2. In you terminal, try: `pipenv install`. Depending on your installation 
   you may have to use `py -m pipenv install` or `python -m pipenv install`
   instead.
3. Optionally use `pipenv shell` (or `py -m pipenv shell`, etc) to send
   commands in this shell session to the virtual environment.
