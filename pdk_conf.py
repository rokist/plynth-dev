import os
import subprocess
import platform

# ===BEGIN_base_config===
base_config = {
    "modules": {

    }
}
# ===END_base_config===


def scripts_path(info=None):
    return ["__dev_scripts"]


def myscript(info=None):
    print("Hello myscript")


def main_config():
    return base_config
