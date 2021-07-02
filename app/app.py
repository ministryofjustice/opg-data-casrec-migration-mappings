import filecmp

import click as click

from run import loop_through_files
from helper import assume_aws_session
from mapping_all_sheets import Mapping
from upload_to_s3 import extract_zip
from upload_to_s3 import get_latest_version
from upload_to_s3 import pull_latest_merged
from upload_to_s3 import report_recursive
from upload_to_s3 import upload_file
from upload_to_s3 import zip_dir


@click.command()
@click.option("--new_format", default=True)
@click.option("--ci_stage", default="pull_request")
@click.option("--role", default="operator")
@click.option("--local", default=False)
def main(new_format, ci_stage, role, local):

    loop_through_files()

    # mapping_doc_name = "Casrec_Mapping_Document.xlsx"
    #
    # mapping = Mapping(mapping_doc_name=mapping_doc_name, new_format=new_format,)
    # mapping.generate_json_files()

    if not local:

        dirs_to_zip = ["mapping_spreadsheet", "mapping_definitions"]
        if ci_stage == "pull_request":
            s3_folder = "staged"
        elif ci_stage == "merge_main":
            s3_folder = "merged"
        else:
            print("Unknown stage")

        zip_file_pre = "mappings"
        ext = ".zip"
        zip_file = f"{zip_file_pre}{ext}"
        account = "288342028542"
        previous_folder = "mapping_definitions_previous"
        bucket_name = "casrec-migration-mappings-development"
        s3_file_path = f"{s3_folder}/{zip_file_pre}{ext}"
        s3_session = assume_aws_session(account, role)
        s3 = s3_session.client("s3")
        output_file = "./mapping_definitions/summary/file_diffs.txt"

        pull_latest_merged(bucket_name, s3, zip_file)
        extract_zip(zip_file, previous_folder)

        directory_comparison = filecmp.dircmp(
            "mapping_definitions_previous/mapping_definitions", "mapping_definitions"
        )
        report_recursive(directory_comparison, output_file)

        zip_dir(dirs_to_zip, zip_file)
        upload_file(bucket_name, zip_file, s3, s3_file_path)
        print(get_latest_version(bucket_name, s3_file_path, s3))


if __name__ == "__main__":

    main()
