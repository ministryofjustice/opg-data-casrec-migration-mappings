import os
import re
from pathlib import Path

from config import config
from generate_all_files import  generate_files




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


def loop_through_files():

    for mapping_file in os.listdir(config['SPREADSHEET_PATH']):
        print(f"mapping_file: {mapping_file}")
        if os.path.isfile(os.path.join(config['SPREADSHEET_PATH'], mapping_file)):
            if mapping_file[:2] != '~$':
                entity_name = get_entity_name_from_file(file_name=mapping_file)
                entity_file_path = create_entity_folder(entity_name=entity_name)
                generate_files(spreadsheet_name=mapping_file, destination=entity_file_path)


loop_through_files()


