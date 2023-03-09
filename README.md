# jogi - Just Oracle Git Integration

![github actions](https://github.com/slavong/jogi/actions/workflows/python-app.yml/badge.svg)

This project provides integration between Oracle Database and `git` using a repository with .

- Why "just"?

*Well, it can mean "only", but also "fair" if used as an adjective.*

- How to pronounce it?

*As German name "Jogi" (yogi)*

- Why not "yogi"?

*Because "y" is often interchanged with "z" on some international keyboards. 
And try to type "jogi", it is quite easy, isn't it? Just type "jo", move one left, and you get "gi" ;)*

# Oracle Database

Which versions are supported?

*Version 19c and above. Version 19c is used for development at the moment 
and it is assumed that newer versions of the Oracle Database are backward compatible.*
*No explicit tests are done for newer versions, but feel free to contribute.*

# Development

## Requirements

Following tools should be installed:
* python 3.10+
* poetry
* docker

## Initial Setup

1.  Start local Oracle database inside a docker container

`docker-compose up`

*NOTE: oracle-ee is a very large image, it can take minutes to download it, depending on your network bandwidth*

2. Create virtual environment and activate it

```bash
python -m venv
./venv/bin/activate
```

*NOTE: the `activate` command might need to be adjusted based on your operating system*

3. Install required packages

```bash
poetry install --with=dev
```

or if you have already run `install` before

```bash
poetry update --with=dev
```

4. Run the application 

```bash
./venv/bin/activate
python src/jogi/main.py
```

5. Run the tests

```bash
./venv/bin/activate
poetry update --with=tests
python -m pytest tests
```

6. Make sure `nox` runs without any issues

7. Contribute

[//]: # (TODO dummy)
