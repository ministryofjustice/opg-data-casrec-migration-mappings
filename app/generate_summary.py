import os
import json

def get_existing_summary():
    path = "./mapping_definitions/summary/"

    with open(f"{path}/mapping_progress_summary.json", "r") as json_in:
        summary_data = json_in.read()
        return json.loads(summary_data)

def export_summary_as_json_file(summary_data):
    path = "./mapping_definitions/summary/"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/mapping_progress_summary.json", "w") as json_out:
        json.dump(summary_data, json_out, indent=4)

def generate_worksheet_data(module_name, mapping_dict):



    module_total_rows = len(mapping_dict)

    module_total_unmapped_rows = len(
        [k for k, v in mapping_dict.items() if v['mapping_status']["is_complete"] is not True]
    )
    module_total_mapped_rows = module_total_rows - module_total_unmapped_rows
    try:
        module_percentage_complete = round(
            module_total_mapped_rows / module_total_rows * 100
        )
    except ZeroDivisionError:
        module_percentage_complete = 0

    worksheet_data = {}
    worksheet_data["total_rows"] = module_total_rows
    worksheet_data[
        "total_unmapped"
    ] = module_total_unmapped_rows
    worksheet_data[
        "total_mapped"
    ] = module_total_mapped_rows
    worksheet_data[
        "percentage_complete"
    ] = module_percentage_complete

    # print(json.dumps(worksheet_data, indent=4))
    return worksheet_data

def update_totals(worksheet_data, module_name, existing_total):

    fields = existing_total["fields"]
    sheets = existing_total["worksheets"]

    fields["total_fields"] += worksheet_data["total_rows"]
    fields["total_unmapped"] += worksheet_data["total_unmapped"]
    fields["total_mapped"] += worksheet_data["total_mapped"]
    try:
        fields["percentage_complete"] = round(
            fields["total_mapped"] / fields["total_fields"] * 100
        )
    except ZeroDivisionError:
        fields["percentage_complete"] = 0

    sheets["total_sheets"] += 1
    sheets["total_complete"] = (
        sheets["total_complete"] + 1 if worksheet_data["percentage_complete"] == 100 else +0
    )

    # print(json.dumps(existing_total, indent=4))
    return existing_total

def get_summary():
    try:
        summary = get_existing_summary()
    except:
        summary = {
            "worksheets": {
            },
            "total": {
                "worksheets": {
                    "total_sheets": 0,
                    "total_complete": 0
                },
                "fields": {
                    "total_fields": 0,
                    "total_unmapped": 0,
                    "total_mapped": 0,
                    "percentage_complete": 0
                }
            }
            }

    return summary

def add_module_to_summary(module_name, mapping_dict):

    summary = get_summary()
    worksheet_data = generate_worksheet_data(module_name, mapping_dict)
    summary['worksheets'][module_name] = worksheet_data
    summary['total'] = update_totals(worksheet_data, module_name, existing_total=summary['total'])

    # print(json.dumps(summary, indent=4))

    export_summary_as_json_file(summary_data=summary)