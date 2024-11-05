import traceback
from typing import Any, List
import numpy as np
import pandas as pd
import signal

from empirical.dataset.stats import getFileLength, getAllFileCount
from FAME-ML.py_parser import getPythonExcepts, func_def_log_check, getAllSLOC

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