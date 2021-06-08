import os
import shutil

from generate_entity_folder import get_entity_name_from_file, create_entity_folder
from config import config
from generate_all_files import generate_files



def remove_old_files():

    path = f"./{config['DEFINITION_PATH']}"

    try:
        shutil.rmtree(path)


    except Exception as e:
        print(f"e: {e}")


def loop_through_files():

    remove_old_files()

    for mapping_file in os.listdir(config['SPREADSHEET_PATH']):
        # if mapping_file == 'Casrec_Mapping_Document_Bond.xlsx':
        if os.path.isfile(os.path.join(config['SPREADSHEET_PATH'], mapping_file)):
            if mapping_file[:2] != '~$':
                print(f"mapping_file: {mapping_file}")
                entity_name = get_entity_name_from_file(file_name=mapping_file)
                entity_file_path = create_entity_folder(entity_name=entity_name)
                generate_files(spreadsheet_name=mapping_file, destination=entity_file_path)


# loop_through_files()


