import re

def to_snake_case(input_string):
    # Use regular expression to match uppercase letters, and add underscores
    snake_case_result = re.sub(r'([a-z0-9])([A-Z ])', r'\1_\2', input_string)
    # Remove any remaining spaces and convert the result to lowercase
    return snake_case_result.replace(' ', '').lower()
