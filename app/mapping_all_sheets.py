import json
import os
import re
from typing import Dict
from typing import List

import pandas as pd


pd.options.mode.chained_assignment = None


class Mapping:
    def __init__(
        self,
        mapping_doc_name: str,
        columns: List[str] = [],
        new_format: bool = False,
        file_paths: dict = {},
    ):

        self.default_paths = {
            "mapping_spreadsheet": "./mapping_spreadsheet/",
            "json_template": "./app/template",
            "mapping_definitions_output": "./mapping_definitions",
            "lookup_tables_output": "./mapping_definitions/lookups",
            "summary_output": "./mapping_definitions/summary",
        }

        self.paths = file_paths if len(file_paths) > 0 else self.default_paths
        self.excel_doc = mapping_doc_name
        self.index_column = "column_name"
        self.source_column_name = "casrec_column_name"
        self.lookup_table_name = "lookup"
        self.new_format = new_format
        self.default_columns = [
            "casrec_table",
            "casrec_column_name",
            "alias",
            "requires_transformation",
            "lookup_table",
            "default_value",
            "calculated",
            "additional_columns",
            "is_pk",
            "data_type",
            "table_name",
            # 'fk_children',
            "fk_parents",
            "is_complete",
            "entity",
            "sync"
        ]
        self.columns = columns if len(columns) > 0 else self.default_columns
        self.summary = {}

    def _apply_column_alias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Some source columns are used multiple times when mapping to the destination.
        This appends a number to the column alias for the duplicates, makes the
        transformations easier as some of the duplicates are handled differently
        """

        df["count"] = df.groupby(self.source_column_name).cumcount()
        df["alias"] = df[[self.source_column_name, "count"]].values.tolist()
        df["alias"] = df["alias"].apply(
            lambda x: f"{x[0]} {x[1]}" if str(x[0]) != "nan" and int(x[1]) > 0 else x[0]
        )

        return df

    def _clean_up_and_convert_to_dict(self, df: pd.DataFrame) -> Dict:
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
        mapping_df = self._apply_column_alias(df=df)
        # only select the columns we are interested in
        # add any missing columns with empty string as value
        wanted_cols = self.columns + [self.index_column]
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
        mapping_df = mapping_df.dropna(axis=0, how="all", subset=self.columns)
        # fill 'nan' with empty string
        mapping_df = mapping_df.fillna("")

        # only select the rows where include is True
        mapping_df = mapping_df.loc[mapping_df["include"] == True]
        # drop the include col (because it's always True)
        mapping_df.drop("include", axis=1, inplace=True)

        # set index to the column name so the to_dict pivots on the sirius column name
        mapping_df = mapping_df.set_index(self.index_column)
        # convert to dictionary
        mapping_dict = mapping_df.to_dict("index")

        return mapping_dict

    def _add_single_module_details_to_summary(
        self, module_name: str, mapping_dict: dict
    ):

        module_total_rows = len(mapping_dict)

        module_total_unmapped_rows = len(
            [k for k, v in mapping_dict.items() if v["is_complete"] is not True]
        )
        module_total_mapped_rows = module_total_rows - module_total_unmapped_rows
        try:
            module_percentage_complete = round(
                module_total_mapped_rows / module_total_rows * 100
            )
        except ZeroDivisionError:
            module_percentage_complete = 0

        self.summary["worksheets"][module_name] = {}
        self.summary["worksheets"][module_name]["total_rows"] = module_total_rows
        self.summary["worksheets"][module_name][
            "total_unmapped"
        ] = module_total_unmapped_rows
        self.summary["worksheets"][module_name][
            "total_mapped"
        ] = module_total_mapped_rows
        self.summary["worksheets"][module_name][
            "percentage_complete"
        ] = module_percentage_complete

        fields = self.summary["total"]["fields"]
        sheets = self.summary["total"]["worksheets"]

        fields["total_fields"] += module_total_rows
        fields["total_unmapped"] += module_total_unmapped_rows
        fields["total_mapped"] += module_total_mapped_rows
        try:
            fields["percentage_complete"] = round(
                fields["total_mapped"] / fields["total_fields"] * 100
            )
        except ZeroDivisionError:
            fields["percentage_complete"] = 0

        sheets["total_sheets"] += 1
        sheets["total_complete"] = (
            sheets["total_complete"] + 1 if module_percentage_complete == 100 else +0
        )

    def _format_multiple_columns(self, mapping_dict: Dict) -> Dict:
        """
        Some items are across multiple columns in the source data but map to a single
        column in the destination.
        These come out of Excel as a string, we need to convert them to a list.
        Easier to do it once it's a dict than in the dataframe, as the numpy concept of
        'list' doesn't map easily using 'to_dict'!
        """
        multi_fields = [self.source_column_name, "alias", "additional_columns", "sync"]

        for col, details in mapping_dict.items():
            for field in multi_fields:
                if "\n" in details[field]:
                    details[field] = [x.strip() for x in details[field].split("\n")]

        return mapping_dict

    def _convert_sheet_name_to_module_name(self, sheet_name: str) -> str:
        """
        Excel sheet names are for humans.
        """
        return sheet_name.replace(" ", "_").replace("(", "").replace(")", "").lower()

    def get_sheets_as_dataframes(self) -> List[Dict[str, pd.DataFrame]]:
        """
        We need to process each sheet individually
        """
        dirname = os.path.dirname(__file__)
        path = "mapping_spreadsheet"

        all_sheets = []

        for mapping_file in os.listdir(path):
            if os.path.isfile(os.path.join(path, mapping_file)):
                if mapping_file[:2] != '~$':
                    file_path =  os.path.join(dirname, "..", path, mapping_file)
                    excel_df = pd.ExcelFile(file_path)

                    all_sheets_single_file = [
                        {
                            self._convert_sheet_name_to_module_name(sheet): pd.read_excel(
                                excel_df, sheet_name=sheet
                            )
                        }
                        for sheet in excel_df.sheet_names
                    ]

                all_sheets += all_sheets_single_file

        return all_sheets

    def export_single_module_as_json_file(self, module_name: str, mapping_dict: Dict):
        path = self.paths["mapping_definitions_output"]

        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/{module_name}_mapping.json", "w") as json_out:
            json.dump(mapping_dict, json_out, indent=4)

    def export_summary_as_json_file(self):
        path = self.paths["summary_output"]

        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/mapping_progress_summary.json", "w") as json_out:
            json.dump(self.summary, json_out, indent=4)

    def _convert_lookup_to_dict(self, name, df):
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

    def _convert_dict_to_new_format(self, mapping_dict: Dict) -> Dict:
        dirname = os.path.dirname(__file__)
        path = "template"
        file_path = os.path.join(dirname, path, "mapping_template.json")

        #
        # path = self.paths["json_template"]
        # file_path = f"{path}/mapping_template.json"

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

    def generate_json_files(self):
        dirname = os.path.dirname(__file__)
        path = "template"
        file_path = os.path.join(dirname, path, "summary_template.json")

        with open(file_path, "r") as template_json:
            template_data = template_json.read()
            self.summary = json.loads(template_data)

        all_modules = self.get_sheets_as_dataframes()

        for module in all_modules:
            for name, df in module.items():
                print(f"generating {name}")
                if self._table_name in name:
                    self._convert_lookup_to_dict(name, df)
                else:
                    module_dict = self._clean_up_and_convert_to_dict(df=df)

                    self._add_single_module_details_to_summary(
                        module_name=name, mapping_dict=module_dict
                    )
                    if len(module_dict) > 0:
                        module_dict = self._format_multiple_columns(
                            mapping_dict=module_dict
                        )

                        if self.new_format:
                            module_dict = self._convert_dict_to_new_format(
                                mapping_dict=module_dict
                            )

                        self.export_single_module_as_json_file(
                            module_name=name, mapping_dict=module_dict
                        )
        self.export_summary_as_json_file()
