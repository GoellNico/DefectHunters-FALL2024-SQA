import traceback
from typing import Any, List
import numpy as np
import pandas as pd
import signal

# Functions to fuzz
def getFileLength(file_):
    return sum(1 for line in open(file_, encoding='latin-1'))

def getAllFileCount(df_):
    tot_fil_size = 0 
    file_names_ = np.unique(df_['FILE_FULL_PATH'].tolist())
    for file_ in file_names_:
        tot_fil_size = tot_fil_size + getFileLength(file_)
    return tot_fil_size, len(file_names_)

def getAllSLOC(df_param, csv_encoding='latin-1'):
    total_sloc = 0
    all_files = np.unique(df_param['FILE_FULL_PATH'].tolist())
    for file_ in all_files:
        total_sloc = total_sloc + sum(1 for line in open(file_, encoding=csv_encoding))
    return total_sloc

def checkLoggingPerData(tree_object, name2track):
    LOGGING_EXISTS_FLAG = False 
    IMPORT_FLAG, FUNC_FLAG, ARG_FLAG  = False, False , False 
    for stmt_ in tree_object.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Import):
                funcDict = node_.__dict__     
                import_name_objects = funcDict[constants.NAMES_KW]
                for obj in import_name_objects:
                    if constants.LOGGING_KW in obj.__dict__[constants.NAME_KW]: 
                        IMPORT_FLAG = True 
    func_decl_list = getPythonAtrributeFuncs(tree_object)
    for func_decl_ in func_decl_list:
        func_parent_id, func_name, funcLineNo, call_arg_list = func_decl_ 
        if constants.LOGGING_KW in func_parent_id or constants.LOGGING_KW in func_name: 
            FUNC_FLAG = True 
            for arg_ in call_arg_list:
                if name2track in arg_:
                    ARG_FLAG = True 
    if IMPORT_FLAG and FUNC_FLAG and ARG_FLAG:
        LOGGING_EXISTS_FLAG = True 
    return LOGGING_EXISTS_FLAG 

def func_def_log_check(func_decl_list):
    FUNC_FLAG = False 
    for func_decl_ in func_decl_list:
        func_parent_id, func_name, funcLineNo, call_arg_list = func_decl_
        if constants.LOGGING_KW in func_parent_id or constants.LOGGING_KW in func_name: 
            FUNC_FLAG = True         
    return FUNC_FLAG 

def getPythonExcepts(pyTreeObj): 
    except_body_as_list = []
    for stmt_ in pyTreeObj.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.ExceptHandler): 
                exceptDict = node_.__dict__     
                except_body_as_list = exceptDict[constants.BODY_KW]  
    return except_body_as_list

# Timeout handler for long-running functions
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Function timed out")

# Mock function for constants used in AST functions
class constants:
    NAMES_KW = "names"
    NAME_KW = "name"
    LOGGING_KW = "logging"
    BODY_KW = "body"

signal.signal(signal.SIGALRM, timeout_handler)

# Enhanced fuzz function with console logging
def fuzz(method, fuzzed_args: List[Any]):
    for args in fuzzed_args:
        try:
            # Set a timeout for each fuzz test
            signal.alarm(5)  # Timeout after 5 seconds
            result = method(*args)
            signal.alarm(0)  # Disable alarm if successful
            print(f"FUZZ: {method.__name__} PASSED ({result}) with args {args}")
        except TimeoutException:
            print(f"FUZZ: {method.__name__} TIMED OUT with args {args}")
        except Exception as exc:
            print(f"FUZZ: {method.__name__} FAILED with args {args}")
            traceback.print_exc()

# Fuzzing targets for each function
if __name__ == "__main__":
    fuzz_targets = [
        # Fuzzing getFileLength with various file inputs
        (
            getFileLength, [
                ("nonexistent_file.txt",),  # File that doesn't exist
                (None,),                    # None as file name
                (123,),                     # Invalid file type
                ("",),                      # Empty string as file name
            ]
        ),
        # Fuzzing getAllFileCount with various DataFrame inputs
        (
            getAllFileCount, [
                (pd.DataFrame({"FILE_FULL_PATH": []}),),               # Empty DataFrame
                (pd.DataFrame({"FILE_FULL_PATH": ["nonexistent.txt"]}),), # File path that doesn't exist
                (pd.DataFrame({"WRONG_COLUMN": ["file1.txt"]}),),      # Missing required column
                (None,),                                              # None instead of DataFrame
            ]
        ),
        # Fuzzing getAllSLOC with DataFrame inputs and encoding variations
        (
            getAllSLOC, [
                (pd.DataFrame({"FILE_FULL_PATH": []}),),               # Empty DataFrame
                (pd.DataFrame({"FILE_FULL_PATH": ["nonexistent.txt"]}), "utf-8"), # Nonexistent file with utf-8 encoding
                (pd.DataFrame({"FILE_FULL_PATH": ["file1.txt"]}), "invalid-encoding"), # Invalid encoding
                (None, "utf-8"),                                      # None as DataFrame
            ]
        ),
        # Fuzzing checkLoggingPerData with AST tree inputs and different tracking names
        (
            checkLoggingPerData, [
                (ast.parse("import logging"), "some_name"),           # Simple import statement with logging
                (None, "name_to_track"),                              # None as tree object
                (ast.parse(""), ""),                                  # Empty tree object and empty name to track
                (ast.parse("def foo(): pass"), "foo"),                # Tree without logging or imports
            ]
        ),
        # Fuzzing func_def_log_check with different function declaration lists
        (
            func_def_log_check, [
                ([("some_class", "logging_function", 12, [])],),      # List with logging function
                ([("some_class", "function", 15, ["logging"])],),     # Non-logging function with logging arg
                ([],),                                                # Empty function declaration list
                (None,),                                              # None as func_decl_list
            ]
        ),
        # Fuzzing getPythonExcepts with various AST inputs
        (
            getPythonExcepts, [
                (ast.parse("try: pass\nexcept: pass"),),              # Simple try-except
                (None,),                                              # None as AST object
                (ast.parse("def foo(): pass"),),                      # Tree with no exceptions
                (ast.parse("try:\n  raise ValueError()\nexcept ValueError:\n  pass"),), # Specific exception
            ]
        )
    ]

    for method, fuzzed_args in fuzz_targets:
        fuzz(method, fuzzed_args)