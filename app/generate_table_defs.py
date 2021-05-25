import os
import pandas as pd

def generate_files(spreadsheet_name):
    dirname = os.path.dirname(__file__)
    path = "mapping_spreadsheet"

    file_path = os.path.join(dirname, "..", path, spreadsheet_name)
    excel_df = pd.ExcelFile(file_path)

    for sheet in excel_df.sheet_names:
        df = pd.read_excel(excel_df, spreadsheet_name=sheet)
        if sheet == 'table_definitions':
            create_table_def_json(table_definition_df=df)
        if 'lookup_table' in sheet:
            create_lookup_table_json(lookup_df=df)



def create_entity_folder(entity_name):
    pass

def create_table_def_json(table_definition_df):
    pass

def create_lookup_table_json(lookup_df):
    pass