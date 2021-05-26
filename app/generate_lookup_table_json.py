import json
import os

def create_lookup_table_json(df, name):
    df = df[["casrec_code", "sirius_mapping"]]
    # df = df.dropna()
    df = df.fillna("")
    df = df.set_index("casrec_code")
    lookup_dict = df.to_dict("index")

    path = self.paths["lookup_tables_output"]

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/{name}.json", "w") as json_out:
        json.dump(lookup_dict, json_out, indent=4)

