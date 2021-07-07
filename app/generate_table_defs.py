import os
import json
import numpy as np

def create_table_def_json(df, name, destination):
    print(f"creating table defs: {name}")
    print(f"name: {name}")

    df = df.replace(np.nan, "")
    df = df.rename(columns={'casrec_conditions': 'source_conditions'})
    df = df.set_index("mapping_file_name")

    try:
        df = df.drop(columns='Unnamed: 8')
    except:
        pass
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
        json.dump(existing_table_defs, json_write, indent=4, sort_keys=True)



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
                conditions = [x for x in details[field].split("\n")]
                condition_details = {}
                for condition in conditions:
                    key = condition.split('=')[0].strip()
                    raw_val = condition.split('=')[1].strip()
                    try:
                        val = json.loads(raw_val)
                    except:
                        val = raw_val

                    condition_details[key] = val
                details[field] = condition_details
            except Exception as e:
                print(e)
                pass
    return definition_dict


