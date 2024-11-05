import os 
import numpy as np 
import ast 
import constants 
import logging
from datetime import datetime

# Configure logging for forensic purposes
logging.basicConfig(
    filename='forensic_analysis.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s'
)

PY_FILE_EXTENSION = '.py'
NAME_KW = 'name'
NAMES_KW = 'names' 
LOGGING_KW = 'logging'

def checkIfParsablePython(pyFile):
    flag = True 
    try:
        with open(pyFile, 'r') as f:
            full_tree = ast.parse(f.read())
        logging.debug(f'Parsed file successfully: {pyFile}')
    except (SyntaxError, UnicodeDecodeError) as err:
        flag = False
        logging.error(f'Failed to parse file {pyFile}: {err}')
    return flag 	

def getAllPythonFilesinRepo(path2dir):
    valid_list = []
    logging.info(f'Searching for Python files in directory: {path2dir}')
    for root_, dirnames, filenames in os.walk(path2dir):
        for file_ in filenames:
            full_path_file = os.path.join(root_, file_)
            if os.path.exists(full_path_file):
                if file_.endswith(PY_FILE_EXTENSION) and checkIfParsablePython(full_path_file):
                    valid_list.append(full_path_file)
                    logging.debug(f'Valid Python file found: {full_path_file}')
    valid_list = np.unique(valid_list)
    logging.info(f'Total Python files found: {len(valid_list)}')
    return valid_list

def hasLogImport(file_):
    IMPORT_FLAG = False 
    try:
        with open(file_, 'r') as f:
            tree_object = ast.parse(f.read())
        for stmt_ in tree_object.body:
            for node_ in ast.walk(stmt_):
                if isinstance(node_, ast.Import):
                    funcDict = node_.__dict__
                    import_name_objects = funcDict[NAMES_KW]
                    for obj in import_name_objects:
                        if LOGGING_KW in obj.__dict__[NAME_KW]:
                            IMPORT_FLAG = True
                            logging.debug(f'Logging import found in {file_}')
                            break
    except (SyntaxError, UnicodeDecodeError) as e:
        logging.error(f'Failed to parse or check imports in {file_}: {e}')
    return IMPORT_FLAG

def getLogStatements(pyFile):
    try:
        with open(pyFile, 'r') as f:
            tree_object = ast.parse(f.read())
        func_decl_list = getPythonAtrributeFuncs(tree_object)
        for func_decl_ in func_decl_list:
            func_parent_id, func_name, funcLineNo, call_arg_list = func_decl_
            if LOGGING_KW in func_parent_id or LOGGING_KW in func_name:
                for arg_ in call_arg_list:
                    logging.info(f'Logging call detected in {pyFile} at line {funcLineNo}: {func_name} with args {arg_}')
                    print(func_parent_id, func_name, call_arg_list, arg_)
    except (SyntaxError, UnicodeDecodeError) as e:
        logging.error(f'Error analyzing log statements in {pyFile}: {e}')

def printLogOps(repo_path):
    logging.info(f'Analyzing repository: {repo_path}')
    valid_py_files = getAllPythonFilesinRepo(repo_path)
    log_py_files = [x_ for x_ in valid_py_files if hasLogImport(x_)]
    logging.info(f'Python files with logging imports: {len(log_py_files)}')
    for py_file in log_py_files:
        logging.info(f'Processing file: {py_file}')
        print(py_file)
        print(getLogStatements(py_file))
        print('=' * 50)

if __name__ == '__main__':
    repo_path = '/Users/arahman/FSE2021_ML_REPOS/MODELZOO/'
    logging.info(f'Starting forensic analysis at {datetime.now()}')
    printLogOps(repo_path)
    logging.info(f'Forensic analysis completed at {datetime.now()}')
