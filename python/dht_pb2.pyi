from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Void(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ("id", "ip_addr", "port")
    ID_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    id: str
    ip_addr: str
    port: int
    def __init__(self, id: _Optional[str] = ..., ip_addr: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class Join(_message.Message):
    __slots__ = ("joining_node", "description")
    JOINING_NODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    joining_node: NodeInfo
    description: str
    def __init__(self, joining_node: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class JoinOk(_message.Message):
    __slots__ = ("next_node", "prev_node", "description")
    NEXT_NODE_FIELD_NUMBER: _ClassVar[int]
    PREV_NODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    next_node: NodeInfo
    prev_node: NodeInfo
    description: str
    def __init__(self, next_node: _Optional[_Union[NodeInfo, _Mapping]] = ..., prev_node: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class NewNode(_message.Message):
    __slots__ = ("joining_node", "description")
    JOINING_NODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    joining_node: NodeInfo
    description: str
    def __init__(self, joining_node: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class Leave(_message.Message):
    __slots__ = ("leaving_node_pred", "description")
    LEAVING_NODE_PRED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    leaving_node_pred: NodeInfo
    description: str
    def __init__(self, leaving_node_pred: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class NodeGone(_message.Message):
    __slots__ = ("leaving_node_next", "description")
    LEAVING_NODE_NEXT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    leaving_node_next: NodeInfo
    description: str
    def __init__(self, leaving_node_next: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class Store(_message.Message):
    __slots__ = ("key", "obj_size", "value", "description")
    KEY_FIELD_NUMBER: _ClassVar[int]
    OBJ_SIZE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    obj_size: int
    value: bytes
    description: str
    def __init__(self, key: _Optional[str] = ..., obj_size: _Optional[int] = ..., value: _Optional[bytes] = ..., description: _Optional[str] = ...) -> None: ...

class Retrieve(_message.Message):
    __slots__ = ("key", "searching_node", "description")
    KEY_FIELD_NUMBER: _ClassVar[int]
    SEARCHING_NODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    searching_node: NodeInfo
    description: str
    def __init__(self, key: _Optional[str] = ..., searching_node: _Optional[_Union[NodeInfo, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class Ok(_message.Message):
    __slots__ = ("key", "obj_size", "value", "description")
    KEY_FIELD_NUMBER: _ClassVar[int]
    OBJ_SIZE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    obj_size: int
    value: bytes
    description: str
    def __init__(self, key: _Optional[str] = ..., obj_size: _Optional[int] = ..., value: _Optional[bytes] = ..., description: _Optional[str] = ...) -> None: ...

class NotFound(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Transfer(_message.Message):
    __slots__ = ("key", "value", "description")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: bytes
    description: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ..., description: _Optional[str] = ...) -> None: ...
