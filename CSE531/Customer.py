#
#   Customer.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Implementation of a banking's branches/customers RPC synchronisation using GRPC, multiprocessing and Python
Customer Class'''

import time
import datetime
import multiprocessing
import json
#import numpy as np

from concurrent import futures
from Util import setup_logger, MyLog, sg, get_operation, get_operation_name, get_result_name, WriteSet, Set_WriteSet_Executed

import grpc
import banking_pb2
import banking_pb2_grpc

ONE_DAY = datetime.timedelta(days=1)
logger = setup_logger("Customer")

client_lock = multiprocessing.Lock()

class Customer:
    """ Customer class definition """

    def __init__(self, _id, events):
        # unique ID of the Customer
        self.id = _id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None
        # the list of Branches including IDs and Addresses
        # This is required in the client-centric consistency assignment to be able to reach every branch
        self.branchList = list()
        # list of WriteIDs - used in case of client-consistency. Implemented with an Array
        #self.writeIDs = np.array([], dtype=int)
        self.writeSets = list()
        #self.writeIDs = []
        # GUI Window handle, if used
        self.window = None

    # Create stub for the customer, matching them with their respective branch
    #
    def createStub(self, Branch_address, want_windows=False, THREAD_CONCURRENCY=1):
        """
        Boots a client (customer) stub in a subprocess.
        If PySimpleGUI/TK are installed and in mode 2, launches a window in the Windows' Manager.

        Args:
            Self:               Customer class
            Branch_address:     TCP/IP address/port where to fund the Branch to connect to
            want_windows:       Boolean, True if graphical windows are desired as UX
            THREAD_CONCURRENCY: Integer, number of threads concurrency

        Returns:
            None

        """
        MyLog(logger, f'[Customer {self.id}] Initializing customer stub to branch stub at {Branch_address}')
        
        self.stub = banking_pb2_grpc.BankingStub(grpc.insecure_channel(Branch_address))

        if ((sg != NotImplemented) and want_windows):
            layout = [
                [sg.Text("Operations Loaded:", size=(60,1), justification="left")],
                [sg.Listbox(values=self.events, size=(60, 3))],
                [sg.Output(size=(80,12))],
                [sg.Button("Run", tooltip='Start Customer\'s Operations')],
                [sg.Button("Close", tooltip='Terminate Customer')]
            ]

            # Create the window
            sg.theme('Dark Green 5')
            w, h = sg.Window.get_screen_size()
            self.window = sg.Window(f"Customer #{self.id} -> To Branch @ {Branch_address}"
                , layout
                , location=(50*(self.id)+10,h/5*(self.id-1)+50)
            )

        client = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY,),)
        client.start()

    # Iterate through the list of the customer's events, sends the messages,
    # and output to the JSON file
    #
    def executeEvents(self, output_file, balance_file, want_windows=False):
        """
        Boots a client (customer) stub in a subprocess.
        If PySimpleGUI/TK are installed and in mode 2, launches a window in the Windows' Manager.

        Args:
            Self:               Customer class
            output_file:        Logging file where to save customer's events
            want_windows:       Boolean, True if graphical windows are desired as UX

        Returns:
            None

        """
        record = {'id': self.id, 'recv': []}
        for event in self.events:
            try:
                request_id = event['id']            # In case of client-consistency
            except KeyError:
                request_id = self.id
            request_operation = get_operation(event['interface'])
            try:
                request_amount = event['money']
            except KeyError:
                request_amount = 0                  # In case of query
            try:
                request_dest = event['dest']        # In case of client-consistency
            except KeyError:
                request_dest = self.id
            
            try:
                if request_operation == banking_pb2.QUERY:
                    request_amount_string = ""
                else:
                    request_amount_string = str(event['money'])
                LogMessage = (
                    f'[Customer {self.id}] ID {request_id}: '
                    f'{get_operation_name(request_operation)} {request_amount_string}'
                    f' -> Branch {request_dest}')
                MyLog(logger, LogMessage, self)

                # Find the right Branch to send to
                msgStubClient = None
                for curr_branch in self.branchList:
                    if request_dest == curr_branch[0]:
                        msgStubClient = banking_pb2_grpc.BankingStub(grpc.insecure_channel(curr_branch[1]))
                        break
                
                if msgStubClient == None:
                    LogMessage = (
                        f'[Customer {self.id}] Error on ID {request_id}: '
                        f'Branch {request_dest} not found in the list.  Not executed.')
                    MyLog(logger, LogMessage, self)
                else:
                    progr_request_id = request_id
                    if request_operation != banking_pb2.QUERY:
                        # First of all, request a WriteID to the Branch - if not a query.
                        # This is used to enforce "Monotonic Writes" and "Read Your Writes" client-centric consistency.
                        wid_response = msgStubClient.RequestWriteSet(
                            banking_pb2.WriteSetRequest(
                                S_ID=self.id,
                                LAST_ID=request_id,
                                Clock=0
                            )
                        )
                        self.writeSets.append(WriteSet(self.id, wid_response.ProgrID, False))
                        progr_request_id = wid_response.ProgrID
                    
                    # Execute the Client's request.
                    # The customer's clock is not used, but could be a future expansion.
                    # In the logical clock assignment (Lampars's algorithm), it is checked,
                    # but the configuration file for customers does not allow setting it anyway.
                    response = msgStubClient.MsgDelivery(
                        banking_pb2.MsgDeliveryRequest(
                            REQ_ID=request_id,
                            OP=request_operation,
                            Amount=request_amount,
                            S_TYPE=banking_pb2.CUSTOMER,    # Source Type = Customer
                            S_ID=self.id,                   # Source ID
                            D_ID=request_dest,
                            Clock=0,
                            ProgrID=progr_request_id
                        )
                    )
                    if request_operation != banking_pb2.QUERY:
                        set_found = Set_WriteSet_Executed (self, self.id, progr_request_id)
                        response_amount_string = f"New balance: {response.Amount}"
                    else:
                        response_amount_string = f"Balance: {response.Amount}"
                        # Output the final balance for the customer from the last query
                        with open(f'{balance_file}', 'a') as outfileb:
                            brecord = {
                                'id': self.id,
                                'balance': response.Amount
                            }
                            json.dump(brecord, outfileb)
                            #outfileb.write('\n')
                    LogMessage = (
                        f'[Customer {self.id}] ID {request_id}: {get_result_name(response.RC)} <- Branch {request_dest} - '
                        f'{response_amount_string}')
                    MyLog(logger, LogMessage, self)

                    values = {
                        'interface': get_operation_name(request_operation),
                        'result': get_result_name(response.RC),
                    }
                    if request_operation == banking_pb2.QUERY:
                        values['money'] = response.Amount
                    record['recv'].append(values)
                                    
                    if record['recv']:
                        # DEBUG
                        #MyLog(logger,f'Writing JSON file on #{output_file}')
                        with open(f'{output_file}', 'a') as outfile:
                            json.dump(record, outfile)
                            outfile.write('\n')
                        
            except grpc.RpcError as rpc_error_call:
                code = rpc_error_call.code()
                details = rpc_error_call.details()

                if (code.name == "UNAVAILABLE"):
                    LogMessage = (f'[Customer {self.id}] Error on Request #{request_id}: Branch {self.id} likely unavailable - Code: {code} - Details: {details}')
                else:
                    LogMessage = (f'[Customer {self.id}] Error on Request #{request_id}: Code: {code} - Details: {details}')
                MyLog(logger, LogMessage, self)
 
    # Spawn the Customer process client. No need to bind to a port here; rather, we are connecting to one.
    #
    def Run_Customer(self, Branch_address, output_file, balance_file, want_windows=False, THREAD_CONCURRENCY=1):
        """Start a client (customer) in a subprocess."""

        MyLog(logger,f'[Customer {self.id}] Booting...')

        Customer.createStub(self, Branch_address, want_windows, THREAD_CONCURRENCY)

        if ((sg != NotImplemented) and want_windows and (self.window != None)):
            # Start events with "Run"
            while True:
                wevent, values = self.window.read()
                
                # End program if user closes window or
                # presses the Close button
                if wevent == "Close" or wevent == sg.WIN_CLOSED:
                    MyLog(logger,f'[Customer {self.id}] Closing windows.')
                    break
                if wevent == "Run":
                    MyLog(logger,f'[Customer {self.id}] Executing events...')
#                    with client_lock:
                    Customer.executeEvents(self, output_file, balance_file, want_windows)
                    MyLog(logger,f'[Customer {self.id}] Events executed. Exiting successfully.')
                    # Uncommenting this break makes the Customer's Window close after Run
                    #break

            self.window.close()
        else:
 #           with client_lock:
            Customer.executeEvents(self, output_file, balance_file, want_windows)
            MyLog(logger,f'[Customer {self.id}] Events executed. Exiting successfully.')

