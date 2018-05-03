import os
import yaml

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    ini_file = os.path.join(CURRENT_DIR, "base.yaml")

    with open(ini_file) as f:
        cfg = yaml.load(f)

    print(cfg)
