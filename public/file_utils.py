import json


def load_json(path: str, default):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(path, 'w') as f:
            json.dump(default, f, indent=2)
        return default


def store_json(path: str, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def load_txt(path: str):
    try:
        with open(path, 'r') as file:
            lines = [line.strip() for line in file]
            return lines
    except FileNotFoundError:
        with open(path, 'w') as f:
            f.write('')
        return []


def load_json_list(path: str):
    return [json.loads(line) for line in load_txt(path)]


def store_json_list(path: str, json_list: list):
    with open(path, 'w') as f:
        for item in json_list:
            f.write(json.dumps(item))
            f.write('\n')


def append_line(path: str, line: str):
    with open(path, 'a') as f:
        f.write(line)
        f.write('\n')


def append_json_line(path: str, json_dict: dict):
    append_line(path, json.dumps(json_dict))


def load_integer(path: str, default: int):
    try:
        with open(path, 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        with open(path, 'w') as f:
            f.write(default.__str__())
        return default


def store_integer(path: str, integer: int):
    with open(path, 'w') as f:
        f.write(integer.__str__())
