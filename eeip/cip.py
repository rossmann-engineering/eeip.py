from enum import Enum


class CIPCommonServices(Enum):
    '''
    Table A-3.1 Volume 1 Chapter A-3
    '''
    GET_ATTRIBUTES_ALL = 0x01,
    SET_ATTRIBUTES_ALL_REQUEST = 0x02,
    GET_ATTRIBUTE_LIST = 0x03,
    SET_ATTRIBUTE_LIST = 0x04,
    RESET = 0x05,
    START = 0x06,
    STOP = 0x07,
    CREATE = 0x08,
    DELETE = 0x09,
    MULTIPLE_SERVICE_PACKET = 0x0A,
    APPLY_ATTRIBUTS = 0x0D,
    GET_ATTRIBUTE_SINGLE = 0x0E,
    SET_ATTRIBUTE_SINGLE = 0x10,
    FIND_NEXT_OBJECT_INSTANCE = 0x11,
    ERROT_RESPONSE = 0x14,
    RESTORE = 0x15,
    SAVE = 0x16,
    NOP = 0x17,
    GET_MEMBER = 0x18,
    SET_MEMBER = 0x19,
    INSERT_MEMBER = 0x1A,
    REMOVE_MEMBER = 0x1B,
    GROUP_SYNC = 0x1C

def get_status_code(code):
    """
    Table B-1.1 CIP General Status Codes
    :param code: Code to get the Status from
    :return: Status Message
    """
    if code == 0x00: return 'Success'
    elif code == 0x01: return 'Connection failure'
    elif code == 0x02: return 'Resource unavailable'
    elif code == 0x03: return 'Invalid Parameter value'
    elif code == 0x04: return 'Path segment error'
    elif code == 0x05: return 'Path destination unknown'
    elif code == 0x06: return 'Partial transfer'
    elif code == 0x07: return 'Connection lost'
    elif code == 0x08: return 'Service not supported'
    elif code == 0x09: return 'Invalid attribute value'
    elif code == 0x0A: return 'Attribute List error'
    elif code == 0x0B: return 'Already in requested mode/state'
    elif code == 0x0C: return 'Object state conflict'
    elif code == 0x0D: return 'Object already exists'
    elif code == 0x0E: return 'Attribute not settable'
    elif code == 0x0F: return 'Privilege violation'
    elif code == 0x10: return 'Device state conflict'
    elif code == 0x11: return 'Reply data too large'
    elif code == 0x12: return 'Fragmentation of a primitive value'
    elif code == 0x13: return 'Not enough data'
    elif code == 0x14: return 'Attribute not supported'
    elif code == 0x15: return 'Too much data'
    elif code == 0x16: return 'Object does not exist'
    elif code == 0x17: return 'Service fragmentation sequence not in progress'
    elif code == 0x18: return 'No stored attribute data'
    elif code == 0x19: return 'Store operation failure'
    elif code == 0x1A: return 'Routing failure, request packet too large'
    elif code == 0x1B: return 'Routing failure, response packet too large'
    elif code == 0x1C: return 'Missing attribute list entry data'
    elif code == 0x1D: return 'Invalid attribute value list'
    elif code == 0x1E: return 'Embedded service error'
    elif code == 0x1F: return 'Vendor specific error'
    elif code == 0x20: return 'Invalid parameter'
    elif code == 0x21: return 'Write-once value or medium atready written'
    elif code == 0x22: return 'Invalid Reply Received'
    elif code == 0x23: return 'Buffer overflow'
    elif code == 0x24: return 'Message format error'
    elif code == 0x25: return 'Key failure path'
    elif code == 0x26: return 'Path size invalid'
    elif code == 0x27: return 'Unecpected attribute list'
    elif code == 0x28: return 'Invalid Member ID'
    elif code == 0x29: return 'Member not settable'
    elif code == 0x2A: return 'Group 2 only Server failure'
    elif code == 0x2B: return 'Unknown Modbus Error'
    else: return 'unknown'

class CIPException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
