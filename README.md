# plynth-dev

https://www.plynth.net

Plynth is a Python/HTML/CSS GUI Framework.

Currently this repository contains the python codes for the developtment kit and examples which you can use as a reference.

<img src="https://www.plynth.net/sites/default/files/2019-10/Screen%20Shot%202019-10-02%20at%2023.44.51.png" width="400px">

<br>

# How to start development using this repository

## Prerequisites
You need to install `python` and `pipenv` on your system first in order to develop with the development kit.

* *Windows*
  * We recommend the official binaries of Python, https://www.python.org/downloads/. On Windows, you don't have to install pipenv manually.
* *Mac*
  * Installing `pipenv` by Homebrew is recommended.
* *Linux*
  * See [this page](docs/linux_prequisites.md).

#### Check commands
```sh
$ python3 -V # 3.7.x or 3.6.x
 or
$ python -V # 3.7.x or 3.6.x
```

```sh
# Mac and Linux only
$ pipenv --version # pipenv, version 2018.11.26
```


## Setup
```sh
$ git clone https://github.com/rokist/plynth-dev.git
$ cd plynth-dev
```

```sh
$ python3 setup.py -p 3.7.4 # use -l to show available python versions
```

## Initialization
* *Mac* or *Linux*
  * `sudo cp pdk /usr/local/bin/`
  * `sudo chmod 755 /usr/local/bin/pdk`

```sh
$ pdk init
```

## Create an application
```sh
$ pdk -p hello new
```

## Run the application
```sh
$ pdk -p hello run
```

## Edit the application with your favorite editor
```sh
$ vi hello/main.py
```

## Installing a python package
```sh
$ pdk i requests
```

## Release
```sh
$ pdk -p hello release
```


## Start from an example
* Windows
  * Copy __utils/exmaples/xxxx to the top folder of pdk using Explorer.
* Linux and Mac
  * ``` cp -R __utils/examples/react_example ./```
  * ``` pdk -p react_example run```
  
  
## For more information
See the instruction at the official document.
* [Plynth development kit](https://www.plynth.net/docs?id=pdk_doc)
* [Get started](https://www.plynth.net/docs?id=get_started)
