import sys
import os
import time
import urllib.request
import shutil
import logging
import itertools
import threading
import zipfile
import platform
import json
import subprocess
import struct
import random
from subprocess import check_output, CalledProcessError, STDOUT


VERSION = "1.0"

PLYNTH_VENV_DIR = "__plynth_venv"
PLYNTH_DIR = "__plynth"
UTILS_DIR = "__utils"
USER_SCRIPTS = "__dev_scripts"
DEV_VENV_DIR = "__dev_scripts"
ARGS_HIDDEN_DIR = ".pass_args_dir"
PDK_PROJECT_JSON = "pdk_project.json"
PYASSETS_NAME = "pyassets"


is_mac = platform.system() == "Darwin"
is_windows = platform.system() == "Windows"
is_linux = platform.system() == "LINUX"

which_command = "where" if is_windows else "which"

ignore_packages = ["pip", "wheel"]
ignore_name_list = ["easy_install.py", "__pycache__"]


class PdkContext:
    def __init__(self):
        self.pipenv_command_path = "pipenv"
        self.hook_values = {}

context_info = PdkContext()


HELP_MSG = "pdk (Plynth Development Kit) version "+ VERSION + """

Usage:

---- Initialization ----
pdk init
pdk remove

---- Modules management for running Plynth ----
pdk install pandas
pdk unisntall pandas
pdk clean
pdk pip isntall pandas
pdk build
pdk rebuild

---- Run python interactive command with modules installed
pdk python

---- Modules management for development ----
pdk dev install requests
pdk dev uninstall requests
pdk dev clean
pdk dev graph

---- Project management ----
[-t: target_project]
pdk -t helloworld new
pdk -t helloworld run
pdk -t helloworld npm install jquery

---- Calling User Scripts ----
pdk script myscript


---- Calling pipenv command ----
pdk pipenv --venv
pdk dev pipenv --venv

---- Release ----
pdk -t helloworld release

"""



def do_main():
    if len(sys.argv) < 3:
        print("Error: No command argument")
        return

    cwdir = sys.argv[1][1:-1]
    sys.path.append(cwdir)

    os.chdir(cwdir)

    rest_args = sys.argv[2:]
    command_arg = rest_args[0]

    project_name = None
    if command_arg == "-p" or command_arg == "-t":
        if len(rest_args) > 1:
            project_name = rest_args[1]
            rest_args = rest_args[2:]


    if not rest_args:
        print("Invalid command")
        return

    command_arg = rest_args[0]

    if project_name:
        if command_arg == "run" or command_arg == "r":
            invoke_project(cwdir, project_name, rest_args[1:])
            return
        elif command_arg == "new" or  command_arg == "newproject":
            newproject(cwdir, project_name, rest_args[1:])
            return
        elif command_arg == "npm":
            invoke_npm(cwdir, project_name, rest_args[1:])
            return
        elif command_arg == "release":
            release_project(cwdir, project_name, rest_args[1:])
            return


    load_pipenv_command_path()


    if command_arg == "--help" or command_arg == "-h":
        print(HELP_MSG)
    elif command_arg == "init":
        init_pdk()
    
    elif command_arg == "remove_devenv":
        remove_pipenv(DEV_VENV_DIR, None)
    elif command_arg == "remove":
        remove_pipenv(PLYNTH_VENV_DIR, "remove_devenv")
        remove_pipenv(DEV_VENV_DIR, None)
    elif command_arg == "remove_env":
        remove_pipenv(PLYNTH_VENV_DIR, None)

    elif command_arg == "clean_dev":
        passing_args = [context_info.pipenv_command_path, "clean"]
        invoke_pipenv_command(True, passing_args, None)
    
    elif command_arg == "clean_and_build":
        passing_args = [context_info.pipenv_command_path, "clean"]
        invoke_pipenv_command(False, passing_args, "build")


    elif command_arg == "install_certifi":
        install_certifi(PLYNTH_VENV_DIR, None)

    elif command_arg == "install_devenv":
        create_pipenv_project(DEV_VENV_DIR, "install_certifi" if is_mac else None)
    elif command_arg == "install_env":
        create_pipenv_project(PLYNTH_VENV_DIR, "install_devenv")
        create_pipenv_project(DEV_VENV_DIR, None)


    elif command_arg == "--version" or command_arg == "-v":
        print("v" + VERSION)
    elif command_arg == "script" or command_arg == "scr":
        invoke_script(cwdir, rest_args[1:])
 
    elif command_arg == "python":
        run_python(cwdir, rest_args[1:])
    
    else:
        # from here, need pipenv command
        venv_dir = find_pipenv_venv_location(PLYNTH_VENV_DIR, True)

        if venv_dir and rest_args:
            command_arg = rest_args[0]

            devmode = False
            if command_arg == "build":
                appsync(cwdir, venv_dir, rest_args[1:], False)
                return
            elif command_arg == "rebuild":
                rebuild(cwdir, venv_dir, rest_args[1:])
                return
            elif command_arg == "dev":
                devmode = True
                rest_args = rest_args[1:]

            # devmode or mainmode
            command_arg = rest_args[0]

            if command_arg == "graph":
                invoke_graph(devmode, cwdir, venv_dir, rest_args[1:])

            elif command_arg == "clean":
                invoke_clean(devmode, cwdir, venv_dir, rest_args[1:])

            elif command_arg == "exec":
                invoke_pipenv_run(devmode, cwdir, venv_dir, rest_args[1:])
            elif command_arg == "pip":
                invoke_pipenv_run(devmode, cwdir, venv_dir, rest_args)
            elif command_arg == "python":
                if devmode:
                    invoke_pipenv_run(devmode, cwdir, venv_dir, rest_args)

            elif command_arg == "install" or command_arg == "i":
                install_action(devmode, cwdir, venv_dir, rest_args[1:])

            elif command_arg == "uninstall" or command_arg == "u":
                if len(rest_args) > 1:
                    uninstall_action(devmode, cwdir, venv_dir, rest_args[1:])

            elif command_arg == "pipenv":
                invoke_generic(devmode, cwdir, venv_dir, rest_args[1:])
            else:
                print("Invalid command")




def invoke_npm(cwdir, project_name, args):
    if args:
        projectdir = project_name.strip().strip("/")
        os.chdir(projectdir)
            
        try:
            if is_windows:
                passing_args = ["npm.cmd"]
                passing_args.extend(args)
                print(passing_args)
            else:
                passing_args = ["npm"]
                passing_args.extend(args)
                print(passing_args)
                
            subprocess.call(passing_args)
        finally:
            os.chdir("..")


def invoke_project(cwdir, project_name, args):
    if is_windows:
        passing_args = [PLYNTH_DIR + "/plynth.exe", project_name]
        passing_args.extend(args)

        subprocess.call(passing_args)

    if is_mac:
        target_site_packages_dir = os.path.join(
            cwdir,
            PLYNTH_DIR,
            "Plynth.app",
            "Contents",
            "MacOS",
            "Plynth"
        )


        app_dir = os.path.join(cwdir, PLYNTH_DIR, "Plynth.app", "Contents", "Resources", "app")
        if os.path.exists(app_dir):
            shutil.rmtree(app_dir)


        passing_args = [target_site_packages_dir, project_name]
        passing_args.extend(args)
        subprocess.call(passing_args)



def call_hook_scripts(cwdir, hook_name, args):
    try:
        import pdk_conf
    except Exception as err:
        print(str(err))

    if os.path.exists(DEV_VENV_DIR):
        os.chdir(DEV_VENV_DIR)
        try:
            exe_args = [
                context_info.pipenv_command_path,
                "run",
                "python",
                "-B",
                "-u",
                os.path.join("..", UTILS_DIR, "invoke_script.py"),
                "call_hook",
                hook_name,
            ]

            if not os.path.exists(ARGS_HIDDEN_DIR):
                os.mkdir(ARGS_HIDDEN_DIR)

            arg_dict = {}
            arg_dict["hook_name"] = hook_name
            arg_dict["devkit_home"] = cwdir
            arg_dict["plynth_dir"] = os.path.join(cwdir, PLYNTH_DIR)
            arg_dict["dev_scripts_path"] = os.path.join(cwdir, DEV_VENV_DIR)
            if is_windows:
                arg_dict["plynth_assets_path"] = os.path.join(cwdir, PLYNTH_DIR, PYASSETS_NAME)
            else:
                arg_dict["plynth_assets_path"] = os.path.join(cwdir, PLYNTH_DIR, "Plynth.app", "Contents","Frameworks", "lib", PYASSETS_NAME)

            for i in args:
                arg_dict[i] = args[i]

            max_val = 1000
            idx = random.randint(1, max_val-1)
            file_path = None
            filename = None
            for _ in range(max_val):
                idx += 1
                filename = "args_file_" + str(idx % max_val)
                file_path = os.path.join(ARGS_HIDDEN_DIR, filename)
                if not os.path.exists(file_path):
                    break
            
            if file_path:
                try:
                    with open(file_path, mode="w") as write_file:
                        json.dump(arg_dict, write_file)

                    exe_args.append(filename)
                    ret = subprocess.call(exe_args)
                    if ret > 0:
                        print("Error code:" + str(ret))


                    arg_dict = {}
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf8") as f:
                            arg_dict = json.load(f)

                            context_info.hook_values[hook_name] = arg_dict


                finally:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
        finally:
            os.chdir("..")


def invoke_script(cwdir, args):
    try:
        import pdk_conf
    except Exception as err:
        print(str(err))

    # Check if we can use the python binary file in pipenv project __dev_scripts
    tried_at_least = False
    if os.path.exists(DEV_VENV_DIR):
        os.chdir(DEV_VENV_DIR)
        try:
            exe_args = [
                context_info.pipenv_command_path,
                "run",
                "python",
                "-B",
                "-u",
                os.path.join("..", UTILS_DIR, "invoke_script.py"),
                "invoke_script",
            ]
            exe_args.extend(args)

            tried_at_least = True
            ret = subprocess.call(exe_args)
            if ret > 0:
                print("Error code:" + str(ret))
        finally:
            os.chdir("..")


    if (not tried_at_least) and args:
        script_name = args[0]
        if hasattr(pdk_conf, script_name):
            att = getattr(pdk_conf, script_name)
            if callable(att):
                try:
                    att({})
                except Exception as e:
                    print(str(e))



def run_python(cwdir, args):
    if is_mac:
        target_site_packages_dir = os.path.join(
            cwdir,
            PLYNTH_DIR,
            "Plynth.app",
            "Contents",
            "Frameworks",
            "python"
        )
        
        commands = [target_site_packages_dir]
        commands.extend(args)
        subprocess.call(commands)

    if is_windows:
        source_path = os.path.join(cwdir, PLYNTH_DIR, PYASSETS_NAME, "python.exe")
        target_path = os.path.join(cwdir, PLYNTH_DIR, "_python.exe")

        if (not os.path.exists(target_path)) and os.path.exists(source_path):
            shutil.copyfile(source_path, target_path)

        if os.path.exists(target_path):
            os.chdir(os.path.join(cwdir, PLYNTH_DIR))
            try:
                passing_args = ["_python.exe", "-B"]
                passing_args.extend(args)

                ret = subprocess.call(passing_args)

                os.unlink(target_path)
            except PermissionError:
                print("[permission error]")
            finally:
                os.chdir(cwdir)


def invoke_pipenv_run(devmode, cwdir, venv_dir, args):
    passing_args = [context_info.pipenv_command_path, "run"]
    passing_args.extend(args)


    run_build = (not devmode) and (len(args)>1) and args[1] == "install"

    invoke_pipenv_command(devmode, passing_args, "build" if run_build else None)

    if run_build:
        appsync(cwdir, venv_dir, args, False)


def invoke_generic(devmode, cwdir, venv_dir, args):
    passing_args = [context_info.pipenv_command_path]
    passing_args.extend(args)

    run_build = (not devmode) and (len(args)>0) and args[0] == "install"

    invoke_pipenv_command(devmode, passing_args, "build" if run_build else None)

    if run_build:
        appsync(cwdir, venv_dir, args, False)



def invoke_clean(devmode, cwdir, venv_dir, args):
    passing_args = [context_info.pipenv_command_path, "clean"]
    passing_args.extend(args)

    invoke_pipenv_command(devmode, passing_args, "build")

    appsync(cwdir, venv_dir, args, False)


def invoke_graph(devmode, cwdir, venv_dir, args):
    passing_args = [context_info.pipenv_command_path, "graph"]
    passing_args.extend(args)

    invoke_pipenv_command(devmode, passing_args)




def rebuild(cwdir, venv_dir, args):
    if is_windows:
        target_site_packages_dir = os.path.join(cwdir, PLYNTH_DIR, "Lib", "site-packages")
    else:
        target_site_packages_dir = os.path.join(
            cwdir,
            PLYNTH_DIR,
            "Plynth.app",
            "Contents",
            "Frameworks",
            "lib",
            f"python{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
            "site-packages",
        )

    os.makedirs(target_site_packages_dir, exist_ok=True)
    if os.path.exists(target_site_packages_dir):
        files_in_site_packages = os.listdir(target_site_packages_dir)
        for entry in files_in_site_packages:
            entry_path = os.path.join(target_site_packages_dir, entry)

            remove_file_or_dir(entry_path)

    appsync(cwdir, venv_dir, args, True)


def remove_file_or_dir(entry):
    if entry and os.path.exists(entry):
        try:
            if os.path.isfile(entry):
                os.unlink(entry)
            elif os.path.isdir(entry):
                shutil.rmtree(entry)
        except Exception as e:
            print(str(e))


def release_project(cwdir, project_name, args):

    project_name = project_name.strip().strip('/')
    project_dir = os.path.join(cwdir, project_name)
    if not os.path.exists(project_dir):
        pass

    app_version = "1.0.0"
    package_file = os.path.join(project_dir, "package.json")
    if os.path.exists(package_file):
        try:
            with open(package_file) as f:
                package_info = json.load(f)
                if "version" in package_info:
                    app_version = package_info["version"]
        except:
            print("error")

    zip_base_name = project_name + "-v" + app_version


    for idx in range(100000):
        release_workspace = os.path.join(cwdir, "release_workspace_"+project_name+("" if idx==0 else "_"+str(idx+1)))

        if os.path.exists(release_workspace):
            continue

        break

    print("Copying files...")
    shutil.copytree(os.path.join(cwdir, PLYNTH_DIR), release_workspace)


    
    if is_windows:
        def zipdir(path, ziph, dir_inzip):
            for cur, dirs, files in os.walk(path):
                for file in files:

                    basename = os.path.basename(cur)
                    if basename == "__pycache__":
                        continue

                    if file == "plynth.exe":
                        arcname = os.path.join(dir_inzip, os.path.relpath(cur, path), project_name+".exe")
                    else:
                        arcname = os.path.join(dir_inzip, os.path.relpath(cur, path), file)
                    if arcname:
                        print(arcname)
                        ziph.write(os.path.join(cur, file), arcname=arcname)

        for idx in range(100000):
            full_file_name = os.path.join(cwdir, zip_base_name+("" if idx==0 else "_"+str(idx+1))+".zip")

            if os.path.exists(full_file_name):
                continue

            print("File path: " + full_file_name)
            print("Zipping...")


            zipf = zipfile.ZipFile(full_file_name, "w", zipfile.ZIP_DEFLATED)
            zipdir(release_workspace, zipf, "")
            zipdir(project_dir, zipf, "resources\\app")

            zipf.close()
            break
    
    if is_mac:
        app_name = project_name +".app"
        new_app_dir = os.path.join(release_workspace, app_name)
        os.rename(os.path.join(release_workspace, "Plynth.app"), new_app_dir)

        app_target_dir = os.path.join(new_app_dir, "Contents", "Resources", "app")

        if os.path.exists(app_target_dir):
            shutil.rmtree(app_target_dir)

        for idx in range(100000):
            filename = zip_base_name + ("" if idx==0 else "_"+str(idx+1))+".zip"
            full_file_name = os.path.join(cwdir, filename)

            if os.path.exists(full_file_name):
                continue

            print("File name: " + filename)
            print("File path: " + full_file_name)
            print("Zipping...")

            shutil.copytree(project_dir, app_target_dir)

            try:
                check_output(['zip', '-ry', full_file_name, app_name], stderr=STDOUT, cwd=release_workspace)
            except CalledProcessError as err:
                print("zip error: 9807889")
            
            shutil.rmtree(app_target_dir)
            
            print("Done.")

            break

    shutil.rmtree(release_workspace)

def appsync(cwdir, venv_dir, args, is_rebuild, installs=None):
    print("* " * 21)

    if is_windows:
        target_site_packages_dir = os.path.join(
            cwdir, PLYNTH_DIR, "Lib", "site-packages"
        )
        site_packages_dir = os.path.join(venv_dir, "Lib", "site-packages")

    else:
        target_site_packages_dir = os.path.join(
            cwdir,
            PLYNTH_DIR,
            "Plynth.app",
            "Contents",
            "Frameworks",
            "lib",
            f"python{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
            "site-packages",
        )
        os.makedirs(target_site_packages_dir, exist_ok=True)
        
        site_packages_dir = os.path.join(
            venv_dir,
            "lib",
            f"python{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
            "site-packages",
        )

    passing_args = {
         "source_site_packages_path": site_packages_dir,
         "target_site_packages_path": target_site_packages_dir,
         "rebuild": is_rebuild
    }

    call_hook_scripts(cwdir, "will_build", passing_args)


    term = "Building Plynth  "
    done = False

    def animate():
        anim_list = []
        width = 20
        for i in range(width):
            anim_list.append("[" + " " * i + "===" + " " * (width - i - 1) + "]")

        for i in reversed(anim_list.copy()):
            anim_list.append(i)

        for c in itertools.cycle(anim_list):
            if done:
                sys.stdout.write("\r" + term + c)
                print("\nDone.")
                break
            sys.stdout.write("\r" + term + c)
            sys.stdout.flush()
            time.sleep(0.04)

    t = threading.Thread(target=animate)
    t.start()



    try:
        files_in_site_packages = os.listdir(site_packages_dir)

        skip_prevent_dirs = []
        recreate_dirs = []
        skip_dirs = []


        for file in files_in_site_packages:
            if not file.endswith(".dist-info"):
                if file in ignore_packages:
                    skip_dirs.append(file)
                if file in ignore_name_list:
                    skip_dirs.append(file)

            if file.endswith(".dist-info"):
                # print(file)
                package_name = ""

                for infile in os.listdir(os.path.join(site_packages_dir, file)):
                    if infile == "METADATA":
                        file_path = os.path.join(site_packages_dir, file, infile)
                        with open(file_path, "r", encoding="utf8") as f:
                            for line in f.readlines():
                                if line.startswith("Name: "):
                                    package_name = line[6:].strip()
                                    break
                                elif line.startswith("Requires-Dist: "):
                                    pass

                    if infile == "top_level.txt":
                        file_path = os.path.join(site_packages_dir, file, infile)
                        with open(file_path, "r", encoding="utf8") as f:
                            for line in f.readlines():
                                line = line.strip()
                                if line:
                                    if package_name in ignore_packages:
                                        skip_dirs.append(line)
                                    else:
                                        skip_prevent_dirs.append(line)

                                    if installs and package_name in installs:
                                        recreate_dirs.append(line)

        for d in skip_prevent_dirs:
            if d in skip_dirs:
                skip_dirs.remove(d)


        if "will_build" in context_info.hook_values:
            if "skip_module_dirs" in context_info.hook_values["will_build"]:
                skip_dirs.extend(context_info.hook_values["will_build"]["skip_module_dirs"])

        for file in files_in_site_packages:
            #if file.endswith(".dist-info"):
                #continue

            if not file in skip_dirs:
                source_path = os.path.join(site_packages_dir, file)
                target_path = os.path.join(target_site_packages_dir, file)

                if os.path.exists(target_path):
                    if file in recreate_dirs:
                        remove_file_or_dir(target_path)

                if not os.path.exists(target_path):
                    try:
                        if os.path.isfile(source_path):
                            shutil.copyfile(source_path, target_path)
                        elif os.path.isdir(source_path):
                            shutil.copytree(source_path, target_path)
                    except Exception as e:
                        print(str(e))

                # Delete __pycache__
                if True:
                    remove_dirs = []
                    for cur, dirs, files in os.walk(target_path):
                        for d in dirs:
                            arcname = os.path.join(target_path, cur, d)

                            if os.path.basename(d) == "__pycache__":
                                remove_dirs.append(arcname)

                    for d in remove_dirs:
                        remove_file_or_dir(d)

        dic = dict()
        for d in os.listdir(site_packages_dir):
            dic[d] = True

        for d in os.listdir(target_site_packages_dir):
            if not d in dic:
                entry_path = os.path.join(target_site_packages_dir, d)
                remove_file_or_dir(entry_path)



        

    finally:
        done = True

    time.sleep(0.2)
    print("Calling 'did_build' hook...")
    call_hook_scripts(cwdir, "did_build", passing_args)
    print("Done.")


    # Recompose python37._pth
    if is_windows: 
        pyassets = os.path.join(cwdir, PLYNTH_DIR, PYASSETS_NAME)
        python_pth = os.path.join(cwdir, PLYNTH_DIR, "python" + str(sys.version_info.major) + str(sys.version_info.minor) + "._pth")

        upper_text = ""
        bottom_text = ""

        if os.path.exists(python_pth):
            state = 0
            with open(python_pth, "r") as f:
                for line in f.readlines():
                    if line.startswith("# BEGIN_PLYNTH"):
                        state = 1
                    elif line.startswith("# END_PLYNTH"):
                        state = 2
                    elif state == 0:
                        upper_text += line
                    elif state == 2:
                        bottom_text += line

            if upper_text and upper_text[-1] != "\n":
                upper_text += "\n"

        text = upper_text

        text += "# BEGIN_PLYNTH\n"
        for filename in os.listdir(pyassets):
            if filename.endswith(".zip"):
                text += PYASSETS_NAME + "/" + filename + "\n"
        text += "." + "\n"
        text += PYASSETS_NAME + "\n"
        text += "# END_PLYNTH\n"

        text += bottom_text

        with open(python_pth, mode="w") as write_file:
            write_file.write(text)
    


def uninstall_action(devmode, cwdir, venv_dir, args):
    passing_args = [context_info.pipenv_command_path, "uninstall", "--skip-lock"]
    passing_args.extend(args)

    invoke_pipenv_command(devmode, passing_args, "clean_dev" if devmode else "clean_and_build")

    if is_windows and (not devmode):
        invoke_pipenv_command(devmode, [context_info.pipenv_command_path, "clean"], None)

        appsync(cwdir, venv_dir, args, False)


def install_action(devmode, cwdir, venv_dir, args):
    # --system                 System pip management.  [env var: PIPENV_SYSTEM]
    # -c, --code TEXT          Import from codebase.
    # --deploy                 Abort if the Pipfile.lock is out-of-date, or Python
    #                          version is wrong.
    # --skip-lock              Skip locking mechanisms and use the Pipfile instead
    #                          during operation.  [env var: PIPENV_SKIP_LOCK]
    # -e, --editable TEXT      An editable python package URL or path, often to a
    #                          VCS repo.
    # --ignore-pipfile         Ignore Pipfile when installing, using the
    #                          Pipfile.lock.  [env var: PIPENV_IGNORE_PIPFILE]
    # --selective-upgrade      Update specified packages.
    # --pre                    Allow pre-releases.
    # -r, --requirements TEXT  Import a requirements.txt file.
    # --extra-index-url TEXT   URLs to the extra PyPI compatible indexes to query
    #                          for package lookups.
    # -i, --index TEXT         Target PyPI-compatible package index url.
    # --sequential             Install dependencies one-at-a-time, instead of
    #                          concurrently.  [env var: PIPENV_SEQUENTIAL]
    # --keep-outdated          Keep out-dated dependencies from being updated in
    #                          Pipfile.lock.  [env var: PIPENV_KEEP_OUTDATED]
    # --pre                    Allow pre-releases.
    # -d, --dev                Install both develop and default packages.  [env
    #                          var: PIPENV_DEV]
    # --python TEXT            Specify which version of Python virtualenv should
    #                          use.
    # --three / --two          Use Python 3/2 when creating virtualenv.
    # --clear                  Clears caches (pipenv, pip, and pip-tools).  [env
    #                          var: PIPENV_CLEAR]
    # -v, --verbose            Verbose mode.
    # --pypi-mirror TEXT       Specify a PyPI mirror.
    # -h, --help               Show this message and exit.
    has_arg_options = [
        "-c",
        "--code",
        "-e",
        "--editable",
        "-r",
        "--requirements",
        "--extra-index-url",
        "-i",
        "--index",
        "--python",
        "--pypi-mirror",
    ]

    options = [
        "--system",
        "--deploy",
        "--skip-lock",
        "--ignore-pipfile",
        "--selective-upgrade",
        "--pre",
        "--sequential",
        "--keep-outdated",
        "--pre",
        "-d",
        "--dev",
        "--three",
        "--two",
        "--clear",
        "-v",
        "--verbose",
        "-h",
        "--help",
    ]

    packages = []
    options = []
    prev_is_has_arg_option = False

    for arg in args[0:]:
        if prev_is_has_arg_option:
            prev_is_has_arg_option = False
            options.append(arg)
            continue

        if arg in has_arg_options:
            prev_is_has_arg_option = True
            options.append(arg)
            continue
        elif arg in options:
            options.append(arg)
            continue

        packages.append(arg)

    # Check whether the package existed on pypi.org
    pypi_url_check_enabled = False
    if pypi_url_check_enabled:
        failed_packages = []
        for package in packages:
            if (not "://" in package) and not "." in package:
                url = "https://pypi.org/pypi/" + package + "/json"
                req = urllib.request.Request(url)
                try:
                    with urllib.request.urlopen(req, timeout=5) as res:
                        body = res.read()
                except urllib.error.HTTPError as e:
                    failed_packages.append(package)
                except Exception as e:
                    print("error code 19283: " + str(package))

        if failed_packages:
            url = "https://pypi.org"
            req = urllib.request.Request(url)
            try:
                with urllib.request.urlopen(req, timeout=3) as res:
                    body = res.read()
            except Exception:
                failed_packages = []

        for failed in failed_packages:
            packages.remove(failed)

    print("packages: " + str(packages))


    passing_args = [context_info.pipenv_command_path, "install", "--skip-lock"]
    passing_args.extend(options)
    passing_args.extend(packages)

    invoke_pipenv_command(devmode, passing_args, "build" if not devmode else None)

    if is_windows:
        if not devmode:
            appsync(cwdir, venv_dir, args, False, installs=packages)



def invoke_pipenv_command(devmode, pipenv_command_args, next_command=None):
    if devmode:
        venv_dir = DEV_VENV_DIR
    else:
        venv_dir = PLYNTH_VENV_DIR

    if is_mac:
        with open(".back_command", mode="w") as write_file:
            scr = "cd " + venv_dir
            scr += "\n"
            scr += " ".join(pipenv_command_args)
            write_file.write(scr)

        if next_command:
            with open(".next_command", mode="w") as write_file:
                write_file.write(next_command)

        sys.exit()
    else:
        os.chdir(venv_dir)

        try:
            subprocess.call(pipenv_command_args)
        finally:
            os.chdir("..")


def predict_python_path(command_name):
    system_drive = "C:"

    if 'SYSTEMDRIVE' in os.environ:
        system_drive = os.environ['SYSTEMDRIVE']


    b32 = struct.calcsize("P") * 8 == 32
    ext = "-32" if b32 else ""

    python_version = str(sys.version_info.major) + str(sys.version_info.minor) + ext

    user_name = os.getlogin()
    if user_name:
        #C:\Users\username\AppData\Local\Programs\Python\Python37\Scripts\pipenv.exe
        command_path = system_drive + "\\Users\\"+user_name+"\\AppData\\Local\\Programs\\Python\\Python"+python_version+"\\Scripts\\" + command_name
        if os.path.exists(command_path):
            return command_path

    # C:\Program Files\Python36
    command_path = system_drive + "\\Program Files\\"+python_version+"\\Scripts\\" + command_name
    if os.path.exists(command_path):
        return command_path

    #C:\Program Files (x86)\Python36-32
    command_path = system_drive + "\\Program Files (x86)\\"+python_version+"\\Scripts\\" + command_name
    if os.path.exists(command_path):
        return command_path


    return None


# 1. Check whether pipenv command exists
# 2. Check whether pip command exists
# 3. Try to execute `pip install pipenv`
def prepare_pipenv_command():

    if not os.path.exists(PLYNTH_VENV_DIR):
        os.mkdir(PLYNTH_VENV_DIR)


    if not os.path.exists(DEV_VENV_DIR):
        os.mkdir(DEV_VENV_DIR)

    if is_windows:
        try:
            vcruntime140 = get_line(cmd=[which_command, "vcruntime140.dll"])
            if len(vcruntime140.strip()) > 4:
                pass
            else:
                shutil.copy( 
                    os.path.join(UTILS_DIR, "vcruntime140.dll"), 
                    PLYNTH_VENV_DIR
                )
                shutil.copy( 
                    os.path.join(UTILS_DIR, "vcruntime140.dll"), 
                    DEV_VENV_DIR
                )
        except:
            pass

        # Find out pip/pipenv path
        pipenv_command = predict_python_path("pipenv.exe")
        if pipenv_command:
            return pipenv_command
        
        pip_command = predict_python_path("pip.exe")
        if pip_command:
            subprocess.call([pip_command, "install", "pipenv"])

            pipenv_command = predict_python_path("pipenv.exe")
            if pipenv_command:
                return pipenv_command



    # Check pipenv is installed
    where_pipenv = get_line(cmd=[which_command, "pipenv"])
    # print(where_pipenv)
    if len(where_pipenv) > 4 and os.path.exists(where_pipenv.strip()):
        return where_pipenv.strip()


    if is_windows:

        where_pip = get_line(cmd=[which_command, "pip"])
        print(where_pip)

        if len(where_pip) > 4 and os.path.exists(where_pip.strip()):
            print("pipenv command not found")

            message = "Are you OK to install pipenv by using `pip install pipenv` command (yes/no) "
            y = input(message)

            if y == "y" or y == "yes":
                subprocess.call(["pip", "install", "pipenv"])
                print(where_pip)

        where_pipenv = get_line(cmd=[which_command, "pipenv"])
        print(where_pipenv)

        if len(where_pipenv) > 4 and os.path.exists(where_pipenv.strip()):
            return where_pipenv.strip()






def load_pipenv_command_path():
    # Check __plynth_venv/pdk_project.json
    pdk_project = os.path.join(PLYNTH_VENV_DIR, PDK_PROJECT_JSON)
    pdk_info_dict = None
    if os.path.exists(pdk_project):
        with open(pdk_project, "r", encoding="utf8") as f:
            pdk_info_dict = json.load(f)
            #print(pdk_info_dict)
    
    if pdk_info_dict and "pipenv_command_path" in pdk_info_dict:
        pipenv_command_path = pdk_info_dict["pipenv_command_path"]
        if os.path.exists(pipenv_command_path):
            context_info.pipenv_command_path = pipenv_command_path

    return None



def init_pdk():

    if not os.path.exists(PLYNTH_VENV_DIR):
        os.mkdir(PLYNTH_VENV_DIR)
    if not os.path.exists(DEV_VENV_DIR):
        os.mkdir(DEV_VENV_DIR)


    pipenv_ready = prepare_pipenv_command()
    print("pipenv command: " + ("OK" if pipenv_ready else "NG"))

    if not pipenv_ready:
        print("Error: cannot find `pipenv` command.")
        return


    context_info.pipenv_command_path = pipenv_ready

    main_venv_dir = find_pipenv_venv_location(PLYNTH_VENV_DIR, False)
    dev_venv_dir = find_pipenv_venv_location(DEV_VENV_DIR, False)

    print("main pipenv project: " + ("OK" if main_venv_dir else "NG"))
    print("dev pipenv project: " + ("OK" if dev_venv_dir else "NG"))

    save_pipenv_path(main_venv_dir, pipenv_ready)

    print("Initialized successfully")

    if is_mac: # install ceritifi
        install_certifi(PLYNTH_VENV_DIR, None)
        



def try_copy_vcruntime(target_dir):
    
    if not os.path.exists(PLYNTH_VENV_DIR):
        return

    os.chdir(PLYNTH_VENV_DIR)

    try:
        # Check pipenv is installed
        where_pipenv = get_line(cmd=[which_command, "vcruntime140.dll"])
        #print(where_pipenv)
        if len(where_pipenv) > 4 and os.path.exists(where_pipenv.strip()):
            return where_pipenv.strip()
        
        return None
    finally:
        os.chdir("..")

def save_pipenv_path(main_venv_dir, pipenv_command_path):
    # __plynth_venv/pdk_project.json
    pdk_project = os.path.join(PLYNTH_VENV_DIR, PDK_PROJECT_JSON)
    pdk_info_dict = None
    if os.path.exists(pdk_project):
        with open(pdk_project, "r", encoding="utf8") as f:
            pdk_info_dict = json.load(f)


    if not pdk_info_dict:
        pdk_info_dict = {
            "pipenv_relative": True,
            "pipenv_dir": "",
            "pipenv_command_path": "",
            "pdk_path": "",
            "pdk_version": VERSION,
            "validate_pipenv_path": True,
        }
    
    if main_venv_dir:
        pdk_info_dict["pipenv_dir"] = main_venv_dir
    
    pdk_info_dict["pipenv_relative"] = main_venv_dir and os.path.normpath(main_venv_dir) == os.path.normpath(os.path.join(os.getcwd(), PLYNTH_VENV_DIR, ".venv"))

    pdk_info_dict["pdk_version"] = VERSION

    pdk_info_dict["pipenv_command_path"] = pipenv_command_path

    with open(pdk_project, mode="w", encoding="utf8") as write_file:
        json.dump(pdk_info_dict, write_file)



def install_certifi(target_dir, next_command):
    cwdir = os.getcwd()

    os.chdir(target_dir)

    try:
        python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
        # python_version = "3.8"

        print("Creating pipenv project... : python " + python_version)

        if is_mac:
            with open(os.path.join(cwdir, ".back_command"), mode="w") as write_file:
                scr = "cd " + target_dir
                scr += "\n"
                scr += context_info.pipenv_command_path + " install certifi --skip-lock"
                write_file.write(scr)

            if next_command:
                with open(os.path.join(cwdir, ".next_command"), mode="w") as write_file:
                    write_file.write(next_command)

            sys.exit()

        else:
            subprocess.call([context_info.pipenv_command_path, "install" , "--skip-lock"])



    finally:
        os.chdir("..")


def create_pipenv_project(target_dir, next_command):
    cwdir = os.getcwd()

    os.chdir(target_dir)

    try:
        python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
        # python_version = "3.8"

        print("Creating pipenv project... : python " + python_version)

        if is_mac:
            with open(os.path.join(cwdir, ".back_command"), mode="w") as write_file:
                scr = "cd " + target_dir
                scr += "\n"
                scr += context_info.pipenv_command_path + " install  --skip-lock --python " + python_version 
                write_file.write(scr)

            if next_command:
                with open(os.path.join(cwdir, ".next_command"), mode="w") as write_file:
                    write_file.write(next_command)

            sys.exit()

        else:
            subprocess.call([context_info.pipenv_command_path, "install", "--skip-lock", "--python", python_version])



    finally:
        os.chdir("..")


def remove_pipenv(target_dir, next_command):
    cwdir = os.getcwd()
    os.chdir(target_dir)

    try:
        python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
        # python_version = "3.8"

        print("Creating pipenv project... : python " + python_version)

        if is_mac:
            with open(os.path.join(cwdir, ".back_command"), mode="w") as write_file:
                scr = "cd " + target_dir
                scr += "\n"
                scr += context_info.pipenv_command_path + " --rm"
                write_file.write(scr)

            if next_command:
                with open(os.path.join(cwdir, ".next_command"), mode="w") as write_file:
                    write_file.write(next_command)

            sys.exit()

        else:
            subprocess.call([context_info.pipenv_command_path, "--rm"])

    finally:
        os.chdir("..")



def find_pipenv_venv_location(target_dir, ask_to_install):
    cwdir = os.getcwd()

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    os.chdir(target_dir)

    try:
        has_Pipfile = os.path.exists("Pipfile")
        if has_Pipfile:
            venv_path = get_line(cmd=[context_info.pipenv_command_path, "--venv"])
            if venv_path:
                venv_path = venv_path.strip()
                if len(venv_path) > 3 and os.path.exists(venv_path.strip()):
                    return venv_path.strip()

        message = "******************************** \n "
        message += "OK to create a pipenv project in `"+target_dir+"`? (yes/no): "

        y = input(message) if ask_to_install else "yes"

        if y == "y" or y == "yes":
            python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
            # python_version = "3.8"

            print("Creating new pipenv project... : python " + python_version)


            if is_mac:
                add_install = " install --skip-lock " if has_Pipfile else ""

                with open(os.path.join(cwdir, ".back_command"), mode="w") as write_file:
                    scr = "cd " + target_dir
                    scr += "\n"
                    scr += context_info.pipenv_command_path + add_install+ " --python " + python_version
                    write_file.write(scr)

                with open(os.path.join(cwdir, ".next_command"), mode="w") as write_file:
                    write_file.write("__same__")

                sys.exit()

            else:
                arglist = [context_info.pipenv_command_path]
                if has_Pipfile:
                    arglist.append("install")
                    arglist.append("--skip-lock")

                arglist.append("--python")
                arglist.append(python_version)

                subprocess.call(arglist)

                # Requested Python version (3.8) not installed, use -0 for available pythons
                # Warning: Python 3.8 was not found on your system...
                has_Pipfile = os.path.exists("Pipfile")
                if has_Pipfile:
                    venv_path = get_line(cmd=[context_info.pipenv_command_path, "--venv"])
                    print(venv_path)
                    if (
                        venv_path
                        and len(venv_path) > 3
                        and os.path.exists(venv_path.strip())
                    ):
                        #C:\Users\User\.virtualenvs\__plynth_venv-ZFW69wgV\Scripts
                        try:
                            os.chdir("..")

                            vcruntime140 = get_line(cmd=[which_command, "vcruntime140.dll"])
                            if vcruntime140 and len(vcruntime140.strip()) > 4:
                                pass
                            else:
                                shutil.copy( 
                                    os.path.join(UTILS_DIR, "vcruntime140.dll"), 
                                    os.path.join(venv_path.strip(), "Scripts")
                                )
                        except Exception as e:
                            print(str(e))
                        finally:
                            os.chdir(target_dir)

                        return venv_path.strip()

    finally:
        os.chdir("..")

    return False


def newproject(cwdir, project_name, rest_args):
    if os.path.exists(project_name) and len(os.listdir(project_name)) > 0:
        print(project_name + " directory is not empty.")
        return
    if not os.path.exists(project_name):
        os.mkdir(project_name)

    package_file = os.path.join(project_name, "package.json")
    index_js_file = os.path.join(project_name, "index.js")
    index_html_file = os.path.join(project_name, "index.html")
    index_py_file = os.path.join(project_name, "main.py")

    with open(package_file, mode="w") as write_file:
        text = """{
    "name": "Plynth Hello",
    "version": "1.0.0",
    "description": "",
    "scripts": {},
    "author": "",
    "license": "ISC",
    "devDependencies": {},
    "deletedDependencies": {},
    "dependencies": {
    },
    "plynth": {}
}
"""
        write_file.write(text)


    with open(index_js_file, mode="w") as write_file:
        text = """var electron = require("electron")

function on_app_ready() {
    let browserWindow = new electron.BrowserWindow(
            {x:200, y:200, width:600, height:480}
    );

    let url_dict = {
        pathname:require("path").join(__dirname, "index.html"), protocol:"file:", slashesd:true
    }

    browserWindow.loadURL(require("url").format(url_dict))
}

electron.app.on("ready", on_app_ready)

"""
        write_file.write(text)

    with open(index_html_file, mode="w") as write_file:
        text = """<!doctype html>
<html>
<head>
    <script type="text/python" import="main" call="main"></script>
</head>

<body>
    <div id="top">Hello Plynth</div>
</body>

</html>
"""
        write_file.write(text)

    with open(index_py_file, mode="w") as write_file:
        text = """import sys
import plynth
import plynth.js as js

def main():
    print("Hello")
"""
        write_file.write(text)







def get_lines(cmd):
    if not is_windows:
        oldcmd = cmd
        cmd = [" ".join(cmd)]
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    while True:
        line = proc.stdout.readline()
        if line:
            try:
                text = force_decode(line)
                yield text
            except Exception as err:
                text = "error:" + str(err)
                yield text

        if not line and proc.poll() is not None:
            break

    out, err = proc.communicate()


def force_decode(string):
    codecs = ["cp1252", "cp932", "utf8"]
    for i in codecs:
        try:
            return string.decode(i)
        except UnicodeDecodeError:
            pass
    return ""


def get_line(cmd):
    str_buf = ""
    for line in get_lines(cmd):
        str_buf += line

    return str_buf


if __name__ == "__main__":
    do_main()


