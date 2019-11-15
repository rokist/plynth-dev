import os
import platform
import sys
import stat
import tarfile
import zipfile
import shutil
import urllib.request
import subprocess
import json
from distutils.dir_util import copy_tree
from pathlib import Path
from subprocess import check_output, CalledProcessError, STDOUT


platform_system = platform.system().upper()

#python_version = "3.7.4"
python_version = "3.6.8"

plynth_version = "1.3.7"

print("Python version: " + python_version)
print("Plynth version: " + plynth_version)

CACHE_FILES_DIR = "cache_files"

##
## Initialize variables
##
if not os.path.exists(CACHE_FILES_DIR):
    os.mkdir(CACHE_FILES_DIR)

version_numbers = python_version.split('.')
to_minor_version = version_numbers[0] + "." + version_numbers[1]
major_version = version_numbers[0]

##
## Deals with __plynth uri
##
if platform_system == "LINUX":
    zip_tmp_file_name = "plynth-"+plynth_version+"_py"+python_version+"_linux_64.zip"
elif platform_system == "DARWIN":
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    # plynth-1.3.7_py3.7.4_mac.zip
    zip_tmp_file_name = "plynth-"+plynth_version+"_py"+python_version+"_mac.zip"
else: # Windows
    zip_tmp_file_name = "plynth-"+plynth_version+"_py"+python_version+"_win_64bit.zip"
    pass

plynth_zip_url = "https://www.plynth.net/dl/1.3.7/b28ed3f9/" + zip_tmp_file_name

zip_local_path = os.path.join(CACHE_FILES_DIR, zip_tmp_file_name)
if not os.path.exists(zip_local_path):
    print("Downloading Plynth binaries...")
    urllib.request.urlretrieve(plynth_zip_url, zip_local_path)

if os.path.exists(zip_local_path):
    if os.path.exists("__plynth"):
        shutil.rmtree("__plynth")

    #os.mkdir("__plynth")

    if platform_system == "DARWIN" or platform_system == "LINUX":
        try:
           check_output(['unzip', '-q', zip_local_path, '-d', "__plynth"], stderr=STDOUT)
        except CalledProcessError as err:
            print("error unzip")
    else:
        try:
            with zipfile.ZipFile(zip_local_path) as existing_zip:
                existing_zip.extractall("__plynth")
        except Exception as err:
            print(str(err))
else:
    print("Unabled to download and save a zip file")


##
## Deals with __utils dir
##
if not os.path.exists("__utils"):
    os.mkdir("__utils")

if not os.path.exists(os.path.join("__utils", "pydir")):
    os.mkdir(os.path.join("__utils", "pydir"))


if platform_system == "LINUX":
    os.unlink(os.path.join("pdk.sh"))
    shutil.copyfile(os.path.join("pdk_linux.sh"), os.path.join("pdk.sh"))


    shutil.copytree(os.path.join("__plynth", "bin"), os.path.join("__utils", "pydir", "bin"))
    shutil.copytree(os.path.join("__plynth", "lib"), os.path.join("__utils", "pydir", "lib"))

    st = os.stat(os.path.join("__utils", "pydir", "bin", "python"))
    os.chmod(os.path.join("__utils", "pydir", "bin", "python"), st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

elif platform_system == "DARWIN":

    lib_dir = os.path.join( "__plynth", "Plynth.app/Contents/Frameworks/")
    shutil.copyfile(
        os.path.join(lib_dir, "libpython"+ to_minor_version+".dylib"),
        os.path.join("__utils", "pydir"
    )

    #os.path.join(lib_dir, "Plynth Framework.framework/Versions/A/Libraries/", "libpython"+ to_minor_version+".dylib")

    shutil.copyfile(
        os.path.join(lib_dir,"python"),
        os.path.join("__utils", "pydir")
    )

    os.chmod(os.path.join("__utils", "pydir", "python"), 0o755)#os.path.join(lib))

    try:
        shutil.copytree(
            os.path.join(lib_dir, "include"),
            os.path.join("__utils", "pydir", "include")
        )
    except:
        pass

    try:
        # copy lib dir
        shutil.copytree(
            os.path.join(lib_dir, "lib"),
            os.path.join("__utils", "pydir", "lib")
        )
    except:
        pass


    pyassets = os.path.join("__utils", "pydir", "lib", "pyassets")
    if not os.path.exists(pyassets):
        os.mkdir(pyassets)


else:
    # zip of embed-python
    #url1 = "https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-win32.zip"
    file_name = "python-"+python_version+"-embed-amd64.zip"
    url2 = "https://www.python.org/ftp/python/"+python_version+"/" + file_name
    local_embed_zip = os.path.join(CACHE_FILES_DIR, file_name)

    #if os.path.exists(local_embed_zip):
        #os.unlink(local_embed_zip)

    if not os.path.exists(local_embed_zip):
        print("Downloading a python embed zip...")
        urllib.request.urlretrieve(url2, local_embed_zip)


    with zipfile.ZipFile(local_embed_zip) as existing_zip:
        existing_zip.extractall(os.path.join("__utils", "pydir"))

