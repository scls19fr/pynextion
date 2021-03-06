from enum import Enum
import ctypes
from .constants import Return


class Event:
    class Touch(Enum):
        Press = 0x01
        Release = 0x00


def has_end(msg):
    return msg[-1] == 0xff and msg[-2] == 0xff and msg[-3] == 0xff


def ensure_has_end(msg):
    if not has_end(msg):
        raise(Exception("Message must end with 0xff 0xff 0xff"))


class AbstractMsgEvent:
    EXPECTED_LENGTH = None
    FIRST_BYTE = None

    @classmethod
    def ensure_has_expected_length(cls, msg):
        expected_length = cls.EXPECTED_LENGTH
        n = len(msg)
        if expected_length is not None and n != expected_length:
            raise(Exception("Event message must have %d bytes not %d" % (expected_length, n)))

    @classmethod
    def ensure_has_expected_first_byte(cls, first_byte):
        expected_first_byte = cls.FIRST_BYTE
        if first_byte != expected_first_byte:
            raise(Exception("Event message must have %d as first byte not %d" % (expected_first_byte, first_byte)))


class TouchEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = 7
    FIRST_BYTE = Return.Code.EVENT_TOUCH_HEAD

    code = None
    pid = None
    cid = None
    tevts = None

    def __init__(self, code, pid, cid, tevts):
        self.code = code
        self.pid = pid
        self.cid = cid
        self.tevts = tevts

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        pid = int(msg[1])
        cid = int(msg[2])
        tevts = Event.Touch(msg[3])
        return TouchEvent(code, pid, cid, tevts)


class CurrentPageIDHeadEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = 5
    FIRST_BYTE = Return.Code.CURRENT_PAGE_ID_HEAD

    code = None
    pid = None

    def __init__(self, code, pid):
        self.code = code
        self.pid = pid

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        pid = int(msg[1])
        return CurrentPageIDHeadEvent(code, pid)


class PositionHeadEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = 9
    FIRST_BYTE = Return.Code.EVENT_POSITION_HEAD

    code = None
    x = None
    y = None
    tevts = None

    def __init__(self, code, x, y, tevts):
        self.code = code
        self.x = x
        self.y = y
        self.tevts = tevts

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        x = (msg[1] << 8) + msg[2]
        y = (msg[3] << 8) + msg[4]
        tevts = Event.Touch(msg[5])
        return PositionHeadEvent(code, x, y, tevts)


class SleepPositionHeadEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = 9
    FIRST_BYTE = Return.Code.EVENT_SLEEP_POSITION_HEAD

    code = None
    x = None
    y = None
    tevts = None

    def __init__(self, code, x, y, tevts):
        self.code = code
        self.x = x
        self.y = y
        self.tevts = tevts

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        x = (msg[1] << 8) + msg[2]
        y = (msg[3] << 8) + msg[4]
        tevts = Event.Touch(msg[5])
        return SleepPositionHeadEvent(code, x, y, tevts)


class StringHeadEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = None
    FIRST_BYTE = Return.Code.STRING_HEAD

    code = None
    value = None

    def __init__(self, code, value):
        self.code = code
        self.value = value

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        value = bytearray(msg[1:-3]).decode("utf-8")
        return StringHeadEvent(code, value)


class NumberHeadEvent(AbstractMsgEvent):
    EXPECTED_LENGTH = 8
    FIRST_BYTE = Return.Code.NUMBER_HEAD

    code = None
    value = None
    signed_value = None

    def __init__(self, code, value, signed_value):
        self.code = code
        self.value = value
        self.signed_value = signed_value

    @classmethod
    def parse(cls, msg):
        ensure_has_end(msg)
        cls.ensure_has_expected_length(msg)
        code = Return.Code(msg[0])
        cls.ensure_has_expected_first_byte(code)
        value = msg[1] + (msg[2] << 8) + (msg[3] << 16) + (msg[4] << 24)
        signed_value = ctypes.c_int32(value).value
        return NumberHeadEvent(code, value, signed_value)


D_BYTE0_EVENT = {
    Return.Code.EVENT_TOUCH_HEAD.value: TouchEvent,
    Return.Code.CURRENT_PAGE_ID_HEAD.value: CurrentPageIDHeadEvent,
    Return.Code.EVENT_POSITION_HEAD.value: PositionHeadEvent,
    Return.Code.EVENT_SLEEP_POSITION_HEAD.value: SleepPositionHeadEvent,
    Return.Code.STRING_HEAD.value: StringHeadEvent,
    Return.Code.NUMBER_HEAD.value: NumberHeadEvent
}


class MsgEvent():
    @classmethod
    def parse(cls, msg):
        evt_typ = D_BYTE0_EVENT[msg[0]]
        return evt_typ.parse(msg)
