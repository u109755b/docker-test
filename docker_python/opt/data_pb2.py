# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: data.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndata.proto\"\x1b\n\x07Request\x12\x10\n\x08json_str\x18\x01 \x01(\t\"\x1c\n\x08Response\x12\x10\n\x08json_str\x18\x02 \x01(\t2(\n\x04Lock\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32*\n\x06Unlock\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0e\x46RSPropagation\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0e\x46RSTermination\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0eTPLPropagation\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0eTPLTermination\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32+\n\x08RSABLoad\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32\'\n\x04RSAB\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REQUEST._serialized_start=14
  _REQUEST._serialized_end=41
  _RESPONSE._serialized_start=43
  _RESPONSE._serialized_end=71
  _LOCK._serialized_start=73
  _LOCK._serialized_end=113
  _UNLOCK._serialized_start=115
  _UNLOCK._serialized_end=157
  _FRSPROPAGATION._serialized_start=159
  _FRSPROPAGATION._serialized_end=209
  _FRSTERMINATION._serialized_start=211
  _FRSTERMINATION._serialized_end=261
  _TPLPROPAGATION._serialized_start=263
  _TPLPROPAGATION._serialized_end=313
  _TPLTERMINATION._serialized_start=315
  _TPLTERMINATION._serialized_end=365
  _RSABLOAD._serialized_start=367
  _RSABLOAD._serialized_end=410
  _RSAB._serialized_start=412
  _RSAB._serialized_end=451
# @@protoc_insertion_point(module_scope)