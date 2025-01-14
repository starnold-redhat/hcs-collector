"""
TODO
"""

import csv
import shutil
import os
import subprocess
import json
from datetime import datetime
from setup_env import setup_env
from execution import process_mw
from execution import process_rhel
from execution import process_virt
from execution import process_rhel_addons
from execution import process_rhel_vdc
from execution import collect_tags
from execution import process_ansible
from execution import process_rhel_versions


def initial_directory_setup():
    """
    TODO
    """
    print("initial directory setup")
    CURRENT_YEAR = str(datetime.now().strftime('%Y'))
    CURRENT_MONTH = str(datetime.now().strftime('%m'))
    CURRENT_DAY = str(datetime.now().strftime('%d'))

    base_dir = setup_env.view_current_conf()['base_dir']

    CURRENT_YEAR_DIR = base_dir + "/" + CURRENT_YEAR
    CURRENT_MONTH_DIR = CURRENT_YEAR_DIR + "/" + CURRENT_MONTH
    CURRENT_JSON_DIR = CURRENT_MONTH_DIR + "/" + "JSON"
    CURRENT_CSV_DIR = CURRENT_MONTH_DIR + "/" + "CSV"

    if not os.path.exists(CURRENT_YEAR_DIR):
        print("dir {} it's not there yet, creating ...".format(CURRENT_YEAR_DIR))
        os.makedirs(CURRENT_YEAR_DIR)

    if not os.path.exists(CURRENT_MONTH_DIR):
        print("dir {} it's not there yet, creating ...".format(CURRENT_MONTH_DIR))
        os.makedirs(CURRENT_MONTH_DIR)

    if not os.path.exists(CURRENT_JSON_DIR):
        print("dir {} it's not there yet, creating ...".format(CURRENT_JSON_DIR))
        os.makedirs(CURRENT_JSON_DIR)

    if not os.path.exists(CURRENT_CSV_DIR):
        print("dir {} it's not there yet, creating ...".format(CURRENT_CSV_DIR))
        os.makedirs(CURRENT_CSV_DIR)

    # At this moment keeping the hard code path
    CSV_FILE = "/tmp/match_inv_sw.csv"
    JSON_FILE_INV = "/tmp/inventory.json"
    JSON_FILE_SWATCH = "/tmp/swatch.json"
    ANSIBLE_USAGE_FILE = "/tmp/ansible.json"

    DEST_CSV_FILE = CURRENT_CSV_DIR + "/" + "match_inv_sw_" + CURRENT_MONTH + "-" + CURRENT_DAY + "-" + CURRENT_YEAR + ".csv"
    DEST_JSON_FILE_INV = CURRENT_JSON_DIR + "/" + "inventory_" + CURRENT_MONTH + "-" + CURRENT_DAY + "-" + CURRENT_YEAR + ".json"
    DEST_JSON_FILE_SWATCH = CURRENT_JSON_DIR + "/" + "swatch_" + CURRENT_MONTH + "-" + CURRENT_DAY + "-" + CURRENT_YEAR + ".json"
    DEST_JSON_FILE_ANSIBLE = CURRENT_JSON_DIR + "/" + "ansible_" + CURRENT_MONTH + "-" + CURRENT_DAY + "-" + CURRENT_YEAR + ".json"

    crhc_cli = setup_env.view_current_conf()['crhc_cli']
    print(crhc_cli)

    print("Cleaning the current cache files")
    os.system(crhc_cli + " ts clean")

    print("Downloading and creating the new match info")
    os.system(crhc_cli + " ts dump_current")
    os.system(crhc_cli + " ts match")
    shutil.copy(CSV_FILE, DEST_CSV_FILE)
    shutil.copy(JSON_FILE_INV, DEST_JSON_FILE_INV)
    shutil.copy(JSON_FILE_SWATCH, DEST_JSON_FILE_SWATCH)
    collect_tags.append_tags_to_inventory_json(DEST_JSON_FILE_INV, crhc_cli)
    collect_tags.append_tags_to_inventory_csv(DEST_CSV_FILE, crhc_cli)
    print("Downloading the ansible info")
    os.system(crhc_cli + " ansible unique_hosts > " + ANSIBLE_USAGE_FILE)
    shutil.copy(ANSIBLE_USAGE_FILE, DEST_JSON_FILE_ANSIBLE)
    
    
    # print(base_dir)





def collect_data():
    """
    TODO
    """
    print("collect data")
    initial_directory_setup()


def process_data(tag):
    """
    TODO
    """
    print("process data with a tag of " + tag)

    base_dir = setup_env.view_current_conf()['base_dir']
 
    try:
        years = os.listdir(base_dir)
    except NotADirectoryError as e:
        years = []
    # print(YEARS)
    for year in years:
        # print(year)
        try:
            months = os.listdir(base_dir + "/" + year)
        except NotADirectoryError as e:
            months = []
        for month in months:
            # print(month)
            csv_files_list = []
            json_files_list = []
            path_to_csv_dir = base_dir + "/" + year + "/" + month + "/" + "CSV"
            if (os.path.exists(path_to_csv_dir)):
                csv_files_list = os.listdir(path_to_csv_dir)
            path_to_json_dir = base_dir + "/" + year + "/" + month + "/" + "JSON"
            if (os.path.exists(path_to_json_dir)):
                json_files_list = os.listdir(path_to_json_dir)
            # print(csv_files_list)
            generate_report(path_to_csv_dir, csv_files_list, path_to_json_dir, json_files_list, tag)


def generate_report(path_to_csv_dir, csv_files_list, path_to_json_dir, json_files_list, tag):
    """
    TODO
    """
    # print("generating the report by ondemand")
    print("")
    print("## RHEL On-Demand")
    print("")
    process_rhel.ondemand_rhel(path_to_csv_dir, csv_files_list, tag)
    print("## RHEL Versions")
    print("")
    process_rhel_versions.process_rhel_versions(path_to_csv_dir, csv_files_list, tag)
    print("## RHEL Add-ons")
    print("")
    process_rhel_addons.ondemand_rhel_related_products(path_to_csv_dir, csv_files_list, tag)
    print("## Virtualization")
    print("")
    process_virt.ondemand_virtualization(path_to_csv_dir, csv_files_list, tag)
    print("## Middleware")
    print("")
    process_mw.ondemand_mw_from_json(path_to_json_dir, json_files_list, tag)
    print("## RHEL Virtual Data Center")
    print("")
    process_rhel_vdc.virtualdatacenter_rhel(path_to_csv_dir, csv_files_list, tag)
    print("## Ansible Managed Hosts")
    print("")
    process_ansible.ondemand_ansible_from_json(path_to_json_dir, json_files_list, tag)







