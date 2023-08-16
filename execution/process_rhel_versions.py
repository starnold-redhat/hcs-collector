import csv
from execution import util

def process_rhel_versions(path_to_csv_dir, csv_files_list, tag):
    """
    TODO
    """

    # for debug purposes
    # print(path_to_csv_dir)
    # print(csv_files_list)

    CURRENT_TIMEFRAME_YEAR = path_to_csv_dir.split("/")[4]
    CURRENT_TIMEFRAME_MONTH = path_to_csv_dir.split("/")[5]
    CURRENT_TIMEFRAME = CURRENT_TIMEFRAME_YEAR + "-" + CURRENT_TIMEFRAME_MONTH
    OS_VERSIONS = ['5','6','7','8','9']

    # max values for the month
    max_versions={}
    max_versions_by_tag = {}

    for sheet in csv_files_list:

        #counted values for this sheet/day
        stage_versions={}
        stage_versions_by_tag = {}

        with open(path_to_csv_dir + "/" + sheet, "r") as file_obj:
            csv_file = csv.reader(file_obj)
            
            for row in csv_file:
                # print(row)
                installed_product = row[35]
                os_version = row[17]
                major_os = os_version[0]
                vmtags = row[len(row)-1]
                tagvalue=""
                if (tag != "none"):
                    #check if tag exists in vmtags
                    tagvalue = util.get_tag_value(vmtags, tag)
                

                if ('69' in installed_product) or ('479' in installed_product):
                    if (tag != "none" and tagvalue!=""):
                        count_rhel_version_by_tag(major_os, stage_versions_by_tag, tagvalue)

                    if (major_os in stage_versions):
                        stage_count = stage_versions.get(major_os).get('count')
                        stage_versions[major_os]['count'] = stage_count+1
                    else:
                        stage_versions.setdefault(major_os, {'count':1})
                    

        # check whether this day's numbers are bigger than the largest this month so far
        for major_os in OS_VERSIONS:
            if major_os in max_versions:
                if (stage_versions[major_os] > max_versions[major_os]):
                    max_versions[major_os] = stage_versions[major_os]
            else:
                max_versions[major_os] = stage_versions[major_os]

            if (tag != "none"):
                update_max_version_by_tag(stage_versions_by_tag, max_versions_by_tag, major_os)


    print("Max Concurrent RHEL On-Demand, by version ....: {}".format(CURRENT_TIMEFRAME))
    for major_os in OS_VERSIONS:
        if (major_os in max_versions):
            print("On-Demand, RHEL " + major_os + ".............................: {}".format(max_versions[major_os]['count']))
            if (tag != "none"):
                for tagvalue in max_versions_by_tag:
                    if (max_versions_by_tag[tagvalue][major_os] >0):
                        util.pretty_print(2,tagvalue, max_versions_by_tag[tagvalue][major_os])
    
    print("")



def update_max_version_by_tag(stage_by_tag, max_by_tag, major_os):
    
    if (major_os.isdigit()):
        for tagvalue in stage_by_tag:
    
            if (tagvalue in max_by_tag):
                if (stage_by_tag[tagvalue][major_os] > max_by_tag[tagvalue][major_os]):
                    max_by_tag[tagvalue][major_os] = stage_by_tag[tagvalue][major_os]
            else:
                max_by_tag.setdefault(tagvalue, { '5':0, '6': 0, '7': 0, '8':0, '9':0})
                max_by_tag[tagvalue][major_os] = stage_by_tag[tagvalue][major_os]
            

def count_rhel_version_by_tag(major_os, versions_by_tag, tagvalue):
    
    if (major_os.isdigit()):
        if (tagvalue in versions_by_tag):
            tag_summary = versions_by_tag.get(tagvalue)
        else:
            tag_summary = versions_by_tag.setdefault(tagvalue, { '5':0, '6': 0, '7': 0, '8':0, '9':0})

        tag_summary[major_os] = tag_summary.get(major_os) +1
   

