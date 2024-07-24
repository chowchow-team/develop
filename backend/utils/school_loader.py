import json
import os
from django.conf import settings

def load_school_choices(filename='domain.json'):
    file_path = os.path.join(settings.BASE_DIR, 'utils', filename)
    with open(file_path, 'r') as file:  # file_path로 변경
        data = json.load(file)
        return [(str(item['id']), item['name']) for item in data]
    
def load_schools_from_json(filename='domain.json'):
    file_path = os.path.join(settings.BASE_DIR, 'utils', filename)
    with open(file_path, 'r') as file:  # file_path로 변경
        return json.load(file)