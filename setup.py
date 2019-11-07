import os
import platform
import sys
import tarfile
import zipfile
import shutil
import urllib.request
import requests
import subprocess
import json
from distutils.dir_util import copy_tree
from pathlib import Path
from subprocess import check_output, CalledProcessError, STDOUT


platform_system = platform.system()

python_version = "3.7.4"
plynth_version = "1.3.7"

cache_files_dir = "cache_files"

##
## Initialize variables
##
if not os.path.exists(cache_files_dir):
    os.mkdir(cache_files_dir)

if platform_system.upper() == "LINUX":
    zip_tmp_file_name = "plynth-"+plynth_version+"_py"+python_version+"_linux_64.zip"
elif platform_system.upper() == "DARWIN":
    pass

##
## Retrieve files
##

# retrieve a zip of plynth
plynth_zip_url = "https://www.plynth.net/dl/1.3.7/b28ed3f9/" + zip_tmp_file_name

zip_local_path = os.path.join(cache_files_dir, zip_tmp_file_name)
if not os.path.exists(zip_local_path):
    print("Downloading Plynth binaries...")
    urllib.request.urlretrieve(plynth_zip_url, zip_local_path)

if not os.path.exists(zip_local_path):
    print("Unabled to download and save a zip file")

try:
   check_output(['unzip', '-q', zip_local_path, '-d', "__plynth"], stderr=STDOUT)
except CalledProcessError as err:
    print("error unzip")

#with zipfile.ZipFile(zip_local_path) as existing_zip:
    #existing_zip.extractall("__plynth")

# zip of embed-python
url1 = "https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-win32.zip"
url2 = "https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip"
local_embed_zip = os.path.join(cache_files_dir, "embed.zip")
os.unlink(local_embed_zip)
if not os.path.exists(local_embed_zip):
    print("Downloading a python embed zip...")
    urllib.request.urlretrieve(url2, local_embed_zip)

shutil.rmtree("__utils")
try:
   check_output(['unzip', '-q', local_embed_zip, '-d', "__utils"], stderr=STDOUT)
except CalledProcessError as err:
    print("error unzip")

shutil.copytree("__utils_src", "__utils")
    

##
## Retrieve files
##
