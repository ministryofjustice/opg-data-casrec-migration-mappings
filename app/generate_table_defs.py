import os
import json
import numpy as np

def create_table_def_json(df, name, destination):
    print(f"creating table defs: {name}")
    print(f"name: {name}")

    df = df.replace(np.nan, "")
    df = df.rename(columns={'casrec_conditions': 'source_conditions'})
    df = df.set_index("mapping_file_name")
    table_def_dict = df.to_dict("index")


    convert_col_to_list(column_names=['source_table_additional_columns'], definition_dict=table_def_dict)
    convert_col_to_dict(column_names=['source_conditions'], definition_dict=table_def_dict)

    path = f"./{destination}/tables"

    if not os.path.exists(path):
        os.makedirs(path)

    try:
        with open(f"{path}/table_definitions.json", "r") as json_out:
            data = json_out.read()
            existing_table_defs = json.loads(data)
    except:
        existing_table_defs = {}

    for mapping_file_name, details in table_def_dict.items():
        existing_table_defs[mapping_file_name] = details

    with open(f"{path}/table_definitions.json", "w") as json_write:
        json.dump(existing_table_defs, json_write, indent=4)



def convert_col_to_list(column_names, definition_dict):
    for col, details in definition_dict.items():
        for field in column_names:
            try:
                details[field] = [x.strip() for x in details[field].split(",")]
            except:
                details[field] = [details[field]]

    return definition_dict


def convert_col_to_dict(column_names, definition_dict):
    for col, details in definition_dict.items():
        for field in column_names:
            try:
                conditions = [x.strip() for x in details[field].split(",")]
                details[field] = {x.split('=')[0].strip(): x.split('=')[1].strip() for x in conditions}
            except:
                pass

    return definition_dict