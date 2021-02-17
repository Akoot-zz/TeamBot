import json


def write_json(json_object, path: str):
    with open(path, 'w') as json_file:
        json_file.write(json_object)


def load_json(path: str):
    # Read json file
    with open(path, 'r') as auth_file:
        data = auth_file.read()

    # Convert to a json object
    return json.loads(data)
