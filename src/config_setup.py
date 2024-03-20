import yaml
from cryptography.fernet import Fernet
import os
from getpass import getpass
import subprocess

""" Generate a fernet key"""

path = os.environ.get('HOME')


def genwrite_key(dir):
    key = Fernet.generate_key()
    with open(f'{dir}/pass.key', "wb") as key_file:
        key_file.write(key)


def call_key(dir):
    return open(f'{dir}/pass.key', 'rb').read()


def make_dir(path):
    try:
        config_path = os.path.join(f"{path}/.config", 'lpt')
        os.makedirs(os.path.join(f"{path}/.config", 'lpt'))
    except FileExistsError:
        pass

    return config_path


def create_config():

    dir_path = make_dir(path)

    genwrite_key(dir_path)

    key = call_key(dir_path)
    f = Fernet(key)

    while True:
        username = input('Enter your student email: ').lower()
        slack_password = getpass('Enter your slack password: ')

        if "@student.wethinkcode.co.za" in username and slack_password != "":
            break
        else:

            print("\nPlease make sure you entered the required information")

    user_info = {
        'username': username,
        'slack_password': f.encrypt(slack_password.encode())
    }

    # * write to file
    with open(f'{path}/.config/lpt/config.yml', 'w') as config:
        data = yaml.dump(user_info, config)

    return data


# read from the config file:

def read_config():
    config_path = os.path.join(f"{path}/.config", 'lpt')

    key = call_key(config_path)
    f = Fernet(key)

    with open(f'{config_path}/config.yml', 'r')as configfile:
        try:
            user_config = yaml.safe_load(configfile)
        except yaml.YAMLError as exc:
            print(exc)

    slack_password = f.decrypt(user_config["slack_password"])
    username = user_config["username"]
    return username, slack_password.decode()


def check_selenium_install():
    package_name = "selenium"

    try:
        import pip
    except ModuleNotFoundError:
        subprocess.check_call(["sudo", "apt", "install", "pip"])

    try:
        import selenium
    except ImportError:
        subprocess.check_call(["pip", "install", package_name])
