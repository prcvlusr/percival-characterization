import os
import yaml

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

def read_yaml():
    ini_file = os.path.join(CURRENT_DIR, "base.yaml")

    with open(ini_file) as f:
        cfg = yaml.load(f)

    return cfg

def fix_non_entries(config):
  for k, v in config.items():
    if isinstance(v, dict):
      fix_non_entries(v)
    else:
        if v == "None":
            config[k] = None

def convert_none():
    cfg = read_yaml()
    fix_non_entries(cfg)
    print(cfg)

if __name__ == "__main__":
    cfg = read_yaml()
    print(cfg)

    convert_none()
