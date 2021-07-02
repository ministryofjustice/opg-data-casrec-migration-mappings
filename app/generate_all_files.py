import os
import pandas as pd


from config import config

from generate_json_def import generate_json_files
from generate_lookup_table_json import create_lookup_table_json
from generate_table_defs import create_table_def_json


def generate_files(spreadsheet_name, destination):
    print(f"spreadsheet_name: {spreadsheet_name}")
    dirname = os.path.dirname(__file__)

    file_path = os.path.join(dirname, "..", config['SPREADSHEET_PATH'], spreadsheet_name)
    excel_df = pd.ExcelFile(file_path)

    for sheet in excel_df.sheet_names:
        print(f"sheet: {sheet}")
        df = pd.read_excel(excel_df, sheet_name=sheet)
        if 'table_definition' in sheet:
            create_table_def_json(df=df, name=sheet, destination=destination)
        elif 'lookup' in sheet:
            create_lookup_table_json(df=df, name=sheet, destination=destination)
        else:
            generate_json_files(df=df, name=sheet, destination=destination)
