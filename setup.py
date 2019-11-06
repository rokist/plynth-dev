import sys
import os
import platform
import urllib.request


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

if not os.path.exists(os.path.join(local_zip_dir, zip_tmp_file_name)):
    urllib.request.urlretrieve(plynth_zip_url, os.path.join(local_zip_dir, zip_tmp_file_name))
    pass


