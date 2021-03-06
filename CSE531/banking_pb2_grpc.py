# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import banking_pb2 as banking__pb2


class BankingStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.MsgDelivery = channel.unary_unary(
                '/app.Banking/MsgDelivery',
                request_serializer=banking__pb2.MsgDeliveryRequest.SerializeToString,
                response_deserializer=banking__pb2.MsgDeliveryResponse.FromString,
                )
        self.RequestWriteSet = channel.unary_unary(
                '/app.Banking/RequestWriteSet',
                request_serializer=banking__pb2.WriteSetRequest.SerializeToString,
                response_deserializer=banking__pb2.WriteSetResponse.FromString,
                )
        self.CheckWriteSet = channel.unary_unary(
                '/app.Banking/CheckWriteSet',
                request_serializer=banking__pb2.WriteSetRequest.SerializeToString,
                response_deserializer=banking__pb2.CheckSetResponse.FromString,
                )
        self.CheckWriteSetCustomer = channel.unary_unary(
                '/app.Banking/CheckWriteSetCustomer',
                request_serializer=banking__pb2.WriteSetCustomerRequest.SerializeToString,
                response_deserializer=banking__pb2.CheckSetResponseCustomer.FromString,
                )


class BankingServicer(object):
    """Missing associated documentation comment in .proto file."""

    def MsgDelivery(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestWriteSet(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckWriteSet(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckWriteSetCustomer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BankingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'MsgDelivery': grpc.unary_unary_rpc_method_handler(
                    servicer.MsgDelivery,
                    request_deserializer=banking__pb2.MsgDeliveryRequest.FromString,
                    response_serializer=banking__pb2.MsgDeliveryResponse.SerializeToString,
            ),
            'RequestWriteSet': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestWriteSet,
                    request_deserializer=banking__pb2.WriteSetRequest.FromString,
                    response_serializer=banking__pb2.WriteSetResponse.SerializeToString,
            ),
            'CheckWriteSet': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckWriteSet,
                    request_deserializer=banking__pb2.WriteSetRequest.FromString,
                    response_serializer=banking__pb2.CheckSetResponse.SerializeToString,
            ),
            'CheckWriteSetCustomer': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckWriteSetCustomer,
                    request_deserializer=banking__pb2.WriteSetCustomerRequest.FromString,
                    response_serializer=banking__pb2.CheckSetResponseCustomer.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'app.Banking', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Banking(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def MsgDelivery(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/app.Banking/MsgDelivery',
            banking__pb2.MsgDeliveryRequest.SerializeToString,
            banking__pb2.MsgDeliveryResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestWriteSet(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/app.Banking/RequestWriteSet',
            banking__pb2.WriteSetRequest.SerializeToString,
            banking__pb2.WriteSetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CheckWriteSet(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/app.Banking/CheckWriteSet',
            banking__pb2.WriteSetRequest.SerializeToString,
            banking__pb2.CheckSetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CheckWriteSetCustomer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/app.Banking/CheckWriteSetCustomer',
            banking__pb2.WriteSetCustomerRequest.SerializeToString,
            banking__pb2.CheckSetResponseCustomer.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
