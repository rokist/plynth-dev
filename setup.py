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

local_zip_dir = "cache_files"
if not os.path.exists(local_zip_dir):
    os.mkdir(local_zip_dir)

if platform_system.upper() == "LINUX":
    zip_tmp_file_name = "plynth-"+plynth_version+"_py"+python_version+"_linux_64.zip"
elif platform_system.upper() == "DARWIN":
    pass

plynth_zip_url = "https://www.plynth.net/dl/1.3.7/b28ed3f9/" + zip_tmp_file_name

zip_local_path = os.path.join(local_zip_dir, zip_tmp_file_name)
if not os.path.exists(zip_local_path):
    urllib.request.urlretrieve(plynth_zip_url, zip_local_path)

if not os.path.exists(zip_local_path):
    print("Unabled to download and save a zip file")


with zipfile.ZipFile(zip_local_path) as existing_zip:
    existing_zip.extractall("__plynth")

