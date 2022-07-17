import yaml
import os

YAML_PATH = "/home/pi/dudebot/dudebot_config.yaml"

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

#loads all yaml file params
def load_yaml(fn):
    if not os.path.exists(fn):
        dump_yaml({}, fn)
    file = open(fn, "r")
    state = yaml.safe_load(file)
    return state

#writes to all yaml file params
def dump_yaml(dict, fn):
    file = open(fn, "w")
    yaml.dump(dict, file, default_flow_style=False, Dumper=NoAliasDumper)

#sets a particular key-value pair
def set_param(name, value, fn=YAML_PATH):
    state = load_yaml(fn)
    if state is None:
        state = {}
    state[name] = value
    dump_yaml(state, fn)

#returns a particular key-value pair
def get_param(name, default=None, fn=YAML_PATH):
    state = load_yaml(fn)
    if state and name in state:
        return state[name]
    print(f"Failed to get parameter {name}, using default: {default}")
    set_param(name, default, fn)
    return default


def main():
    print("This is the main program!")
    x = get_param("DUDEBOT_TOKEN", None)
    print(x)


if __name__ == "__main__":
    main()