import re
import json
from typing import Dict

def to_snake_case(input_string : str) -> str:
    snake_case_result = re.sub(r'([a-z0-9])([A-Z ])', r'\1_\2', input_string)
    return snake_case_result.replace(' ', '').lower()

