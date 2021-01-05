from enum import Enum


class StatusEnum(Enum):
    '''
    Table 2-3.3 Error Codes
    '''
    SUCCESS = 0x0000,
    INVALID_COMMMAND = 0x0001,
    INSUFFICIENT_MEMORY = 0x0002,
    INCORRECT_DATA = 0x0003,
    INVALID_SESSION_HANDLE = 0x0064,
    INVALID_LENGTH = 0x0065,
    UNSUPPORTED_ENCAPSULTATION_PROTOCOL = 0x0069

class CommandsEnum(Enum):
    '''
    Table 2-3.2 Encapsulation Commands
    '''
    NOP = 0x0000,
    LIST_SERVICES = 0x0004,
    LIST_IDENTITY = 0x0063,
    LIST_INTERFACES = 0x0064,
    REGISTER_SESSION = 0x0065,
    UNREGISTER_SESSIOM = 0x0066,
    SEND_RRDATA = 0x006F,
    SENDUNITDATA = 0x0070,
    INDICATE_STATUS = 0x0072,
    CANCEL = 0x0073

class SocketAddress:
    '''
    Socket Address (see section 2-6.3.2)
    '''
    def __init__(self):
        sin_family = int()
        sin_port = int()
        sin_address = int()
        sin_zero = list()

class Encapsulation:

    def __init__(self):
        self.__sender_context = list()
        self.__command_specific_data = list()

    def to_bytes(self):
        returnvalue = list()
        returnvalue.append(self.__command & 0xFF)
        returnvalue.append(self.__command & 0xFF00 >> 8)
        returnvalue.append(self.__length & 0xFF)
        returnvalue.append(self.__length & 0xFF00 >> 8)
        returnvalue.append(self.__session_handle & 0xFF)
        returnvalue.append(self.__session_handle & 0xFF00 >> 8)
        returnvalue.append(self.__session_handle & 0xFF0000 >> 16)
        returnvalue.append(self.__session_handle & 0xFF000000 >> 24)
        returnvalue.append(self.__status & 0xFF)
        returnvalue.append(self.__status & 0xFF00 >> 8)
        returnvalue.append(self.__status & 0xFF0000 >> 16)
        returnvalue.append(self.__status & 0xFF000000 >> 24)
        returnvalue.append(self.__sender_context[0] & 0xFF)
        returnvalue.append(self.__sender_context[1] & 0xFF)
        returnvalue.append(self.__sender_context[2] & 0xFF)
        returnvalue.append(self.__sender_context[3] & 0xFF)
        returnvalue.append(self.__sender_context[4] & 0xFF)
        returnvalue.append(self.__sender_context[5] & 0xFF)
        returnvalue.append(self.__sender_context[6] & 0xFF)
        returnvalue.append(self.__sender_context[7] & 0xFF)
        returnvalue.append(self.__options& 0xFF)
        returnvalue.append(self.__options & 0xFF00 >> 8)
        returnvalue.append(self.__options & 0xFF0000 >> 16)
        returnvalue.append(self.__options & 0xFF000000 >> 24)
        for data in self.__command_specific_data:
            returnvalue.append(data & 0xFF)
        return returnvalue

    class CIPIdentityItem:
        '''
        Table 2-4.4 CIP Identity Item
        '''
        def __init__(self):
            self.item_type_code = int()                                 #Code indicating item type of CIP Identity (0x0C)
            self.item_length = int()                                    #Number of bytes in item which follow (length varies depending on Product Name string)
            self.encapsulation_protocol_version = int()                 #Encapsulation Protocol Version supported (also returned with Register Sesstion reply).
            self.socket_address = SocketAddress()                       #Socket Address (see section 2-6.3.2)
            self.vendor_id1 = int()                                     #Device manufacturers Vendor ID
            self.device_type1 = int()                                   #evice Type of product
            self.product_code1 = int()                                  #Product Code assigned with respect to device type
            self.revision1 = list()                                     #Device revision
            self.status1 = int()                                        #Current status of device
            self.serial_number = int()                                  #Serial number of device
            self.product_name_length = int()
            self.product_name1 = str()                                  #Human readable description of device
            self.state1 = int()                                         #Current state of device

        def get_cip_identity_item(self, starting_byte, receive_data):
            starting_byte = starting_byte + 1
            self.item_type_code = receive_data[0 + starting_byte] | (receive_data[1 + starting_byte] << 8)
            self.item_length = receive_data[2 + starting_byte] | (receive_data[3 + starting_byte] << 8)
            self.encapsulation_protocol_version = receive_data[4 + starting_byte] | (receive_data[5 + starting_byte] << 8)
            self.socket_address.sin_family = receive_data[7 + starting_byte] | (receive_data[6 + starting_byte] << 8)
            self.socket_address.sin_port = receive_data[9 + starting_byte] | (receive_data[8 + starting_byte] << 8)
            self.socket_address.sin_address = receive_data[13 + starting_byte] | (receive_data[12 + starting_byte] << 8) | (receive_data[11 + starting_byte] << 16) | (receive_data[10 + starting_byte] << 24)
            self.vendor_id1 = receive_data[22 + starting_byte] | (receive_data[23 + starting_byte] << 8)
            self.device_type1 = receive_data[24 + starting_byte] | (receive_data[25 + starting_byte] << 8)
            self.product_code1 = receive_data[26 + starting_byte] | (receive_data[27 + starting_byte] << 8)
            self.revision1[0] = receive_data[28 + starting_byte]
            self.revision1[1] = receive_data[29 + starting_byte]
            self.status1 = receive_data[30 + starting_byte] | (receive_data[31 + starting_byte] << 8)
            self.serial_number = receive_data[32 + starting_byte] | (receive_data[33 + starting_byte] << 8) | (
                    receive_data[34 + starting_byte] << 16) | (receive_data[35 + starting_byte] << 24)
            self.product_name_length = receive_data[36 + starting_byte]
            product_name1 = bytearray( self.product_name_length)
            for i in range (0, len(product_name1)-1):
                product_name1 = receive_data[37 + starting_byte + i]
            self.product_name1 = str(product_name1, 'utf-8')
            self.state1 = receive_data[len(receive_data) - 1]

        def get_ip_address(self, address):
            return str(address >> 24) + "." + str(address >> 16) + "." + str(address >> 8) + "." + str(address);

    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self, command):
        self.__command = command

    @property
    def length(self):
        return self.__length

    @length.setter
    def command(self, length):
        self.__length = length

    @property
    def session_handle(self):
        return self.__session_handle

    @session_handle.setter
    def command(self, session_handle):
        self.__session_handle = session_handle

    @property
    def status(self):
        return self.__status

class CommonPacketFormat:
    def __init__(self):
        self.item_count = 2
        self.address_item = 0x0000
        self.address_length = 0
        self.data_item = 0x82                       #0xB2 = Unconnected Data Item
        self.data_length = 8
        self.data = list()
        self.sockaddr_info_item_o_t = 0x8001        #8000 for O->T and 8001 for T->O - Volume 2 Table 2-6.9
        self.sockaddr_info_length = 16
        self.socketaddr_info_o_t = None

    def to_bytes(self):
        if self.socketaddr_info_o_t is not None:
            self.item_count = 3
        returnvalue = list()
        returnvalue.append(self.item_count & 0xFF)
        returnvalue.append(self.item_count & 0xFF00 >> 8)
        returnvalue.append(self.address_item & 0xFF)
        returnvalue.append(self.address_item & 0xFF00 >> 8)
        returnvalue.append(self.address_length & 0xFF)
        returnvalue.append(self.address_length & 0xFF00 >> 8)
        returnvalue.append(self.data_item & 0xFF)
        returnvalue.append(self.data_item & 0xFF00 >> 8)
        returnvalue.append(self.data_length & 0xFF)
        returnvalue.append(self.data_length & 0xFF00 >> 8)
        for item in self.data:
            returnvalue.append(item)

        #Add Socket Address to info Item
        if self.sockaddr_info_item_o_t is not None:
            returnvalue.append(self.sockaddr_info_item_o_t & 0xFF)
            returnvalue.append(self.sockaddr_info_item_o_t & 0xFF00 >> 8)
            returnvalue.append(self.sockaddr_info_length & 0xFF)
            returnvalue.append(self.sockaddr_info_length & 0xFF00 >> 8)

            returnvalue.append(self.sockaddr_info_item_o_t.sin_family & 0xFF00 >> 8)
            returnvalue.append(self.sockaddr_info_item_o_t.sin_family & 0xFF)

            returnvalue.append(self.sockaddr_info_item_o_t.sin_port & 0xFF00 >> 8)
            returnvalue.append(self.sockaddr_info_item_o_t.sin_port & 0xFF)

            returnvalue.append(self.sockaddr_info_item_o_t.sin_address & 0xFF00 >> 24)
            returnvalue.append(self.sockaddr_info_item_o_t.sin_address & 0xFF00 >> 16)
            returnvalue.append(self.sockaddr_info_item_o_t.sin_address & 0xFF00 >> 8)
            returnvalue.append(self.sockaddr_info_item_o_t.sin_address & 0xFF)

            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[0])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[1])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[2])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[3])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[4])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[5])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[6])
            returnvalue.append(self.sockaddr_info_item_o_t.sin_zero[7])

        return returnvalue