#!/bin/bash

cd CSE531

##### gRPC - Assignment 1 #####

# gRPC - Manual debug (ugly - please no)
#test -f output.json && rm output.json
#../bin/python3 -m pdb Main.py -i test1.json -o output.json

# gRPC - default input file from the assignment
#../bin/python3 Main.py -i grpc.json -o grpc_output.json

# gRPC - increased input file for stress test
#../bin/python3 Main.py -i grpc1.json -o grpc_output1.json


##### Lampard's Logical Clock - Assignment 2 #####

#test -f logical_clock_output1.json && less logical_clock_output1.json
#test -f logical_clock_branches1.json && less logical_clock_branches1.json

# Lampard's logical clock - increased input file for stress test - no graphical interface - pretty print JSON
#../bin/python3 Main.py -i logical_clock2.json -o logical_clock_output2.json -c logical_clock_branches2.json -pTrue -wFalse


##### Client-centric Consistency - Assignment 3 #####

# Client-centric consistency - default input file from the assignment - no graphical interface - pretty print JSON
test -f ccc_output1.json && rm ccc_output1.json
test -f ccc_output2.json && rm ccc_output2.json
test -f ccc_monotonic_writes_output.json && rm ccc_monotonic_writes_output.json
test -f ccc_monotonic_writes_balance.json && rm ccc_monotonic_writes_balance.json
#test -f ccc_output_clock2.json && rm ccc_output_clock2.json
#../bin/python3 Main.py -i ccc1.json -o ccc_output1.json -wFalse -pTrue

# Client-centric consistency - default input file from the assignment - no graphical interface - pretty print JSON
#../bin/python3 Main.py -i ccc1.json -o ccc_output1.json -pTrue -wFalse

echo Running monotonic writes demo - Press any key to start
echo
read -n 1;
# Client-centric consistency - Monotonic Writes demonstration - no graphical interface - pretty print JSON
../bin/python3 Main.py -i ccc_monotonic_writes.json -o ccc_monotonic_writes_output.json -b ccc_monotonic_writes_balance.json -pTrue -wFalse
echo
echo Printing the balance output...
cat ccc_monotonic_writes_balance.json
echo
echo
echo Running read your writes demo - Press any key to start
echo
read -n 1;
# Client-centric consistency - Monotonic Writes demonstration - no graphical interface - pretty print JSON
../bin/python3 Main.py -i ccc_read_your_writes.json -o ccc_read_your_writes_output.json -b ccc_read_your_writes_balance.json -pTrue -wFalse
echo
echo
echo "Printing the balance output..."
cat ccc_monotonic_writes_balance.json
echo
echo

# Client-centric consistency - default input file from the assignment - try to start a graphical interface - pretty print JSON
#../bin/python3 Main.py -i ccc1.json -o ccc_output1.json -c ccc_output_clock1.json -pTrue -wFalse

# Client-centric consistency - better input file from the assignment - no graphical interface - pretty print JSON
#../bin/python3 Main.py -i ccc2.json -o ccc_output2.json -c ccc_output_clock2.json -pTrue -wFalse

# Client-centric consistency - better input file from the assignment - try to start a graphical interface - pretty print JSON
#../bin/python3 Main.py -i ccc2.json -o ccc_output2.json -c ccc_output_clock2.json -pTrue -wTrue

