#!/bin/sh

cd CSE531

# gRPC - Manual debug (ugly - please no)
#test -f output.json && rm output.json
#../bin/python3 -m pdb Main.py -i test1.json -o output.json

# gRPC - default input file from the assignment
#../bin/python3 Main.py -i grpc.json -o grpc_output.json

# gRPC - increased input file for stress test
#../bin/python3 Main.py -i grpc1.json -o grpc_output1.json

# Lampard's logical clock - default input file from the assignment - no graphical interface - pretty print JSON
test -f logical_clock_output1.json && rm logical_clock_output1.json
test -f logical_clock_branches1.json && rm logical_clock_branches1.json
../bin/python3 Main.py -i logical_clock1.json -o logical_clock_output1.json -c logical_clock_branches1.json -wFalse -pTrue

# Lampard's logical clock - default input file from the assignment - try to start a graphical interface - pretty print JSON
#../bin/python3 Main.py -i logical_clock1.json -o logical_clock_output1.json -c logical_clock_branches1.json -pTrue -wTrue

# Lampard's logical clock - increased input file for stress test - no graphical interface - pretty print JSON
#../bin/python3 Main.py -i logical_clock2.json -o logical_clock_output2.json -c logical_clock_branches2.json -pTrue -wFalse

#test -f logical_clock_output1.json && less logical_clock_output1.json
#test -f logical_clock_branches1.json && less logical_clock_branches1.json
