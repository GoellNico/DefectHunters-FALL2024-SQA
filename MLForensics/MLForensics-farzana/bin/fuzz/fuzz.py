import traceback
from typing import Any, List
import numpy as np
import signal

from generation.main import generateUnitTest
from label_perturbation_attack.knn import euc_dist, predict
from label_perturbation_attack.main import call_loss, call_prob

# Timeout handler for long-running functions
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Function timed out")

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

if __name__ == "__main__":
    fuzz_targets = [
        (
            generateUnitTest, [
                (None, None),
                (1, 2),
                (1.0, 2.0),
                ([], {}),
                ("bad-filename", "random"),
            ]
        ),
        (
            euc_dist, [
                (None, None),
                ("bad", "args"),
                ([], {}),
                (float("inf"), float("inf")),
                (float("-inf"), float("inf")),
                (1j, 1),
                (np.NAN, np.NAN)
            ]
        ),
        (
            predict, [
                ([]),
                (None, 0),
                (None, 1.0),
                (None, "bad-iterable"),
                (None, [None, None, None]),
                (None, []),
                (None, np.zeros((1, 50))),
            ]
        ),
        (
            call_loss, [
                (None,),
                (0,),
                (1.0,),
                ([],),
                ({},),
                ("bad-model-name",),
            ]
        ),
        (
            call_prob, [
                (0, 0, None,),
                (None, None, 0,),
                ("doesnt", "matter", 1.0,),
                (float("-inf"), float("inf"), [],),
                ([], [], {},),
                ([], [], "bad-model-name",),
            ]
        )
    ]

    for method, fuzzed_args in fuzz_targets:
        fuzz(method, fuzzed_args)