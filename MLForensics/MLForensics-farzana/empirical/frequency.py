import numpy as np 
import os 
import pandas as pd 
import time 
import datetime 
import logging

# Configure logging for forensic purposes
logging.basicConfig(
    filename='forensics_analysis.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s'
)

def giveTimeStamp():
    tsObj = time.time()
    strToret = datetime.datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
    logging.debug(f'Timestamp generated: {strToret}')
    return strToret

def getAllSLOC(df_param, csv_encoding='latin-1'):
    total_sloc = 0
    all_files = np.unique(df_param['FILE_FULL_PATH'].tolist())
    logging.info(f'Calculating total SLOC for {len(all_files)} files.')
    for file_ in all_files:
        try:
            file_sloc = sum(1 for line in open(file_, encoding=csv_encoding))
            total_sloc += file_sloc
            logging.debug(f'File {file_} SLOC: {file_sloc}')
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logging.error(f'Error reading file {file_}: {e}')
    logging.info(f'Total SLOC: {total_sloc}')
    return total_sloc

def reportProportion(res_file, output_file):
    logging.info(f'Starting proportion report generation from {res_file}')
    try:
        res_df = pd.read_csv(res_file)
    except Exception as e:
        logging.error(f'Error reading {res_file}: {e}')
        return

    repo_names = np.unique(res_df['REPO_FULL_PATH'].tolist())
    fields2explore = ['DATA_LOAD_COUNT', 'MODEL_LOAD_COUNT', 'DATA_DOWNLOAD_COUNT', 'MODEL_LABEL_COUNT', 'MODEL_OUTPUT_COUNT',
                      'DATA_PIPELINE_COUNT', 'ENVIRONMENT_COUNT', 'STATE_OBSERVE_COUNT', 'TOTAL_EVENT_COUNT']
    df_list = []

    for repo in repo_names:
        logging.info(f'Processing repository: {repo}')
        repo_entity = res_df[res_df['REPO_FULL_PATH'] == repo]
        all_py_files = np.unique(repo_entity['FILE_FULL_PATH'].tolist())
        for field in fields2explore:
            field_atleast_one_df = repo_entity[repo_entity[field] > 0]
            atleast_one_files = np.unique(field_atleast_one_df['FILE_FULL_PATH'].tolist())
            prop_metric = round(float(len(atleast_one_files)) / float(len(all_py_files)), 5) * 100
            logging.debug(f'Repo: {repo}, Field: {field}, Total files: {len(all_py_files)}, At least one count: {len(atleast_one_files)}, Proportion: {prop_metric}%')
            the_tup = (repo, len(all_py_files), field, len(atleast_one_files), prop_metric)
            df_list.append(the_tup)

    CSV_HEADER = ['REPO_NAME', 'TOTAL_FILES', 'CATEGORY', 'ATLEASTONE', 'PROP_VAL']
    full_df = pd.DataFrame(df_list)
    try:
        full_df.to_csv(output_file, header=CSV_HEADER, index=False, encoding='utf-8')
        logging.info(f'Successfully saved proportion report to {output_file}')
    except Exception as e:
        logging.error(f'Error saving proportion report to {output_file}: {e}')

def reportEventDensity(res_file, output_file):
    logging.info(f'Starting event density report generation from {res_file}')
    try:
        res_df = pd.read_csv(res_file)
    except Exception as e:
        logging.error(f'Error reading {res_file}: {e}')
        return

    repo_names = np.unique(res_df['REPO_FULL_PATH'].tolist())
    fields2explore = ['DATA_LOAD_COUNT', 'MODEL_LOAD_COUNT', 'DATA_DOWNLOAD_COUNT', 'MODEL_LABEL_COUNT', 'MODEL_OUTPUT_COUNT',
                      'DATA_PIPELINE_COUNT', 'ENVIRONMENT_COUNT', 'STATE_OBSERVE_COUNT', 'TOTAL_EVENT_COUNT']
    df_list = []

    for repo in repo_names:
        logging.info(f'Processing repository: {repo}')
        repo_entity = res_df[res_df['REPO_FULL_PATH'] == repo]
        all_py_files = np.unique(repo_entity['FILE_FULL_PATH'].tolist())
        all_py_size = getAllSLOC(repo_entity)

        for field in fields2explore:
            field_res_list = repo_entity[field].tolist()
            field_res_count = sum(field_res_list)
            try:
                event_density = round(float(field_res_count * 1000) / float(all_py_size), 5)
                logging.debug(f'Repo: {repo}, Field: {field}, Event count: {field_res_count}, Event density: {event_density}')
                the_tup = (repo, all_py_size, field, field_res_count, event_density)
                df_list.append(the_tup)
            except ZeroDivisionError as e:
                logging.warning(f'ZeroDivisionError for repo {repo} on field {field}: {e}')
                event_density = 0
                the_tup = (repo, all_py_size, field, field_res_count, event_density)
                df_list.append(the_tup)

    CSV_HEADER = ['REPO_NAME', 'TOTAL_LOC', 'CATEGORY', 'TOTAL_EVENT_COUNT', 'EVENT_DENSITY']
    full_df = pd.DataFrame(df_list)
    try:
        full_df.to_csv(output_file, header=CSV_HEADER, index=False, encoding='utf-8')
        logging.info(f'Successfully saved event density report to {output_file}')
    except Exception as e:
        logging.error(f'Error saving event density report to {output_file}: {e}')

if __name__ == '__main__':
    logging.info('Script execution started')
    print('*' * 100)
    t1 = time.time()
    print('Started at:', giveTimeStamp())
    print('*' * 100)

    # Replace with actual file paths as needed
    # RESULTS_FILE = 'V5_OUTPUT_MODELZOO.csv'
    # PROPORTION_FILE = 'PROPORTION_MODELZOO.csv'
    # DENSITY_FILE = 'DENSITY_MODELZOO.csv'

    reportProportion(RESULTS_FILE, PROPORTION_FILE)
    print('*' * 100)
    reportEventDensity(RESULTS_FILE, DENSITY_FILE)
    print('*' * 100)

    t2 = time.time()
    print('Ended at:', giveTimeStamp())
    print('Duration: {} minutes'.format(round((t2 - t1) / 60, 5)))
    logging.info('Script execution completed')
    print('*' * 100)
