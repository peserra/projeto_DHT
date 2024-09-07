# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dht.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tdht.proto\"\x06\n\x04Void\"5\n\x08NodeInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07ip_addr\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\r\"\'\n\x04Join\x12\x1f\n\x0cjoining_node\x18\x01 \x01(\x0b\x32\t.NodeInfo\"D\n\x06JoinOk\x12\x1c\n\tnext_node\x18\x01 \x01(\x0b\x32\t.NodeInfo\x12\x1c\n\tprev_node\x18\x02 \x01(\x0b\x32\t.NodeInfo\"*\n\x07NewNode\x12\x1f\n\x0cjoining_node\x18\x01 \x01(\x0b\x32\t.NodeInfo\"-\n\x05Leave\x12$\n\x11leaving_node_pred\x18\x01 \x01(\x0b\x32\t.NodeInfo\"0\n\x08NodeGone\x12$\n\x11leaving_node_next\x18\x01 \x01(\x0b\x32\t.NodeInfo\"5\n\x05Store\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08obj_size\x18\x02 \x01(\r\x12\r\n\x05value\x18\x03 \x01(\x0c\":\n\x08Retrieve\x12\x0b\n\x03key\x18\x01 \x01(\t\x12!\n\x0esearching_node\x18\x02 \x01(\x0b\x32\t.NodeInfo\"2\n\x02Ok\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08obj_size\x18\x02 \x01(\r\x12\r\n\x05value\x18\x03 \x01(\x0c\"\n\n\x08NotFound\"&\n\x08Transfer\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0c\x32\xd7\x02\n\rDhtOperations\x12\x18\n\x08\x46indNext\x12\x05.Join\x1a\x05.Void\x12%\n\x13SendJoiningPosition\x12\x07.JoinOk\x1a\x05.Void\x12!\n\x0e\x41\x64justPredJoin\x12\x08.NewNode\x1a\x05.Void\x12 \n\x0f\x41\x64justNextLeave\x12\x06.Leave\x1a\x05.Void\x12#\n\x0f\x41\x64justPredLeave\x12\t.NodeGone\x1a\x05.Void\x12\x1a\n\tStoreItem\x12\x06.Store\x1a\x05.Void\x12 \n\x0cRetrieveItem\x12\t.Retrieve\x1a\x05.Void\x12\x16\n\x08SendItem\x12\x03.Ok\x1a\x05.Void\x12 \n\x0cSendNotFound\x12\t.NotFound\x1a\x05.Void\x12#\n\rTransferItems\x12\t.Transfer\x1a\x05.Void(\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'dht_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_VOID']._serialized_start=13
  _globals['_VOID']._serialized_end=19
  _globals['_NODEINFO']._serialized_start=21
  _globals['_NODEINFO']._serialized_end=74
  _globals['_JOIN']._serialized_start=76
  _globals['_JOIN']._serialized_end=115
  _globals['_JOINOK']._serialized_start=117
  _globals['_JOINOK']._serialized_end=185
  _globals['_NEWNODE']._serialized_start=187
  _globals['_NEWNODE']._serialized_end=229
  _globals['_LEAVE']._serialized_start=231
  _globals['_LEAVE']._serialized_end=276
  _globals['_NODEGONE']._serialized_start=278
  _globals['_NODEGONE']._serialized_end=326
  _globals['_STORE']._serialized_start=328
  _globals['_STORE']._serialized_end=381
  _globals['_RETRIEVE']._serialized_start=383
  _globals['_RETRIEVE']._serialized_end=441
  _globals['_OK']._serialized_start=443
  _globals['_OK']._serialized_end=493
  _globals['_NOTFOUND']._serialized_start=495
  _globals['_NOTFOUND']._serialized_end=505
  _globals['_TRANSFER']._serialized_start=507
  _globals['_TRANSFER']._serialized_end=545
  _globals['_DHTOPERATIONS']._serialized_start=548
  _globals['_DHTOPERATIONS']._serialized_end=891
# @@protoc_insertion_point(module_scope)
