
config = {
    "SPREADSHEET_PATH" : "mapping_spreadsheet",
    "DEFINITION_PATH" : "mapping_definitions",
    "JSON_DEFS": {
        "index_column": "column_name",
        "source_column_name" : "casrec_column_name",
        "default_paths" : {
            "mapping_spreadsheet": "./mapping_spreadsheet/",
            "json_template": "./app/template",
            "mapping_definitions_output": "./mapping_definitions",
            "lookup_tables_output": "./mapping_definitions/lookups",
            "summary_output": "./mapping_definitions/summary",
        },
        "default_columns" : [
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
    }
}
