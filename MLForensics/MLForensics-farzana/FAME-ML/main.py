import lint_engine
import constants 
import time 
import datetime 
import os 
import pandas as pd
import py_parser 
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='forensics.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def giveTimeStamp():
    tsObj = time.time()
    strToret = datetime.datetime.fromtimestamp(tsObj).strftime(constants.TIME_FORMAT)
    logging.info(f"Generated timestamp: {strToret}")
    return strToret


def log_forensics(event, details=""):
    timestamp = giveTimeStamp()
    logging.info(f'{timestamp} - {event}: {details}')


def getCSVData(dic_, dir_repo):
    temp_list = []
    for TEST_ML_SCRIPT in dic_:
        log_forensics("Analyzing Script", TEST_ML_SCRIPT)

        # Section 1.1a
        data_load_counta = lint_engine.getDataLoadCount(TEST_ML_SCRIPT) 
        log_forensics("Data Load Count A", data_load_counta)

        # Section 1.1b
        data_load_countb = lint_engine.getDataLoadCountb(TEST_ML_SCRIPT)
        log_forensics("Data Load Count B", data_load_countb)

        # Section 1.1c
        data_load_countc = lint_engine.getDataLoadCountc(TEST_ML_SCRIPT)
        log_forensics("Data Load Count C", data_load_countc)

        # More processing...
        # (Continue adding log_forensics where appropriate for model load, data download, etc.)

        data_load_count = data_load_counta + data_load_countb + data_load_countc
        model_load_count = lint_engine.getModelLoadCounta(TEST_ML_SCRIPT) + \
                           lint_engine.getModelLoadCountb(TEST_ML_SCRIPT) + \
                           lint_engine.getModelLoadCountc(TEST_ML_SCRIPT) + \
                           lint_engine.getModelLoadCountd(TEST_ML_SCRIPT)
        log_forensics("Model Load Count", model_load_count)

        # More aggregation...

        total_event_count = data_load_count + model_load_count + data_load_countb + data_load_countc
        log_forensics("Total Event Count", total_event_count)

        the_tup = (dir_repo, TEST_ML_SCRIPT, data_load_count, model_load_count, data_load_countb, \
                   data_load_countc, total_event_count)

        temp_list.append(the_tup)
        log_forensics("Appended results for", TEST_ML_SCRIPT)

    return temp_list


def getAllPythonFilesinRepo(path2dir):
    valid_list = []
    for root_, dirnames, filenames in os.walk(path2dir):
        for file_ in filenames:
            full_path_file = os.path.join(root_, file_) 
            if os.path.exists(full_path_file):
                if file_.endswith(constants.PY_FILE_EXTENSION) and py_parser.checkIfParsablePython(full_path_file):
                    valid_list.append(full_path_file)
                    log_forensics("Valid Python file added", full_path_file)
    valid_list = np.unique(valid_list)
    log_forensics("Total Python files in repo", len(valid_list))
    return valid_list


def runFameML(inp_dir, csv_fil):
    output_event_dict = {}
    df_list = [] 
    list_subfolders_with_paths = [f.path for f in os.scandir(inp_dir) if f.is_dir()]
    for subfolder in list_subfolders_with_paths: 
        events_with_dic = getAllPythonFilesinRepo(subfolder)  
        if subfolder not in output_event_dict:
            output_event_dict[subfolder] = events_with_dic
        temp_list = getCSVData(events_with_dic, subfolder)
        df_list = df_list + temp_list 
        log_forensics("Analyzing subfolder", subfolder)

    full_df = pd.DataFrame(df_list)
    full_df.to_csv(csv_fil, header=constants.CSV_HEADER, index=False, encoding=constants.UTF_ENCODING)     
    log_forensics("CSV generated", csv_fil)
    return output_event_dict


if __name__ == '__main__':
    command_line_flag = False  # after acceptance

    t1 = time.time()
    print('Started at:', giveTimeStamp())
    print('*' * 100)

    if command_line_flag:
        dir_path = input(constants.ASK_INPUT_FROM_USER)   
        dir_path = dir_path.strip() 
        if os.path.exists(dir_path):
            repo_dir = dir_path
            output_file = dir_path.split('/')[-2]
            output_csv = '/Users/arahman/Documents/OneDriveWingUp/OneDrive-TennesseeTechUniversity/Research/VulnStrategyMining/ForensicsinML/Output/V5_' + output_file + '.csv'
            full_dict = runFameML(repo_dir, output_csv)
    else: 
        repo_dir = '/Users/arahman/FSE2021_ML_REPOS/GITHUB_REPOS/'
        output_csv = '/Users/arahman/Documents/OneDriveWingUp/OneDrive-TennesseeTechUniversity/Research/VulnStrategyMining/ForensicsinML/Output/V5_OUTPUT_GITHUB.csv'
        full_dict = runFameML(repo_dir, output_csv)

    t2 = time.time()
    time_diff = round((t2 - t1) / 60, 5)
    log_forensics("Script completed in minutes", time_diff)

    print('Ended at:', giveTimeStamp())
    print('*' * 100)
    print(f'Duration: {time_diff} minutes')
    print('*' * 100)
