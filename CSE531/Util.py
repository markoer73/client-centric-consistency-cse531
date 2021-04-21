#
#   Util.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Utility classes - logging, Windows manager, multi-threaded branch output, etc.'''

import logging
import sys
import argparse
import multiprocessing

import banking_pb2
import banking_pb2_grpc

# Implements PySimpleGUI and TK for graphical windows if they are installed.
# Overridden by command line (-w). Command line is not useful, obviously, if
# PySimpleGUI and TK are not functioning.
try:
    import PySimpleGUI as sg                #  Better than CTRL+c
except ImportError:
    sg = NotImplemented

# Sometimes required to unstuck processes - but generally not used
#SLEEP_SECONDS = 3
SLEEP_SECONDS = 0

# Prettify JSON output. Overridden by command line (-p).
PRETTY_JSON = False

# setup a maximum number of thread concurrency following the number of CPUs x cores enumerated by Python
THREAD_CONCURRENCY = multiprocessing.cpu_count()
#THREAD_CONCURRENCY = 2

# Global logger
def setup_logger (name):
    """Sets up the Global Logger"""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[PID %(process)d %(asctime)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def MyLog (logger, LogMessage, obj=None):
    """Prints the log to STDOUT, and if used, updates PySimpleGUI windows"""
    logger.info(LogMessage)
    sys.stdout.flush()
    if ((sg != NotImplemented) and (hasattr(obj, "window")) and (obj.window != None)):
        print(LogMessage)
        if (hasattr(obj, "balance")):
            update_string = (f"Balance: {obj.balance}")
            if (obj.local_clock != None):
                update_string += (f" - Local Clock: {obj.local_clock}")
            obj.window.FindElement('-WINDOWTEXT-').update(update_string)
        obj.window.Refresh()

def Process_Args():
    """Parse command-line arguments."""
    _Input = _Output = _Clock = _Windows = _Pretty = None
    all_args = argparse.ArgumentParser(description='Input, Output, Clock file names')
    all_args.add_argument('-i', '--Input', required=False, help='File name containing branches and customers, in JSON format (optional; defaults to input.json')
    all_args.add_argument('-o', '--Output', required=False, help='Output file name to use (optional; defaults to output.json)')
    all_args.add_argument('-c', '--Clock', required=False, help='Output file from branches - enables Lampard\'s logical clocks (optional; if not provided, clocks are disabled)')
    all_args.add_argument('-w', '--Windows', required=False, help='Enables use of graphical windows/user interactivity (default=False)')
    all_args.add_argument('-p', '--Pretty', required=False, help='Pretty Print JSON output (default=False)')
    args = all_args.parse_args()
    if (args.Input != None):
        _Input = args.Input.strip()
    if (args.Output != None):
        _Output = args.Output.strip()
    if (args.Clock != None):
        _Clock = args.Clock.strip()
    if (args.Windows != None):
        if ((args.Windows.strip().lower() == "true") or (args.Windows.strip().lower() == "yes")):
            _Windows = True
        else:
            _Windows = False
            sg = NotImplemented
    else:
        _Windows = False
        sg = NotImplemented
    if (args.Pretty != None):
        if ((args.Pretty.strip().lower() == "true") or (args.Pretty.strip().lower() == "yes")):
            _Pretty = True
            PRETTY_JSON = True
        else:
            _Pretty = False
            PRETTY_JSON = False
    else:
        _Pretty = False
        PRETTY_JSON = False

    return _Input, _Output, _Clock, _Windows, _Pretty

# Utility functions, used for readability
#
def get_operation(operation):
    """Returns the message type from the operation described in the input file."""
    if operation == 'query':
        return banking_pb2.QUERY
    if operation == 'deposit':
        return banking_pb2.DEPOSIT
    if operation == 'withdraw':
        return banking_pb2.WITHDRAW

def get_operation_name(operation):
    """Returns the operation type from the message."""
    if operation == banking_pb2.QUERY:
        return 'QUERY'
    if operation == banking_pb2.DEPOSIT:
        return 'DEPOSIT'
    if operation == banking_pb2.WITHDRAW:
        return 'WITHDRAW'

def get_result_name(name):
    """Return state of a client's operation."""
    if name == banking_pb2.SUCCESS:
        return 'SUCCESS'
    if name == banking_pb2.FAILURE:
        return 'FAILURE'
    if name == banking_pb2.ERROR:
        return 'ERROR'
