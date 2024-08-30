from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VOID_PARAM(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ADDRESS(_message.Message):
    __slots__ = ("ip_addr", "port")
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip_addr: str
    port: int
    def __init__(self, ip_addr: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class JOIN(_message.Message):
    __slots__ = ("id", "address")
    ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: int
    address: ADDRESS
    def __init__(self, id: _Optional[int] = ..., address: _Optional[_Union[ADDRESS, _Mapping]] = ...) -> None: ...

class JOIN_OK(_message.Message):
    __slots__ = ("node", "succ_address", "pred_address")
    NODE_FIELD_NUMBER: _ClassVar[int]
    SUCC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PRED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    node: JOIN
    succ_address: ADDRESS
    pred_address: ADDRESS
    def __init__(self, node: _Optional[_Union[JOIN, _Mapping]] = ..., succ_address: _Optional[_Union[ADDRESS, _Mapping]] = ..., pred_address: _Optional[_Union[ADDRESS, _Mapping]] = ...) -> None: ...

class TRANSFER(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: int
    value: str
    def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...

class NEW_NODE(_message.Message):
    __slots__ = ("ip", "port")
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class LEAVE(_message.Message):
    __slots__ = ("id", "pred_address")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: int
    pred_address: ADDRESS
    def __init__(self, id: _Optional[int] = ..., pred_address: _Optional[_Union[ADDRESS, _Mapping]] = ...) -> None: ...

class NODE_GONE(_message.Message):
    __slots__ = ("id", "new_succ_address")
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_SUCC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: int
    new_succ_address: ADDRESS
    def __init__(self, id: _Optional[int] = ..., new_succ_address: _Optional[_Union[ADDRESS, _Mapping]] = ...) -> None: ...

class STORE(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: int
    value: bytes
    def __init__(self, key: _Optional[int] = ..., value: _Optional[bytes] = ...) -> None: ...

class RETRIEVE(_message.Message):
    __slots__ = ("key", "requester_address")
    KEY_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    key: int
    requester_address: ADDRESS
    def __init__(self, key: _Optional[int] = ..., requester_address: _Optional[_Union[ADDRESS, _Mapping]] = ...) -> None: ...

class OK(_message.Message):
    __slots__ = ("key", "n", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: int
    n: int
    value: bytes
    def __init__(self, key: _Optional[int] = ..., n: _Optional[int] = ..., value: _Optional[bytes] = ...) -> None: ...

class NOT_FOUND(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
