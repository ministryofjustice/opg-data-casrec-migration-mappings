import os
import json

def create_table_def_json(df, name, destination):
    print(f"creating table defs: {name}")

    df = df.set_index("mapping_file_name")
    table_def_dict = df.to_dict("index")

    for mapping_file_name, details in table_def_dict.items():

        path = f"./{destination}/{mapping_file_name}"
    
        if not os.path.exists(path):
            os.makedirs(path)


        with open(f"{path}/{name}.json", "w") as json_out:
            json.dump(details, json_out, indent=4)