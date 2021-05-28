import os


from generate_entity_folder import get_entity_name_from_file, create_entity_folder
from config import config
from generate_all_files import generate_files






def loop_through_files():

    for mapping_file in os.listdir(config['SPREADSHEET_PATH']):
        print(f"mapping_file: {mapping_file}")
        if os.path.isfile(os.path.join(config['SPREADSHEET_PATH'], mapping_file)):
            if mapping_file[:2] != '~$':
                entity_name = get_entity_name_from_file(file_name=mapping_file)
                entity_file_path = create_entity_folder(entity_name=entity_name)
                generate_files(spreadsheet_name=mapping_file, destination=entity_file_path)


loop_through_files()


