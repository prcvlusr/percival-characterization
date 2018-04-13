import configparser
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    ini_file = os.path.join(CURRENT_DIR, "base.ini")

    read_config = configparser.ConfigParser()
    read_config.read(ini_file)

    config = {}
    for section, sec_value in read_config.items():
        if section not in config:
            config[section] = {}
        for key, key_value in sec_value.items():
            config[section][key] = key_value

    print(config)
