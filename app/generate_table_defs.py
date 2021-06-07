import os
import json
import numpy as np

def create_table_def_json(df, name, destination):
    print(f"creating table defs: {name}")
    print(f"name: {name}")

    df = df.replace(np.nan, "")
    df = df.set_index("mapping_file_name")
    table_def_dict = df.to_dict("index")


    convert_cell_to_list(column_names=['source_table_additional_columns'], definition_dict=table_def_dict)


    for mapping_file_name, details in table_def_dict.items():

        path = f"./{destination}/{mapping_file_name}"
    
        if not os.path.exists(path):
            os.makedirs(path)


        with open(f"{path}/{name}.json", "w") as json_out:
            json.dump(details, json_out, indent=4)


def convert_cell_to_list(column_names, definition_dict):
    for col, details in definition_dict.items():
        for field in column_names:
            print(f"field: {field}")
            try:
                details[field] = [x.strip() for x in details[field].split("\n")]
            except:
                details[field] = [details[field]]

    return definition_dict