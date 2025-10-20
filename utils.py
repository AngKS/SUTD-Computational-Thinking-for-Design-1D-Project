import json

def read_data(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}

def write_data(file_path, data: dict) -> bool:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        return True
    return False