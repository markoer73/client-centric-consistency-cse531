cd CSE531
rm banking_pb2*
python3 -m grpc_tools.protoc -I . banking.proto  --python_out=. --grpc_python_out=.
