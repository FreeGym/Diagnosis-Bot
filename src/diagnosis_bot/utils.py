import re
import json
from typing import Dict

def to_snake_case(input_string : str) -> str:
    snake_case_result = re.sub(r'([a-z0-9])([A-Z ])', r'\1_\2', input_string)
    return snake_case_result.replace(' ', '').lower()

def save_json(raw_json_string, file_path) -> str:            
    try:
        data = json.loads(raw_json_string)
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f'JSON data has been written to {file_path}')
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
    return ""