"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    1,
    '',
    'chat.proto'
)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\")\n\x07Message\x12\x10\n\x08nickname\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"\x14\n\x06Status\x12\n\n\x02ok\x18\x01 \x01(\x08\"\x1f\n\nGetRequest\x12\x11\n\tlast_line\x18\x01 \x01(\x05\"0\n\x08Messages\x12\r\n\x05lines\x18\x01 \x03(\t\x12\x15\n\rnew_last_line\x18\x02 \x01(\x05\x32j\n\x0b\x43hatService\x12*\n\x0bSendMessage\x12\r.chat.Message\x1a\x0c.chat.Status\x12/\n\x0bGetMessages\x12\x10.chat.GetRequest\x1a\x0e.chat.Messagesb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGE']._serialized_start=20
  _globals['_MESSAGE']._serialized_end=61
  _globals['_STATUS']._serialized_start=63
  _globals['_STATUS']._serialized_end=83
  _globals['_GETREQUEST']._serialized_start=85
  _globals['_GETREQUEST']._serialized_end=116
  _globals['_MESSAGES']._serialized_start=118
  _globals['_MESSAGES']._serialized_end=166
  _globals['_CHATSERVICE']._serialized_start=168
  _globals['_CHATSERVICE']._serialized_end=274
