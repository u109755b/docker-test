# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: data.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndata.proto\"\x1b\n\x07Request\x12\x10\n\x08json_str\x18\x01 \x01(\t\"\x1c\n\x08Response\x12\x10\n\x08json_str\x18\x02 \x01(\t22\n\x0e\x46RSPropagation\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0e\x46RSTermination\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32(\n\x04Lock\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32*\n\x06Unlock\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0eTPLPropagation\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32\x32\n\x0eTPLTermination\x12 \n\x07on_post\x12\x08.Request\x1a\t.Response\"\x00\x32+\n\x08YCSBLoad\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32\'\n\x04YCSB\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32\x30\n\rTPCCLoadLocal\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32\x33\n\x10TPCCLoadCustomer\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32\'\n\x04TPCC\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32+\n\x08LoadData\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32,\n\tBenchmark\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x32,\n\tValChange\x12\x1f\n\x06on_get\x12\x08.Request\x1a\t.Response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_REQUEST']._serialized_start=14
  _globals['_REQUEST']._serialized_end=41
  _globals['_RESPONSE']._serialized_start=43
  _globals['_RESPONSE']._serialized_end=71
  _globals['_FRSPROPAGATION']._serialized_start=73
  _globals['_FRSPROPAGATION']._serialized_end=123
  _globals['_FRSTERMINATION']._serialized_start=125
  _globals['_FRSTERMINATION']._serialized_end=175
  _globals['_LOCK']._serialized_start=177
  _globals['_LOCK']._serialized_end=217
  _globals['_UNLOCK']._serialized_start=219
  _globals['_UNLOCK']._serialized_end=261
  _globals['_TPLPROPAGATION']._serialized_start=263
  _globals['_TPLPROPAGATION']._serialized_end=313
  _globals['_TPLTERMINATION']._serialized_start=315
  _globals['_TPLTERMINATION']._serialized_end=365
  _globals['_YCSBLOAD']._serialized_start=367
  _globals['_YCSBLOAD']._serialized_end=410
  _globals['_YCSB']._serialized_start=412
  _globals['_YCSB']._serialized_end=451
  _globals['_TPCCLOADLOCAL']._serialized_start=453
  _globals['_TPCCLOADLOCAL']._serialized_end=501
  _globals['_TPCCLOADCUSTOMER']._serialized_start=503
  _globals['_TPCCLOADCUSTOMER']._serialized_end=554
  _globals['_TPCC']._serialized_start=556
  _globals['_TPCC']._serialized_end=595
  _globals['_LOADDATA']._serialized_start=597
  _globals['_LOADDATA']._serialized_end=640
  _globals['_BENCHMARK']._serialized_start=642
  _globals['_BENCHMARK']._serialized_end=686
  _globals['_VALCHANGE']._serialized_start=688
  _globals['_VALCHANGE']._serialized_end=732
# @@protoc_insertion_point(module_scope)
