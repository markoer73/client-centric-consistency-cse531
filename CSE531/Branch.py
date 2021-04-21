#
#   Branch.py
#
# Marco Ermini - March 2021 for ASU CSE531 Course
# Do not leech!
# Built with python 3.8 with GRPC and GRPC-tools libraries; may work with other Python versions
'''Implementation of a banking's branches/customers RPC synchronisation using GRPC, multiprocessing and Python
Branch Class'''

import time
import datetime
import sys
import multiprocessing
import json

from concurrent import futures
from Util import setup_logger, MyLog, sg, get_operation, get_operation_name, get_result_name, SLEEP_SECONDS

import grpc
import banking_pb2
import banking_pb2_grpc

ONE_DAY = datetime.timedelta(days=1)
logger = setup_logger("Branch")


# A constant used to indicate that the Branch must not propagate an operation. This is because a Branch receiving a message
#   cannot distinguish between an operation is coming from a client or another branch or it has been received already.
#   Without this control, the branches would keep propagating operations in an infinite loop. By setting this value after
#   the first propagation, it is not spread further.
DO_NOT_PROPAGATE = -1       

class Branch(banking_pb2_grpc.BankingServicer):
    """ Branch class definition """

    def __init__(self, ID, balance, branches):
        # unique ID of the Branch
        self.id = ID
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
#        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # Binded address
        self.bind_address = str
        # the list of Branches including IDs and Addresses
        self.branchList = list()
        # GUI Window handle, if used
        self.window = None
        # Local logical clock, connected to logical clock exercise (not used otherwise)
        self.local_clock = 0
        # List of events connected to logical clock exercise (not used otherwise)
        self.clock_events = None
        # Logical clock output file (not used otherwise)
        self.clock_output = None
        self.branch_lock = multiprocessing.Lock()

    def MsgDelivery(self, request, context):
        """
        Manages RPC calls coming into a branch from a customer or
        another branch.

        Args:
            self:    Branch class
            request: gRPC class (the message)
            context: gRPC context

        Returns:
            MsgDeliveryResponse class (gRPC response object)

        """
#        with self.branch_lock:
        # Keep a copy of the requests
        self.recvMsg.append(request)

        balance_result = None
        response_result = None

        if request.D_ID == DO_NOT_PROPAGATE:
            CustomerText = 'another Branch'
        else:
            CustomerText = (f'Customer {request.D_ID}')
        LogMessage = (
            f'[Branch {self.id}] Received request: ID {request.REQ_ID} from {CustomerText} - '
            f'Operation: {get_operation_name(request.OP)} - '
            f'Amount: {request.Amount}')
        if (self.clock_events != None):
            LogMessage += (f' - Clock: {request.Clock}')
        MyLog(logger, LogMessage, self)
        
        if request.OP == banking_pb2.QUERY:
            if (self.clock_events != None):
                self.eventReceive(request.Clock)            # Event received from a customer
                self.eventExecute()                         # Event is executed
            response_result, balance_result = self.Query()

        # If DO_NOT_PROPAGATE it means it has arrived from another branch and it must not be
        # spread further.  Also, there is no need to propagate query operations, in general.
        #        
        if request.OP == banking_pb2.DEPOSIT:
            if request.D_ID == DO_NOT_PROPAGATE:
                if (self.clock_events != None):
                    self.propagateReceive(request.Clock)    # Event received from another branch
                    self.register_event(request.REQ_ID, "deposit_broadcast_request")
                    self.eventExecute()                     # Event is executed
                    self.register_event(request.REQ_ID, "deposit_broadcast_execute")
            else:
                if (self.clock_events != None):
                    self.eventReceive(request.Clock)        # Event received from a customer
                    self.register_event(request.REQ_ID, "deposit_request")
                    self.eventExecute()                     # Event is executed
                    self.register_event(request.REQ_ID, "deposit_execute")
            response_result, balance_result = self.Deposit(request.Amount)
         
        if request.OP == banking_pb2.WITHDRAW:
            if request.D_ID == DO_NOT_PROPAGATE:
                if (self.clock_events != None):
                    self.propagateReceive(request.Clock)    # Event received from another branch
                    self.register_event(request.REQ_ID, "withdraw_broadcast_request")
                    self.eventExecute()                     # Event is executed
                    self.register_event(request.REQ_ID, "withdraw_broadcast_execute")
            else:
                if (self.clock_events != None):
                    self.eventReceive(request.Clock)        # Event received from a customer
                    self.register_event(request.REQ_ID, "withdraw_request")
                    self.eventExecute()                     # Event is executed
                    self.register_event(request.REQ_ID, "withdraw_execute")
            response_result, balance_result = self.Withdraw(request.Amount)

        LogMessage = (
            f'[Branch {self.id}] Operation executed: {get_operation_name(request.OP)} request ID {request.REQ_ID} - '
            f'Result: {get_result_name(response_result)} - '
            f'New balance: {balance_result}'
        )
        if (self.clock_events != None):
            LogMessage += (f' - Clock: {self.local_clock}')
        MyLog(logger, LogMessage, self)

        # If DO_NOT_PROPAGATE it means it has arrived from another branch and it must not be
        # spread further.  Also, there is no need to propagate query operations, in general.
        # Finally, only propagates if the operation has been successful.
#            if response_result == banking_pb2.SUCCESS:
        if request.D_ID == DO_NOT_PROPAGATE:
            if (self.clock_events != None):
                self.propagateReceive(request.Clock)            # Sets clock for propagation received
        else:
            if request.OP == banking_pb2.DEPOSIT:
                if (self.clock_events != None):
                    self.propagateSend()                        # Sets clock for further propagation
                    #self.register_event(request.REQ_ID, "deposit_broadcast_execute")
                self.Propagate_Deposit(request.REQ_ID, request.Amount)
            if request.OP == banking_pb2.WITHDRAW:
                if (self.clock_events != None):
                    self.propagateSend()                        # Sets clock for further propagation
                    #self.register_event(request.REQ_ID, "withdraw_broadcast_execute")
                self.Propagate_Withdraw(request.REQ_ID, request.Amount)

        self.eventResponse()                                        # Call for eventResponse

        response = banking_pb2.MsgDeliveryResponse(
            ID=request.REQ_ID,
            RC=response_result,
            Amount=balance_result,
            Clock=self.local_clock
        )

        if (self.clock_events != None):
            if request.OP == banking_pb2.DEPOSIT:
                if request.D_ID == DO_NOT_PROPAGATE:
                    self.register_event(request.REQ_ID, "deposit_broadcast_response")
                else:
                    self.register_event(request.REQ_ID, "deposit_response")
            if request.OP == banking_pb2.WITHDRAW:
                if request.D_ID == DO_NOT_PROPAGATE:
                    self.register_event(request.REQ_ID, "withdraw_broadcast_response")
                else:
                    self.register_event(request.REQ_ID, "withdraw_response")

        LogMessage = (
            f'[Branch {self.id}] Sent response to request ID {request.REQ_ID} back to {CustomerText} - '
            f'Result: {get_result_name(response_result)} - '
            f'New balance: {balance_result}'
        )
        if (self.clock_events != None):
            LogMessage += (f' - Clock: {self.local_clock}')
        MyLog(logger, LogMessage, self)

        LogMessage = (
            f'[Branch {self.id}] Event processing completed for request ID {request.REQ_ID} '
            f'replied back to {CustomerText} - '
            f'Result: {get_result_name(response_result)} - '
            f'New balance: {balance_result}'
        )
        if (self.clock_events != None):
            LogMessage += (f' - Clock: {self.local_clock}')
        MyLog(logger, LogMessage, self)

        if ((sg == NotImplemented or (not self.window)) and SLEEP_SECONDS):
            # Wait some seconds to allow execution of propagation in case of command line execution
            MyLog(logger, f'[Main] *** Waiting for {SLEEP_SECONDS} seconds to allow finish propagations ***')
            MyLog(logger, f'[Main]     (Otherwise it will sometimes fail when the computer is slow)')
            time.sleep(SLEEP_SECONDS)

        return response

    def Query(self):
        """
        Implements the Query interface.

        Args:
            Self:   Branch class
        
        Returns: The current Branch balance

        """
        return banking_pb2.SUCCESS, self.balance

    def Deposit(self, amount):
        """
        Implements the Deposit interface.

        Args:
            Self:   Branch class
            amount: the amount to be added to the balance

        Returns:
            banking_pb2 constant: either SUCCESS, FAILURE, or ERROR
                If the amount added is smaller than zero,
                the operation will return ERROR, otherwise SUCCESS.

            new_balance: The updated Branch balance after the amount has been added.

        """
        if amount <= 0:		                            # invalid operation - but returns the balance anyway
            return banking_pb2.ERROR, self.balance
        new_balance = self.balance + amount
        self.balance = new_balance
        return banking_pb2.SUCCESS, new_balance         # success

    def Withdraw(self, amount):
        """
        Implements the Withdraw interface.

        Args:
            Self:   Branch class
            amount: the amount to be removed to the balance

        Returns: 
            banking_pb2 constant: either SUCCESS, FAILURE, or ERROR.
                If the amount requested is smaller than zero,
                the operation will return ERROR.
                If the amount requested is bigger than the current balance,
                the operation will return FAILURE, otherwise SUCCESS.

            new_balance: The updated Branch balance after the amount has been withdrawn.
                If the amount requested is bigger than the current balance,
                the operation will fail and the balance returned will be the previous
                balance. 

        """
        # Distinguish between error (cannot execute a certain operation) or failure (operation is valid, but for instance
        # there is not enough balance).
        # This distinction is used to distinguish between cases such as overdrafts and thread/OS errors.
        if amount <= 0:		        # invalid operation
            return banking_pb2.ERROR, 0
        new_balance = self.balance - amount
        if new_balance < 0:	        # not enough money! cannot widthdraw
            return banking_pb2.FAILURE, amount
        self.balance = new_balance
        return banking_pb2.SUCCESS, new_balance

    def Propagate_Deposit(self, request_id, amount):
        """
        Implements the propagation of the deposit to other branches.

        Args:
            Self:   Branch class
            request_id: the request ID of the event
            amount: the amount to be added to the balance

        Returns: The updated Branch balance after the amount added

        """
#        with self.branch_lock:
        for stub in self.branchList:
            if self.id != stub[0]:                          # Do not propagate to itself (should not happen, added security)
                LogMessage = (
                    f'[Branch {self.id}] Propagate {get_operation_name(banking_pb2.DEPOSIT)} request ID {request_id} '
                    f'amount {amount} to Branch {stub[0]} @{stub[1]}')   
                if (self.clock_events != None):             # Verify if in the logical clock case
                    LogMessage += (f' with clock {self.local_clock}')
                MyLog(logger, LogMessage, self)
                
                try:
                    msgStub = banking_pb2_grpc.BankingStub(grpc.insecure_channel(stub[1]))
                    
                    if (self.clock_events != None):             # Verify if in the logical clock case
                        response = msgStub.MsgDelivery(
                            banking_pb2.MsgDeliveryRequest(
                                REQ_ID=request_id,
                                OP=banking_pb2.DEPOSIT,
                                Amount=amount,
                                D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                                Clock=self.local_clock
                            )
                        )
                    else:
                        response = msgStub.MsgDelivery(
                            banking_pb2.MsgDeliveryRequest(
                                REQ_ID=request_id,
                                OP=banking_pb2.DEPOSIT,
                                Amount=amount,
                                D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                            )
                        )
                    LogMessage = (
                        f'[Branch {self.id}] received response to request ID {request_id} to Branch @{stub[1]} - '
                        f'Operation: {get_operation_name(banking_pb2.DEPOSIT)} - Result: {get_result_name(response.RC)} - '
                        f'New balance: {response.Amount}')
                    if (self.clock_events != None):         # Verify if in the logical clock case
                        LogMessage += (f' - Clock: {response.Clock}')

                    self.eventResponse()                    # Call for eventResponse
                    
                except grpc.RpcError as rpc_error_call:
                    code = rpc_error_call.code()
                    details = rpc_error_call.details()

                    if (code.name == "UNAVAILABLE"):
                        LogMessage = (f'[Branch {self.id}] Error on request ID {request_id}: Branch {stub[0]} @{stub[1]} likely unavailable - Code: {code} - Details: {details}')
                    else:
                        LogMessage = (f'[Branch {self.id}] Error on request ID {request_id}: Code: {code} - Details: {details}')

                MyLog(logger, LogMessage, self)


    def Propagate_Withdraw(self, request_id, amount):
        """
        Implements the propagation of the withdraw to other branches.

        Args:
            Self:   Branch class
            request_id: the request ID of the event
            amount: the amount to be withdrawn from the balance

        Returns: The updated Branch balance after the amount withdrawn

        """        
#        with self.branch_lock:
        for stub in self.branchList:
            if self.id != stub[0]:                          # Do not propagate to itself (should not happen, added security)
                LogMessage = (
                    f'[Branch {self.id}] Propagate {get_operation_name(banking_pb2.WITHDRAW)} request ID {request_id} '
                    f'amount {amount} to Branch {stub[0]} @{stub[1]}')
                if (self.clock_events != None):             # Verify if in the logical clock case
                    LogMessage += (f' with clock {self.local_clock}')
                MyLog(logger, LogMessage, self)

                try:
                    msgStub = banking_pb2_grpc.BankingStub(grpc.insecure_channel(stub[1]))

                    if (self.clock_events != None):             # Verify if in the logical clock case
                        response = msgStub.MsgDelivery(
                            banking_pb2.MsgDeliveryRequest(
                                REQ_ID=request_id,
                                OP=banking_pb2.WITHDRAW,
                                Amount=amount,
                                D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                                Clock=self.local_clock
                            )
                        )
                    else:
                        response = msgStub.MsgDelivery(
                            banking_pb2.MsgDeliveryRequest(
                                REQ_ID=request_id,
                                OP=banking_pb2.WITHDRAW,
                                Amount=amount,
                                D_ID=DO_NOT_PROPAGATE,          # Sets DO_NOT_PROPAGATE for receiving branches
                            )
                        )
                    LogMessage = (
                        f'[Branch {self.id}] received response to request ID {request_id} to Branch @{stub[1]} - '
                        f'Operation: {get_operation_name(banking_pb2.WITHDRAW)} - Result: {get_result_name(response.RC)} - '
                        f'New balance: {response.Amount}')
                    if (self.clock_events != None):         # Verify if in the logical clock case
                        LogMessage += (f' - Clock: {response.Clock}')

                    self.eventResponse()                    # Call for eventResponse

                except grpc.RpcError as rpc_error_call:
                    code = rpc_error_call.code()
                    details = rpc_error_call.details()

                    if (code.name == "UNAVAILABLE"):
                        LogMessage = (f'[Branch {self.id}] Error on request ID {request_id}: Branch {stub[0]} @{stub[1]} likely unavailable - Code: {code} - Details: {details}')
                    else:
                        LogMessage = (f'[Branch {self.id}] Error on request ID {request_id}: Code: {code} - Details: {details}')

                MyLog(logger, LogMessage, self)

    def eventReceive(self, passed_clock):
        """
        Implementation of sub-interface "eventReceive".            
        This subevent happens when the Branch process receives a request
        from the Customer process. The Branch process selects the larger
        value between the local clock and the remote clock from the message,
        and increments one from the selected value.  
            
        Args:
            self:           Branch class
            passed_clock:   The clock to compare to the local one

        Returns: None

        """
        self.local_clock = max(self.local_clock, passed_clock) + 1

    def eventExecute(self):
        """
        Implementation of sub-interface "eventExecute".
        This subevent happens when the Branch process executes the event
        after the subevent “Event Request”. The Branch process increments
        one from its local clock.  

        Args:
            self:           Branch class

        Returns: None

        """
        self.local_clock += 1

    def propagateSend(self):
        """
        Interface to set the clock tick for "propagateSend".
        This subevent happens when the Branch process receives the
        propagation request to its fellow branch processes. The Branch
        process increments one from its local clock.
            
        Returns: None

        """
        self.local_clock += 1

    def propagateReceive(self, passed_clock):
        """
        Implementation of sub-interface "propagateReceive".
        This subevent happens when the Branch receives the propagation request
        from its fellow branches. The Branch process selects the biggest value
        between the local clock and the remote clock from the message, and
        increments one from the selected value.            
            
        Args:
            self:           Branch class
            passed_clock:   The clock to compare to the local one

        Returns: None

        """
        self.local_clock = max(self.local_clock, passed_clock) + 1

    def propagateExecute(self):
        """
        Interface to set the clock tick for "propagateExecute".
        This subevent happens when the Branch process executes the event after
        the subevent “Propogate_Request”. The Branch process increments one
        from its local clock.          
            
        Returns: None

        """
        self.local_clock += 1

    def eventResponse(self):
        """
        Interface to set the clock tick for "eventResponse".
        This subevent happens after all the propagation  responses are returned
        from the branches. The branch returns success - fail back to the
        Customer process. The Branch process increments one from its local clock.

        Returns: None

        """
        self.local_clock += 1

    def register_event(self, passed_id, passed_name):
        """
        Adds an event to the list of processed events by the branch process

        Args:
            self:           Branch class
            passed_id:      Event ID to record
            passed_name:    Event Name
            passed_clock:   Local clock recorded

        Returns: None

        """
        if (self.clock_events != None):
            self.clock_events.append({'id': passed_id, 'name': passed_name, 'clock': self.local_clock})
        if (self.window):
            MyLog(logger, (f"[Branch {passed_id}] Registered event  \"{passed_name}\" - ID {passed_id}, clock {self.local_clock}"))

def Wait_Loop(Branch, want_windows=False):
    """
    Implements the main waiting loop for branches.
    If PySimpleGUI/TK are installed, relies on user's interaction on graphical windows.
    Otherwise, it waits for a day unless CTRL+C is pressed.

    Args:
        Self:   Branch class

    Returns: none.
    
    """
    if ((sg != NotImplemented) and want_windows):
        # Create an event loop
        while True:
            event, values = Branch.window.read()

            # End program if user closes window or
            # presses the Close button
            if event == "Close" or event == sg.WIN_CLOSED:
                break
    else:
        try:
            while True:
                time.sleep(ONE_DAY.total_seconds())
        except KeyboardInterrupt:
            return

def Run_Branch(Branch, clock_file=None, want_windows=False, THREAD_CONCURRENCY=1):
    """
    Boot a server (branch) in a subprocess.
    If PySimpleGUI/TK are installed and mode 2 requested, launches a window in the
    Windows' Manager.

    Args:
        Branch:             Branch class
        clock_file:         String, output file where to write the logical clock event.
                            If set to None, works as it was Exercise 1 (gRPC) and does
                            not use clocks.
        want_windows:       Boolean, True if graphical windows are desired as UX
        THREAD_CONCURRENCY: Integer, number of threads concurrency

    Returns: none.
    
    """
    if (clock_file == None):
        MyLog(logger,f'[Branch {Branch.id}] Initialising @{Branch.bind_address}...')
    else:
        MyLog(logger,f'[Branch {Branch.id}] Initialising @{Branch.bind_address} with local clock {Branch.local_clock}...')

    options = (('grpc.so_reuseport', 1),)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY,), options=options)
    banking_pb2_grpc.add_BankingServicer_to_server(Branch, server)

    if ((sg != NotImplemented) and want_windows):
        if (clock_file == None):
            layout = [
                [sg.Text(f"Balance: {Branch.balance}", size=(40,1), justification="left", key='-WINDOWTEXT-')],
                [sg.Output(size=(90,15))],
                [sg.Button("Close", tooltip='Terminates Branch')]
            ]
        else:
            layout = [
                [sg.Text(f"Balance: {Branch.balance} - Local Clock: {Branch.local_clock}", size=(40,1), justification="left", key='-WINDOWTEXT-')],
                [sg.Output(size=(90,15))],
                [sg.Button("Close", tooltip='Terminates Branch')]
            ]

        # Create the window
        sg.theme('Dark Blue 3')
        w, h = sg.Window.get_screen_size()
        Branch.window = sg.Window(f"Branch #{Branch.id} @Address {Branch.bind_address}"
            , layout
            , location=(w/2+50*Branch.id, h/5*(Branch.id-1)+50)
        )

        Branch.window.refresh()

    server.add_insecure_port(Branch.bind_address)
    server.start()

    if ((sg == NotImplemented) or want_windows):
        MyLog(logger,f'[Branch {Branch.id}] *** Press CTRL+C to exit the process when finished ***')
    
    Wait_Loop(Branch, want_windows)

    if ((sg != NotImplemented) and want_windows):
        Branch.window.close()

    if Branch.clock_output:
        with open(f'{Branch.clock_output.name}', 'a') as outfile:
            if (Branch.clock_events != None):
                Branch.clock_events.sort(key=lambda item: item['clock'])
                record = {'pid': Branch.id, 'data': Branch.clock_events}
            else:
                record = {'pid': Branch.id, 'data': []}
            json.dump(record, outfile)
            outfile.write('\n')
            outfile.close()

    server.stop(None)
    
    MyLog(logger,f'[Branch {Branch.id}] Exiting Successfully.')