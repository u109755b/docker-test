# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import data_pb2 as data__pb2


class LockStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/Lock/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class LockServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LockServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Lock', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Lock(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Lock/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class UnlockStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/Unlock/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class UnlockServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UnlockServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Unlock', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Unlock(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Unlock/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class FRSPropagationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/FRSPropagation/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class FRSPropagationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FRSPropagationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'FRSPropagation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FRSPropagation(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/FRSPropagation/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class FRSTerminationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/FRSTermination/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class FRSTerminationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FRSTerminationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'FRSTermination', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FRSTermination(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/FRSTermination/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class TPLPropagationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/TPLPropagation/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class TPLPropagationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TPLPropagationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'TPLPropagation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TPLPropagation(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TPLPropagation/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class TPLTerminationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_post = channel.unary_unary(
                '/TPLTermination/on_post',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class TPLTerminationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_post(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TPLTerminationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_post': grpc.unary_unary_rpc_method_handler(
                    servicer.on_post,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'TPLTermination', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TPLTermination(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_post(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TPLTermination/on_post',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class RSABLoadStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_get = channel.unary_unary(
                '/RSABLoad/on_get',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class RSABLoadServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RSABLoadServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_get': grpc.unary_unary_rpc_method_handler(
                    servicer.on_get,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RSABLoad', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RSABLoad(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RSABLoad/on_get',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class RSABStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_get = channel.unary_unary(
                '/RSAB/on_get',
                request_serializer=data__pb2.Request.SerializeToString,
                response_deserializer=data__pb2.Response.FromString,
                )


class RSABServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RSABServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_get': grpc.unary_unary_rpc_method_handler(
                    servicer.on_get,
                    request_deserializer=data__pb2.Request.FromString,
                    response_serializer=data__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RSAB', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RSAB(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RSAB/on_get',
            data__pb2.Request.SerializeToString,
            data__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
