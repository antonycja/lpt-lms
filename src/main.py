import os
from logic import run_script, delete_tmp_files, tmp_file_path
from config_setup import create_config, path
import lpt_lms

# TODO: Import the config

config_path = f'{path}/.config/lpt/config.yml'
# TODO: Tmp path


def run_lms_script() -> None:
    """Check if the config file exists in the directory, if it doesn't, go through the configuration process then run the slack script.
    """
    global message
    try:
        os.makedirs(tmp_file_path)
    except FileExistsError:
        pass

    if os.path.exists(config_path):

        if len(os.listdir(tmp_file_path)) == 0:
            message = lpt_lms.run()
        else:
            message = lpt_lms.return_message()
        run_script(os)

    else:
        create_config()
        if len(os.listdir(tmp_file_path)) == 0:
            message = lpt_lms.run()
        else:
            message = lpt_lms.return_message()
        run_script(os)


if __name__ == "__main__":

    print()
    run_lms_script()
    lpt_lms.messenger(message)
    delete_tmp_files(os)
