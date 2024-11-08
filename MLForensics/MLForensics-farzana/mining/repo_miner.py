import pandas as pd 
import csv 
import subprocess
import numpy as np
import shutil
from git import Repo
from git import exc 
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import time 
import datetime 
import os 
import logging

# Configure logging for forensic analysis
logging.basicConfig(
    filename='repo_mining_forensics.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s'
)

def deleteRepo(dirName, type_):
    logging.info(f'Deleting {dirName} due to {type_}')
    try:
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
            logging.info(f'Successfully deleted {dirName}')
    except OSError as e:
        logging.error(f'Failed to delete {dirName} due to {e}')
        print('Failed deleting, will try manually')        

def makeChunks(the_list, size_):
    logging.debug(f'Splitting list into chunks of size {size_}')
    for i in range(0, len(the_list), size_):
        yield the_list[i:i+size_]

def cloneRepo(repo_name, target_dir):
    cmd_ = f"git clone {repo_name} {target_dir}"
    try:
        logging.info(f'Cloning repo: {repo_name} into {target_dir}')
        subprocess.check_output(['bash', '-c', cmd_])
    except subprocess.CalledProcessError as e:
        logging.warning(f'Skipping repo due to cloning issue: {repo_name} - {e}')
        print('Skipping this repo ... trouble cloning repo:', repo_name)

def dumpContentIntoFile(strP, fileP):
    logging.info(f'Dumping content into {fileP}')
    try:
        with open(fileP, 'w') as fileToWrite:
            fileToWrite.write(strP)
        file_size = os.stat(fileP).st_size
        logging.info(f'File {fileP} size after dumping: {file_size} bytes')
        return str(file_size)
    except Exception as e:
        logging.error(f'Error writing to file {fileP}: {e}')
        return '0'

def getPythonCount(path2dir): 
    usageCount = 0
    logging.debug(f'Counting Python files in {path2dir}')
    for root_, dirnames, filenames in os.walk(path2dir):
        for file_ in filenames:
            if file_.endswith('.py'):
                usageCount += 1
    logging.info(f'Python file count in {path2dir}: {usageCount}')
    return usageCount                         

def cloneRepos(repo_list): 
    counter = 0     
    for repo_batch in repo_list:
        for repo_ in repo_batch:
            counter += 1 
            logging.info(f'Processing repo {counter}: {repo_}')
            dirName = '/Users/arahman/FSE2021_ML_REPOS/GITHUB_REPOS/' + repo_.split('/')[-2] + '@' + repo_.split('/')[-1]
            cloneRepo(repo_, dirName)
            
            try:
                all_fil_cnt = sum([len(files) for r_, d_, files in os.walk(dirName)])
                if all_fil_cnt <= 0:
                    deleteRepo(dirName, 'NO_FILES')
                else: 
                    py_file_count = getPythonCount(dirName)
                    prop_py = float(py_file_count) / float(all_fil_cnt)
                    if prop_py < 0.25:
                        deleteRepo(dirName, f'LOW_PYTHON_{round(prop_py, 5)}')
            except Exception as e:
                logging.error(f'Error processing repo {repo_}: {e}')
            
            logging.info(f'Processed {counter} repos so far')
            if counter % 10 == 0:
                dumpContentIntoFile('Tracker log updated', 'tracker_completed_repos.csv')

def getMLStats(repo_path):
    repo_statLs = []
    repo_count = 0 
    all_repos = [f.path for f in os.scandir(repo_path) if f.is_dir()]
    logging.info(f'Starting ML stats collection for {len(all_repos)} repos')
    
    for repo_ in all_repos:
        repo_count += 1 
        ml_lib_cnt = getMLLibraryUsage(repo_)
        repo_statLs.append((repo_, ml_lib_cnt))
        logging.info(f'Repo {repo_count}: {repo_} - ML Library Count: {ml_lib_cnt}')
    return repo_statLs 

def getMLLibraryUsage(path2dir): 
    usageCount = 0 
    logging.debug(f'Checking ML library usage in {path2dir}')
    try:
        for root_, dirnames, filenames in os.walk(path2dir):
            for file_ in filenames:
                if file_.endswith('.py'):
                    with open(os.path.join(root_, file_), 'r', encoding='latin-1') as f:
                        for line in f:
                            line_lower = line.lower()
                            if any(lib in line_lower for lib in ['sklearn', 'keras', 'gym.', 'pyqlearning', 'tensorflow', 'torch', 'rl_coach', 'tensorforce', 'stable_baselines', 'tf.']):
                                usageCount += 1
        logging.info(f'Total ML usage count in {path2dir}: {usageCount}')
    except Exception as e:
        logging.error(f'Error analyzing {path2dir}: {e}')
    
    return usageCount 

def deleteRepos():
    try:
        repos_df = pd.read_csv('DELETE_CANDIDATES_GITHUB_V2.csv')
        repos = np.unique(repos_df['REPO'].tolist())
        logging.info(f'Deleting repos listed in DELETE_CANDIDATES_GITHUB_V2.csv')
        for x_ in repos:
            deleteRepo(x_, 'ML_LIBRARY_THRESHOLD')
    except Exception as e:
        logging.error(f'Error in deleteRepos: {e}')

if __name__ == '__main__':
    # Example usage logging in main code block
    logging.info('Script execution started')

    try:
        # Run main cloning or utility functions as needed
        pass
    except Exception as main_e:
        logging.critical(f'Script crashed: {main_e}')

    logging.info('Script execution ended')
