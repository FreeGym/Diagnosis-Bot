import json

def load_medical_professionals(file_path='data/medical_professionals.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data