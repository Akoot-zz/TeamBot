import json


def write_json(data, path: str):
    with open(path, 'w') as json_file:
        json.dump(data, json_file)


def load_json(path: str):
    # Read json file
    with open(path, 'r') as json_file:
        data = json_file.read()

    # Convert to a json object
    return json.loads(data)
