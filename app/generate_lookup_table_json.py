import json
import os

def create_lookup_table_json(df, name, destination):
    print(f"creating lookup file: {name}")
    df = df[["casrec_code", "sirius_mapping"]]
    df = df.fillna("")
    df = df.set_index("casrec_code")
    lookup_dict = df.to_dict("index")

    path = f"./{destination}/lookups"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/{name}.json", "w") as json_out:
        json.dump(lookup_dict, json_out, indent=4)

