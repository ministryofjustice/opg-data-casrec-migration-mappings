import json
import os
import re
from typing import Dict
from typing import List

from generate_summary import add_module_to_summary
from config import config
import pandas as pd


pd.options.mode.chained_assignment = None

json_def_config = config['JSON_DEFS']


def apply_column_alias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Some source columns are used multiple times when mapping to the destination.
    This appends a number to the column alias for the duplicates, makes the
    transformations easier as some of the duplicates are handled differently
    """

    df["count"] = df.groupby(json_def_config['source_column_name']).cumcount()
    df["alias"] = df[[json_def_config['source_column_name'], "count"]].values.tolist()
    df["alias"] = df["alias"].apply(
        lambda x: f"{x[0]} {x[1]}" if str(x[0]) != "nan" and int(x[1]) > 0 else x[0]
    )

    return df

def clean_up_and_convert_to_dict(df: pd.DataFrame) -> Dict:
    """
    1.  add the 'alias' col to the dataframe
    2.  only select the columns we are interested in
    3.  add any missing columns with empty string as value
    4.  remove False from 'is_pk' col
    5.  convert 'is_complete' rows to boolean
    6.  change 'is_complete' to true if field is a pk
    7.  change 'is_complete' to true if field is a fk
    8.  drop any rows that have no value in all interesting cols
    9.  fill 'nan' with empty string
    10. set 'include' to True where 'is_complete' is not N/A (ie, means it should
        be mapped even if the mapping is not complete)
    11. force pk fields to be included
    12. force fk link fields to be included
    13. only select the rows where 'include' is True
    14. drop the include col (because it's always True)
    15. set index to the column name so the to_dict pivots on the sirius column name
    16. convert to dictionary
    """

    # add the 'alias' col to the dataframe
    mapping_df = apply_column_alias(df=df)
    # only select the columns we are interested in
    # add any missing columns with empty string as value
    wanted_cols = json_def_config['default_columns'] + [json_def_config['index_column']]
    existing_cols = mapping_df.columns.values.tolist()
    cols_to_select = list(set(wanted_cols) & set(existing_cols))
    cols_to_add = [x for x in wanted_cols if x not in existing_cols]

    mapping_df = mapping_df[cols_to_select]

    for col in cols_to_add:
        mapping_df[col] = ""

    mapping_df["is_complete"] = mapping_df["is_complete"].fillna("NO")
    # set 'include' to True where 'is_complete' is not N/A or empty (ie, means it
    # should be mapped even if the mapping is not complete)
    mapping_df["is_complete"].to_string(na_rep="").lower()

    mapping_df["include"] = mapping_df.apply(
        lambda x: True if x["is_complete"] not in ("not mapped") else False, axis=1
    )

    # # remove nan
    mapping_df = mapping_df.fillna("")
    # print(mapping_df.to_markdown())

    # remove False from 'is_pk' col
    mapping_df["is_pk"] = mapping_df.apply(
        lambda x: True if x["is_pk"] is True else "", axis=1
    )

    # force pk fields to be included
    mapping_df["include"] = mapping_df.apply(
        lambda x: True if x["is_pk"] is True else x["include"], axis=1
    )
    # force fk link fields to be included
    mapping_df["include"] = mapping_df.apply(
        lambda x: True if x["fk_parents"] != "" else x["include"], axis=1
    )
    # convert 'is_complete' rows to boolean: True
    mapping_df["is_complete"] = mapping_df.apply(
        lambda x: True if x["is_complete"] in ["yes", "YES"] else False, axis=1,
    )

    # change 'is_complete' to true if field is a pk
    mapping_df["is_complete"] = mapping_df.apply(
        lambda x: True if x["is_pk"] is True else x["is_complete"], axis=1,
    )
    # change 'is_complete' to true if field is a fk
    mapping_df["is_complete"] = mapping_df.apply(
        lambda x: True if x["fk_parents"] != "" else x["is_complete"], axis=1,
    )

    # drop any rows that have no value in all interesting cols
    mapping_df = mapping_df.dropna(axis=0, how="all", subset=json_def_config['default_columns'])
    # fill 'nan' with empty string
    mapping_df = mapping_df.fillna("")

    # only select the rows where include is True
    mapping_df = mapping_df.loc[mapping_df["include"] == True]
    # drop the include col (because it's always True)
    mapping_df.drop("include", axis=1, inplace=True)

    # set index to the column name so the to_dict pivots on the sirius column name
    mapping_df = mapping_df.set_index(json_def_config['index_column'])
    # convert to dictionary

    mapping_dict = mapping_df.to_dict("index")

    return mapping_dict



def format_multiple_columns(mapping_dict: Dict) -> Dict:
    """
    Some items are across multiple columns in the source data but map to a single
    column in the destination.
    These come out of Excel as a string, we need to convert them to a list.
    Easier to do it once it's a dict than in the dataframe, as the numpy concept of
    'list' doesn't map easily using 'to_dict'!
    """
    multi_fields = [json_def_config['source_column_name'], "alias", "additional_columns"]

    for col, details in mapping_dict.items():
        for field in multi_fields:
            if "\n" in details[field]:
                details[field] = [x.strip() for x in details[field].split("\n")]

    return mapping_dict

def convert_dict_to_new_format(mapping_dict: Dict) -> Dict:
    dirname = os.path.dirname(__file__)
    path = "template"
    file_path = os.path.join(dirname, path, "mapping_template.json")


    with open(file_path, "r") as template_json:
        template_data = template_json.read()
        template_dict = json.loads(template_data)

    from_template = {}
    for k in mapping_dict:
        field = {}
        for stage, details in template_dict.items():
            field[stage] = {
                i: mapping_dict[k][i] for i in details if i in mapping_dict[k]
            }

        from_template[k] = field

    return from_template

def export_single_module_as_json_file(module_name: str, mapping_dict: Dict, destination: str):

    path = f"{destination}"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/{module_name}_mapping.json", "w") as json_out:
        json.dump(mapping_dict, json_out, indent=4)



def generate_json_files(df, name, destination):
    print(f"creating json defs: {name}")
    module_dict = clean_up_and_convert_to_dict(df=df)


    if len(module_dict) > 0:
        module_dict = format_multiple_columns(
            mapping_dict=module_dict
        )

        module_dict = convert_dict_to_new_format(mapping_dict=module_dict)


        export_single_module_as_json_file(
            module_name=name, mapping_dict=module_dict, destination=destination
        )

        add_module_to_summary(module_name=name, mapping_dict=module_dict)