import os
import sys
import json
import importlib
from glob import glob


# syntax:
# pdk script a_script
# pdk script mymodule.script1
def invoke_script(args):

    if not args:
        print("No args")
        return

    invoked = False

    # Call a function from pdk_conf.py
    script_name = args[0]
    if hasattr(pdk_conf, script_name):
        func = getattr(pdk_conf, script_name)
        if callable(func):
            invoked = True
            func({})

    # Call module.func in __dev_scripts
    if (not invoked) and ('.' in script_name):
        terms = script_name.split(".")
        if len(terms) > 1:
            mod_name, func_name = terms[0], terms[1]

            try:
                mod = importlib.import_module(mod_name)
                if mod and hasattr(mod, func_name):
                    func = getattr(mod, func_name)
                    if callable(func):
                        invoked = True
                        func({})
            except Exception as err:
                print(str(err))
    
    if not invoked:
        print("failed to invoke script.")


def call_hook(hook_name, info_dict):
    # inside pdk_conf.py
    # top_levels = dir(pdk_conf)
    # for top_level in top_levels:
    #     if not top_level.startswith("__"):
    #         func = getattr(pdk_conf, top_level)
    #         print(top_level)
        

    # for package_path in sys.path:
    #     if "site-packages" in package_path:
    #         print(package_path)
    #         for modname in os.listdir(package_path):
    #             mod_path = os.path.join(package_path, modname)
    #             if os.path.isdir(mod_path) \
    #                 and not '.' in modname \
    #                 and not modname.startswith('__'):
    #                 try:
    #                     print(modname)
    #                     mod = importlib.import_module(modname)
    #                     #print(dir(mod))
    #                     #b = importlib.import_module(modname, package=a)
    #                 except Exception as err:
    #                     print(str(err))

    #for x in glob(os.path.join(os.path.dirname(__file__), "..", "__dev_scripts", "*.py")):
    for p in get_scripts_path():
        for x in glob(os.path.join("..", p, "*.py")):
            if (not x.startswith('__')) and len(x) > 4:
                modname = os.path.basename(x)[:-3]
                if modname != "__init__":
                    #print(modname)
                    try:
                        mod = importlib.import_module(modname)
                        hook_func_name = "__hook_" + hook_name
                        if hasattr(mod, hook_func_name):
                            func = getattr(mod, hook_func_name)
                            if callable(func):
                                func(info_dict)
                    except Exception as err:
                        print(str(err))


def get_scripts_path():
    try:
        return pdk_conf.scripts_path()
    except:
        return os.path.join("..", "__dev_scripts")


if __name__ == "__main__":
    sys.path.append("..")
    import pdk_conf

    try:
        for path in pdk_conf.scripts_path():
            import_path = os.path.join("..", path)
            if os.path.exists(import_path):
                sys.path.append(import_path)
    except Exception as e:
        print(str(e))
        sys.path.append(os.path.join("..", "__dev_scripts"))


    if sys.argv[1] == "call_hook":
        hook_name = sys.argv[2]
        filename = sys.argv[3]
        try:
            file_path = os.path.join(".pass_args_dir", filename)

            arg_dict = {}
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf8") as f:
                    arg_dict = json.load(f)

            call_hook(hook_name, arg_dict)

            if os.path.exists(file_path):
                with open(file_path, mode="w") as write_file:
                    json.dump(arg_dict, write_file)

        finally:
            pass
            #if os.path.exists(file_path):
                #os.unlink(file_path)

    if sys.argv[1] == "invoke_script":
        invoke_script(sys.argv[2:])
