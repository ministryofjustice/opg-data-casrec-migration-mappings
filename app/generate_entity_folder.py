import os
from config import config


def get_entity_name_from_file(file_name):
    try:
        entity_name = file_name[24:][:-5].lower()

        print(f"starting entity: {entity_name}")
        return entity_name

    except Exception:
        print(f"problem getting entity name from '{file_name}' {e}")


def create_entity_folder(entity_name):
    try:
        path = f"./{config['DEFINITION_PATH']}/{entity_name}"

        if not os.path.exists(path):
            os.makedirs(path)
        print(f"Folder '{entity_name}' created")
        return path
    except Exception as e:
        print(f"e: {e}")