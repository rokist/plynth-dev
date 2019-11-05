import os
import shutil
import zipfile
import platform

is_mac = platform.system() == "Darwin"

tensorflow_target_dir = "tensorflow_core"

so_list = [
    os.path.join("compiler", "tf2xla", "ops", "_xla_ops.so"),
    os.path.join("lite", "experimental", "microfrontend", "python", "ops", "_audio_microfrontend_op.so"),
    os.path.join("python", "framework", "fast_tensor_util.so"),
    os.path.join("lite", "python", "optimize", "_tensorflow_lite_wrap_calibration_wrapper.pyd"),
    os.path.join("lite", "python", "interpreter_wrapper", "_tensorflow_wrap_interpreter_wrapper.pyd")
]


def __hook_will_build(info):
    if not "skip_module_dirs" in info:
        info["skip_module_dirs"] = []

    info["skip_module_dirs"].append(tensorflow_target_dir)
    info["skip_module_dirs"].append("tensorboard")


def __hook_did_build(info):

    target_packages_dir = info["target_site_packages_path"]
    source_packages_dir = info["source_site_packages_path"]
    plynth_assets_path = info["plynth_assets_path"]
    rebuild_mode = info["rebuild"]

    # {
    # 'hook_name': 'did_build',
    # 'devkit_home': 'C:\\py\\plynth_devkit\\',
    # 'plynth_dir': 'C:\\py\\plynth_devkit\\__plynth',
    # 'dev_scripts_path': 'C:\\py\\plynth_devkit\\__dev_scripts',
    # 'plynth_assets_path': 'C:\\py\\plynth_devkit\\__plynth\\pyassets',
    # 'target_site_packages_path': 'C:\\py\\plynth_devkit\\__plynth\\Lib\\site-packages',
    # 'source_site_packages_path': 'C:\\py\\plynth_devkit\\__plynth_venv\\.venv\\Lib\\site-packages',
    # 'rebuild': False
    # }

    cur_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Uninstall/Unfreezing
    if not os.path.exists(os.path.join(source_packages_dir, tensorflow_target_dir)):
        # Assumed tensorflow has been uninstalled, we are going to clean up

        delete_files = [
            "_pywrap_tensorflow_internal",
            "libtensorflow_framework",
            "tensorflow.zip",
        ]
        
        for so_file in so_list:
            delete_files.append(os.path.basename(so_file))

        for f in os.listdir(plynth_assets_path):
            for file in delete_files:
                if f.startswith(file):
                    filepath = os.path.join(plynth_assets_path, f)
                    if os.path.exists(filepath):
                        os.unlink(filepath)

        workspace_folder = os.path.join(cur_dir, "tensorflow_freezing_workspace")
        if os.path.exists(workspace_folder):
            shutil.rmtree(workspace_folder)

        return

    # Install/Freezing
    try:

        google_init_path = os.path.join(target_packages_dir, "google", "__init__.py")
        if not os.path.exists(google_init_path):
            with open(google_init_path, mode="w") as write_file:
                write_file.write("\n")

        workspace_folder = os.path.join(cur_dir, "tensorflow_freezing_workspace")
        if rebuild_mode and os.path.exists(workspace_folder):
            shutil.rmtree(workspace_folder)

        if not os.path.exists(workspace_folder):
            os.mkdir(workspace_folder)

            tensorflow_workspace = os.path.join(workspace_folder, tensorflow_target_dir)

            shutil.copytree(
                os.path.join(source_packages_dir, tensorflow_target_dir),
                tensorflow_workspace,
            )
            shutil.copytree(
                os.path.join(source_packages_dir, "tensorboard"),
                os.path.join(workspace_folder, "tensorboard"),
            )

            try:
                if os.path.exists(tensorflow_workspace):
                    # Try to remove the include dir
                    if os.path.exists(os.path.join(tensorflow_workspace, "include")):
                        shutil.rmtree(os.path.join(tensorflow_workspace, "include"))
            except Exception as err:
                print(str(err))

            # Replace get_path_to_datafile(path)
            for so_file in so_list:
                target_path = os.path.join(
                    plynth_assets_path, os.path.basename(so_file)
                )
                source_path = os.path.join(tensorflow_workspace, so_file)
                if not os.path.exists(target_path):
                    if os.path.exists(source_path):
                        shutil.move(source_path, target_path)

            resource_loader_text = ""

            with open(
                os.path.join(
                    tensorflow_workspace, "python", "platform", "resource_loader.py"
                )
            ) as target_file:
                lines = target_file.readlines()

                for line in lines:
                    if "def get_path_to_datafile(path):" in line:
                        space = line[0 : line.index("def get_path_to_datafile(path):")]
                        resource_loader_text += (
                            space + "def get_path_to_datafile(path):\n"
                        )
                        resource_loader_text += space + "    import os as __os__\n"
                        resource_loader_text += space + "    import sys as __sys__\n"
                        if is_mac:
                            resource_loader_text += (
                                space
                                + '    return __os__.path.join(__os__.path.dirname(__sys__.executable), "lib", "pyassets", path)\n'
                            )
                        else:
                            resource_loader_text += (
                                space
                                + '    return __os__.path.join(__os__.path.dirname(__sys__.executable), "pyassets", path)\n'
                            )


                        resource_loader_text += space + "def _dummy_plynth_(path):\n"
                    else:
                        resource_loader_text += line

            if resource_loader_text:
                with open(
                    os.path.join(
                        tensorflow_workspace, "python", "platform", "resource_loader.py"
                    ),
                    mode="w",
                ) as write_file:
                    write_file.write(resource_loader_text)

            def move_file(file_name):
                if os.path.exists(
                    os.path.join(tensorflow_workspace, "python", file_name)
                ):
                    if os.path.exists(os.path.join(plynth_assets_path, file_name)):
                        os.unlink(os.path.join(plynth_assets_path, file_name))

                    shutil.move(
                        os.path.join(tensorflow_workspace, "python", file_name),
                        plynth_assets_path,
                    )

            def move_file2(prefix):
                for filename in os.listdir(tensorflow_workspace):
                    if filename.startswith(prefix):
                        if os.path.exists(os.path.join(tensorflow_workspace, filename)):
                            if os.path.exists(
                                os.path.join(plynth_assets_path, filename)
                            ):
                                os.unlink(os.path.join(plynth_assets_path, filename))

                            shutil.move(
                                os.path.join(tensorflow_workspace, filename),
                                plynth_assets_path,
                            )

            # for windows
            move_file("_pywrap_tensorflow_internal.lib")
            move_file("_pywrap_tensorflow_internal.pyd")

            # for mac
            move_file("_pywrap_tensorflow_internal.so")
            move_file2("libtensorflow_framework")

            def zipdir(path, ziph, top_name):
                for cur, dirs, files in os.walk(path):
                    for file in files:
                        basename = os.path.basename(cur)
                        if basename == "__pycache__":
                            continue

                        arcname = os.path.join(
                            top_name, os.path.relpath(cur, path), file
                        )

                        if arcname:
                            ziph.write(os.path.join(cur, file), arcname=arcname)

            full_file_name = os.path.join(plynth_assets_path, "tensorflow.zip")

            zipf = zipfile.ZipFile(full_file_name, "w", zipfile.ZIP_DEFLATED)
            zipdir(
                os.path.join(workspace_folder, tensorflow_target_dir),
                zipf,
                tensorflow_target_dir,
            )
            zipdir(os.path.join(workspace_folder, "tensorboard"), zipf, "tensorboard")
            zipf.close()

    except Exception as err:
        print(str(err))
