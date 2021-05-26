import os
import pandas as pd
from pathlib import Path

from app.generate_json_def import generate_json_files
from app.generate_lookup_table_json import create_lookup_table_json
from app.generate_table_defs import create_table_def_json


def generate_files(spreadsheet_name):
    dirname = os.path.dirname(__file__)
    path = "mapping_spreadsheet"

    file_path = os.path.join(dirname, "..", path, spreadsheet_name)
    excel_df = pd.ExcelFile(file_path)

    for sheet in excel_df.sheet_names:
        df = pd.read_excel(excel_df, spreadsheet_name=sheet)
        if sheet == 'table_definitions':
            create_table_def_json(table_definition_df=df)
        elif 'lookup_table' in sheet:
            create_lookup_table_json(df=df, name=sheet)
        else:
            generate_json_files(df=df, name=sheet)



def create_entity_folder(entity_name):
    try:
        Path(f"/mapping_definitions_new/{entity_name}").mkdir(parents=True, exist_ok=True)
        print(f"Folder '{entity_name}' created")
    except Exception as e:
        print(f"e: {e}")