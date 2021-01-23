from eeip import encapsulation
import threading
import socket
import struct
import traceback
from eeip import cip
from enum import Enum, IntEnum
import random
import time, datetime


class EEIPClient:
    def __init__(self):
        self.__tcpClient_socket = None
        self.__session_handle = 0
        self.__connection_id_o_t = 0
        self.__connection_id_t_o = 0
        self.multicast_address = 0
        self.__connection_serial_number = 0
        self.__receivedata = bytearray()
        self.__o_t_realtime_format = RealTimeFormat.HEADER32BIT
        self.__t_o_realtime_format = RealTimeFormat.MODELESS
        self.__t_o_connection_type = ConnectionType.MULTICAST
        self.__o_t_connection_type = ConnectionType.POINT_TO_POINT
        self.__requested_packet_rate_o_t = 0x7A120 #500ms
        self.__requested_packet_rate_t_o = 0x7A120 #500ms
        self.__o_t_length = 505
        self.__t_o_length = 505
        self.__o_t_variable_length = True
        self.__t_o_variable_length = True
        self.__o_t_priority = Priority.SCHEDULED
        self.__t_o_priority = Priority.SCHEDULED
        self.__o_t_owner_redundant = True
        self.__t_o_owner_redundant = True
        self.__assembly_object_class = 0x04
        self.__configuration_assembly_instance_id = 0x01
        self.__o_t_instance_id = 0x64
        self.__t_o_instance_id = 0x65
        self.__originator_udp_port = 0x08AE
        self.__target_udp_port = 0x08AE
        self.__o_t_iodata = 256 * [0]
        self.__t_o_iodata = 256 * [0]
        self.__multicastAddress = 0
        self.__lock_receive_data = threading.Lock()


        self.__udp_client_receive_closed = False

    def ListIdentity(self):
        """
        List and identify potential targets. This command shall be sent as broadcast massage using UDP.
        :return: List containing the received informations from all devices
        """
        senddata = bytearray(24)
        senddata[0] = 0x63      #Command for "ListIdentity"
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.settimeout(5)
        #client.bind(("", 44818))
        client.sendto(senddata, ("<broadcast>", 44818))
        while True:
            data, addr = client.recv(1024)
            print("received message: %s" % data)


    def register_session(self, address, port = 0xAF12):
        """
        Sends a RegisterSession command to target to initiate session
        :param address IP-Address of the target device
        :param port Port of the target device (Should be 0xAF12)
        :return: Session Handle
        """
        if self.__session_handle != 0:
            return self.__session_handle
        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.command = encapsulation.CommandsEnum.REGISTER_SESSION
        __encapsulation.length = 4
        __encapsulation.command_specific_data.append(1)     #Protocol Version (Should be set to 1)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)     #Session option shall be set to "0"
        __encapsulation.command_specific_data.append(0)
        self.ip_address = address
        #self.__ip_address = encapsulation.Encapsulation.CIPIdentityItem().get_ip_address(address)
        self.__tcpClient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.__tcpClient_socket is not None:
            self.__tcpClient_socket.settimeout(5)
            self.__tcpClient_socket.connect((address, port))
            self.__thread = threading.Thread(target=self.__listen, args=())
            self.__thread.start()
            self.__tcpClient_socket.send(bytearray(__encapsulation.to_bytes()))

            try:
                while len(self.__receivedata) == 0:
                    pass
            except Exception:
                raise Exception('Read Timeout' + traceback.format_exc())

            self.__session_handle = self.__receivedata[4] | (self.__receivedata[5]) << 8 | (self.__receivedata[6]) << 16 | (self.__receivedata[7]) << 24

            return self.__session_handle;


    def unregister_session(self):
        """
        Sends an UnRegisterSession command to a target to terminate session
        """
        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.command = encapsulation.CommandsEnum.UNREGISTER_SESSIOM
        __encapsulation.length = 0
        __encapsulation.session_handle = self.__session_handle
        self.__tcpClient_socket.send(bytearray(__encapsulation.to_bytes()))
        if self.__tcpClient_socket is not None:
            self.__stoplistening = True
            self.__tcpClient_socket.shutdown(socket.SHUT_RDWR)
            self.__tcpClient_socket.close()
        self.__session_handle = 0


    def get_attribute_single(self, class_id, instance_id, attribute_id):
        """
        Implementation of Common Service "Get_Attribute_Single" - Service Code: 0x0E
        Specification Vol. 1 Appendix A - Chapter A-4.12 - Page A-20
        Returns the contents of the specified attribute.
        :param class_id Class id of requested Attribute
        :param instance_id Instance of Requested Attributes (0 for class Attributes)
        :param attribute_id Requested attribute
        :return: Requested Attribute value
        """
        requested_path = self.get_epath(class_id, instance_id, attribute_id)
        #If the session handle is 0, try to register a session with the predefined IP-Address and Port
        if self.__session_handle == 0:
            self.__session_handle = self.register_session(self.__ip_address, self.__tcp_port)
        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.session_handle = self.__session_handle
        __encapsulation.command = encapsulation.CommandsEnum.SEND_RRDATA
        __encapsulation.length = 18 + len(requested_path)

        #---------------Interface Handle CIP
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        #----------------Interface Handle CIP

        #----------------Timeout
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        #----------------Timeout

        #Common Packet Format (Table 2-6.1)
        common_packet_format = encapsulation.CommonPacketFormat()

        common_packet_format.data_length = 2 + len(requested_path)

        #----------------CIP Command "Get Attribute Single"
        if attribute_id is not None:
            common_packet_format.data.append(int(cip.CIPCommonServices.GET_ATTRIBUTE_SINGLE))
        else:
            common_packet_format.data.append(int(cip.CIPCommonServices.GET_ATTRIBUTES_ALL))

        #---------------CIP Command "Get Attribute Single"

        #----------------Requested Path size (number of 16 bit words)
        common_packet_format.data.append(int(len(requested_path) / 2) & 0xFF);
        #----------------Requested Path size (number of 16 bit words)

        #----------------Path segment for Class ID
        #----------------Path segment for Class ID

        #----------------Path segment for Instance ID
        #----------------Path segment for Instace ID

        #----------------Path segment for Attribute ID
        #----------------Path segment for Attribute ID

        for i in requested_path:
            common_packet_format.data.append(i);


        data_to_write = __encapsulation.to_bytes() + common_packet_format.to_bytes()
        self.__receivedata = bytearray()
        self.__tcpClient_socket.send(bytearray(data_to_write))

        try:
            while len(self.__receivedata) == 0:
                pass
        except Exception:
            raise Exception('Read Timeout')

        #--------------------------BEGIN Error?
        if len(self.__receivedata) > 41:
            if self.__receivedata[42] != 0: #Exception codes see "Table B-1.1 CIP General Status Codes"
                raise cip.CIPException(cip.get_status_code(self.__receivedata[42]))
        #--------------------------END Error?

        returnvalue = list()
        for i in range(len(self.__receivedata) - 44):
            returnvalue.append(self.__receivedata[i+44])

        return returnvalue


    def get_attributes_all(self, class_id, instance_id):
        """
        Implementation of Common Service "Get_Attributes_All" - Service Code: 0x01
        Specification Vol. 1 Appendix A - Chapter A-4.1 - Page A-7
        Returns the contents of the instance or class attributes defined in the object definition.
        :param class_id Class id of requested Attributes
        :param instance_id Instance of Requested Attributes (0 for class Attributes)
        :return: Requested Attributes
        """
        return self.get_attribute_single(class_id, instance_id, None)


    def set_attribute_single(self, class_id, instance_id, attribute_id, value):
        """
        Implementation of Common Service "Set_Attribute_Single" - Service Code: 0x10
        Modifies an attribute value
        Specification Vol. 1 Appendix A - Chapter A-4.13 - Page A-21
        :param class_id Class id of requested Attribute to write
        :param instance_id Instance of Requested Attribute to write (0 for class Attributes)
        :param attribute_id Attribute to write
        :param value value(s) to write in the requested attribute
        """
        requested_path = self.get_epath(class_id, instance_id, attribute_id)
        # If the session handle is 0, try to register a session with the predefined IP-Address and Port
        if self.__session_handle == 0:
            self.__session_handle = self.register_session(self.__ip_address, self.__tcp_port)
        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.session_handle = self.__session_handle
        __encapsulation.command = encapsulation.CommandsEnum.SEND_RRDATA
        __encapsulation.length = 18 + len(requested_path) + len(value)

        # ---------------Interface Handle CIP
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Interface Handle CIP

        # ----------------Timeout
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Timeout

        # Common Packet Format (Table 2-6.1)
        common_packet_format = encapsulation.CommonPacketFormat()

        common_packet_format.data_length = 2 + len(requested_path) + len(value)

        # ----------------CIP Command "Get Attribute Single"
        common_packet_format.data.append(int(cip.CIPCommonServices.SET_ATTRIBUTE_SINGLE))

        # ----------------Requested Path size (number of 16 bit words)
        common_packet_format.data.append(int(len(requested_path) / 2) & 0xFF)
        # ----------------Requested Path size (number of 16 bit words)

        for i in requested_path:
            common_packet_format.data.append(i)

        for i in value:
            common_packet_format.data.append(i)

        data_to_write = __encapsulation.to_bytes() + common_packet_format.to_bytes()
        self.__receivedata = bytearray()
        self.__tcpClient_socket.send(bytearray(data_to_write))

        try:
            while len(self.__receivedata) == 0:
                pass
        except Exception:
            raise Exception('Read Timeout')

        # --------------------------BEGIN Error?
        if len(self.__receivedata) > 41:
            if self.__receivedata[42] != 0:  # Exception codes see "Table B-1.1 CIP General Status Codes"
                raise cip.CIPException(cip.get_status_code(self.__receivedata[42]))
        # --------------------------END Error?

        returnvalue = list()
        for i in range(len(self.__receivedata) - 44):
            returnvalue.append(self.__receivedata[i + 44])

        return returnvalue

    def forward_open(self, large_forward_open = False):
        self.__udp_client_receive_closed = False
        o_t_header_offset = 2
        if (self.__o_t_realtime_format == RealTimeFormat.HEADER32BIT):
            o_t_header_offset = 6
        if (self.__o_t_realtime_format == RealTimeFormat.HEARTBEAT):
            o_t_header_offset = 0

        t_o_header_offset = 2
        if (self.__t_o_realtime_format == RealTimeFormat.HEADER32BIT):
            t_o_header_offset = 6
        if (self.__t_o_realtime_format == RealTimeFormat.HEARTBEAT):
            t_o_header_offset = 0

        length_offset = 5 + (0 if self.__t_o_connection_type == ConnectionType.NULL else 2) + (0 if self.__o_t_connection_type == ConnectionType.NULL else 2)

        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.session_handle = self.__session_handle
        __encapsulation.command = encapsulation.CommandsEnum.SEND_RRDATA
        #!!!!!!!!-----length field at the end

        # ---------------Interface Handle CIP
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Interface Handle CIP

        # ----------------Timeout
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Timeout

        # Common Packet Format (Table 2-6.1)
        common_packet_format = encapsulation.CommonPacketFormat()

        common_packet_format.data_length = 41 + length_offset
        if large_forward_open:
            common_packet_format.data_length += 4

        # ----------------CIP Command "Forward open" (Service code 0x54)
        if not large_forward_open:
            common_packet_format.data.append(0x54)
        # ----------------CIP Command "Large Forward open" (Service code 0x58)
        else:
            common_packet_format.data.append(0x58)

        # ----------------Requested Path Size
        common_packet_format.data.append(2)
        # ----------------Requested Path Size

        # ----------------Path segment for the Class ID
        common_packet_format.data.append(0x20)
        common_packet_format.data.append(6)
        # ----------------Path segment for the Class ID

        # ----------------Path segment for the Instance ID
        common_packet_format.data.append(0x24)
        common_packet_format.data.append(1)
        # ----------------Path segment for the Instance ID

        # ----------------Priority and Time/Tick - Table 3-5.16 (Vol. 1)
        common_packet_format.data.append(0x03)
        # ----------------Priority and Time/Tick - Table 3-5.16 (Vol. 1)

        # ----------------Timeout Ticks - Table 3-5.16 (Vol. 1)
        common_packet_format.data.append(0xfa)
        # ----------------Timeout Ticks - Table 3-5.16 (Vol. 1)

        self.__connection_id_o_t = int(random.random() * 10000000)
        self.__connection_id_t_o = int(random.random() * 10000000 + 1)

        common_packet_format.data.append(self.__connection_id_o_t & 0xFF)
        common_packet_format.data.append((self.__connection_id_o_t & 0xFF00) >> 8)
        common_packet_format.data.append((self.__connection_id_o_t & 0xFF0000) >> 16)
        common_packet_format.data.append((self.__connection_id_o_t & 0xFF000000) >> 24)

        common_packet_format.data.append(self.__connection_id_t_o & 0xFF)
        common_packet_format.data.append((self.__connection_id_t_o & 0xFF00) >> 8)
        common_packet_format.data.append((self.__connection_id_t_o & 0xFF0000) >> 16)
        common_packet_format.data.append((self.__connection_id_t_o & 0xFF000000) >> 24)

        self.__connection_serial_number = int(random.random() * 1000 + 2)
        common_packet_format.data.append(self.__connection_serial_number & 0xFF)
        common_packet_format.data.append((self.__connection_serial_number & 0xFF00) >> 8)

        # ----------------Originator Vendor ID
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0)
        # ----------------Originator Vendor ID

        # ----------------Originator Serial Number
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        # ----------------Originator Serial Number

        # ----------------Timeout Multiplier
        common_packet_format.data.append(3)
        # ----------------Timeout Multiplier

        # ----------------Reserved
        common_packet_format.data.append(0)
        common_packet_format.data.append(0)
        common_packet_format.data.append(0)
        # ----------------Reserved

        # ----------------Requested Packet Rate O->T in Microseconds
        common_packet_format.data.append(self.__requested_packet_rate_o_t & 0xFF)
        common_packet_format.data.append((self.__requested_packet_rate_o_t & 0xFF00) >> 8)
        common_packet_format.data.append((self.__requested_packet_rate_o_t & 0xFF0000) >> 16)
        common_packet_format.data.append((self.__requested_packet_rate_o_t & 0xFF000000) >> 24)
        # ----------------Requested Packet Rate O->T in Microseconds

        # ----------------O->T Network Connection Parameters
        connection_size = self.__o_t_length + o_t_header_offset   #The maximum size in bytes og the data for each direction (were applicable) of the connection. For a variable -> maximum

        # ----------------O->T Network Connection Parameters
        network_connection_parameters = (connection_size & 0x1FF) | (self.__o_t_variable_length << 9) | ((self.__o_t_priority & 0x03) << 10) | ((self.__o_t_connection_type & 0x03) << 13) | (self.__o_t_owner_redundant << 15)
        if large_forward_open:
            network_connection_parameters = (connection_size & 0xFFFF) | (self.__o_t_variable_length << 25) | (
                        (self.__o_t_priority & 0x03) << 26) | ((self.__o_t_connection_type & 0x03) << 29) | (
                                                        self.__o_t_owner_redundant << 31)

        common_packet_format.data.append(network_connection_parameters & 0xFF)
        common_packet_format.data.append((network_connection_parameters & 0xFF00) >> 8)

        if large_forward_open:
            common_packet_format.data.append((network_connection_parameters & 0xFF0000) >> 16)
            common_packet_format.data.append((network_connection_parameters & 0xFF000000) >> 14)
        # ----------------O->T Network Connection Parameters

        # ----------------Requested Packet Rate T->O in Microseconds
        common_packet_format.data.append(self.__requested_packet_rate_t_o & 0xFF)
        common_packet_format.data.append((self.__requested_packet_rate_t_o & 0xFF00) >> 8)
        common_packet_format.data.append((self.__requested_packet_rate_t_o & 0xFF0000) >> 16)
        common_packet_format.data.append((self.__requested_packet_rate_t_o & 0xFF000000) >> 24)
        # ----------------Requested Packet Rate T->O in Microseconds

        # ----------------T->O Network Connection Parameters
        connection_size = self.__t_o_length + t_o_header_offset   #The maximum size in bytes og the data for each direction (were applicable) of the connection. For a variable -> maximum

        network_connection_parameters = (connection_size & 0x1FF) | (self.__t_o_variable_length << 9) | ((self.__t_o_priority & 0x03) << 10) | ((self.__t_o_connection_type & 0x03) << 13) | (self.__t_o_owner_redundant << 15)
        if large_forward_open:
            network_connection_parameters = (connection_size & 0xFFFF) | (self.__t_o_variable_length << 25) | (
                        (self.__t_o_priority & 0x03) << 26) | ((self.__t_o_connection_type & 0x03) << 29) | (
                                                        self.__t_o_owner_redundant << 31)

        common_packet_format.data.append(network_connection_parameters & 0xFF)
        common_packet_format.data.append((network_connection_parameters & 0xFF00) >> 8)

        if large_forward_open:
            common_packet_format.data.append((network_connection_parameters & 0xFF0000) >> 16)
            common_packet_format.data.append((network_connection_parameters & 0xFF000000) >> 14)
        # ----------------T->O Network Connection Parameters

        # ----------------Transport Type / Trigger commonPacketFormat.Data.Add(0x01);
        # X - ------ = 0 = Client; 1 = Server
        # -XXX - --- = Production Trigger, 0 = Cyclic, 1 = CoS, 2 = Application Object
        # ----XXXX = Transport class , 0 = Class 0, 1 = Class 1, 2 = Class 2, 3 = Class 3
        # ----------------Transport Type Trigger
        common_packet_format.data.append(0x01)
        # Connection Path size
        common_packet_format.data.append(0x02 + (0 if self.__o_t_connection_type == ConnectionType.NULL else 1) + (0 if self.__t_o_connection_type == ConnectionType.NULL else 1))
        # Verbindugspfad
        common_packet_format.data.append(0x20)
        common_packet_format.data.append(self.__assembly_object_class)
        common_packet_format.data.append(0x24)
        common_packet_format.data.append(self.__configuration_assembly_instance_id)
        if self.__o_t_connection_type != ConnectionType.NULL:
            common_packet_format.data.append(0x2C)
            common_packet_format.data.append(self.__o_t_instance_id)
        if self.__t_o_connection_type != ConnectionType.NULL:
            common_packet_format.data.append(0x2C)
            common_packet_format.data.append(self.__t_o_instance_id)

        # AddSocket Addrress Item O->T
        common_packet_format.socketaddr_info_o_t = encapsulation.SocketAddress()
        common_packet_format.socketaddr_info_o_t.sin_port = self.__originator_udp_port
        common_packet_format.socketaddr_info_o_t.sin_family = 2

        if self.__o_t_connection_type == ConnectionType.MULTICAST:
            multicast_response_address = self.get_multicast_address(self.ip2int(self.__ip_address))

            common_packet_format.socketaddr_info_o_t.sin_address = multicast_response_address
            self.__multicastAddress = common_packet_format.socketaddr_info_o_t.sin_address
        else:
            common_packet_format.socketaddr_info_o_t.sin_address = 0

        __encapsulation.length = len(common_packet_format.to_bytes()) + 6

        data_to_write = __encapsulation.to_bytes() + common_packet_format.to_bytes()

        self.__receivedata = bytearray()
        self.__tcpClient_socket.send(bytearray(data_to_write))

        try:
            while len(self.__receivedata) == 0:
                pass
        except Exception:
            raise Exception('Read Timeout')

        # --------------------------BEGIN Error?
        if len(self.__receivedata) > 41:
            if self.__receivedata[42] != 0:  # Exception codes see "Table B-1.1 CIP General Status Codes"
                if self.__receivedata[42] == 1:
                    if self.__receivedata[43] == 0:

                        raise cip.CIPException(("Connection failure, General Status Code: " + str(self.__receivedata[42])))
                    else: #TODO Error Code from Connection Manager Object
                        raise cip.CIPException(("Connection failure, General Status Code: " + str(self.__receivedata[42]) + " Additional Status Code: " + str(self.__receivedata[44] | (self.__receivedata[45] << 8))))
                else:
                    raise cip.CIPException(cip.get_status_code(self.__receivedata[42]))
        # --------------------------END Error?
        item_count = self.__receivedata[30] + (self.__receivedata[31] << 8)
        length_unconnected_data_item = self.__receivedata[38] + (self.__receivedata[39] << 8)
        self.__connection_id_o_t = self.__receivedata[44] + (self.__receivedata[45] << 8) + (self.__receivedata[46] << 16) + (self.__receivedata[47] << 24)
        self.__connection_id_t_o = self.__receivedata[48] + (self.__receivedata[49] << 8) + (
                    self.__receivedata[50] << 16) + (self.__receivedata[51] << 24)

        #Is there a SocketInfoItem?
        number_of_current_item = 0
        socket_info_item = encapsulation.SocketAddress()
        while item_count > 2:
            type_id = self.__receivedata[40 + length_unconnected_data_item + 20 * number_of_current_item] + (self.__receivedata[40 + length_unconnected_data_item + 21 * number_of_current_item] << 8)
            if type_id == 0x8001:
                socket_info_item = encapsulation.SocketAddress()
                socket_info_item.sin_address = self.__receivedata[40 + length_unconnected_data_item + 11 + 20 * number_of_current_item] + (self.__receivedata[40 + length_unconnected_data_item + 10 + 20 * number_of_current_item] << 8) + (self.__receivedata[40 + length_unconnected_data_item + 9 + 20 * number_of_current_item] << 16) + (self.__receivedata[40 + length_unconnected_data_item + 8 + 20 * number_of_current_item] << 24)
                socket_info_item.sin_port = self.__receivedata[40 + length_unconnected_data_item + 7 + 20 * number_of_current_item] + (self.__receivedata[40 + length_unconnected_data_item + 6 + 20 * number_of_current_item] << 8)
                if self.__t_o_connection_type == ConnectionType.MULTICAST:
                    self.__multicastAddress = socket_info_item.sin_address
                self.__target_udp_port = socket_info_item.sin_port
            number_of_current_item = number_of_current_item + 1
            item_count = item_count - 1

        self.__udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.__udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__udp_server_socket.bind(('', self.__originator_udp_port))
        if self.__t_o_connection_type == ConnectionType.MULTICAST:
            mc_address = self.int2ip(self.__multicastAddress)
            group = socket.inet_aton(mc_address)
            mreq = struct.pack('=4sL', group, socket.INADDR_ANY)
            self.__udp_server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__udp_recv_thread = threading.Thread(target=self.__udp_listen, args=())
        self.__udp_recv_thread.daemon = True
        self.__udp_recv_thread.start()
        self.__udp_send_thread = threading.Thread(target=self.__send_udp, args=())
        self.__udp_send_thread.daemon = True
        self.__udp_send_thread.start()


    def forward_close(self):

        length_offset = 5 + (0 if self.__t_o_connection_type == ConnectionType.NULL else 2) + (0 if self.__o_t_connection_type == ConnectionType.NULL else 2)

        __encapsulation = encapsulation.Encapsulation()
        __encapsulation.session_handle = self.__session_handle
        __encapsulation.command = encapsulation.CommandsEnum.SEND_RRDATA
        __encapsulation.length = 16 + 17 + length_offset

        # ---------------Interface Handle CIP
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Interface Handle CIP

        # ----------------Timeout
        __encapsulation.command_specific_data.append(0)
        __encapsulation.command_specific_data.append(0)
        # ----------------Timeout

        # Common Packet Format (Table 2-6.1)
        common_packet_format = encapsulation.CommonPacketFormat()
        common_packet_format.item_count = 0x02

        common_packet_format.address_item = 0
        common_packet_format.address_length = 0

        common_packet_format.data_item = 0xB2
        common_packet_format.data_length = 17 + length_offset

        # ----------------CIP Command "Forward Close"
        common_packet_format.data.append(0x4E)
        # ----------------CIP Command "Forward Close"

        # ----------------Requested Path size
        common_packet_format.data.append(2)
        # ----------------Requested Path size

        # ----------------Path segment for Class ID
        common_packet_format.data.append(0x20)
        common_packet_format.data.append(6)
        # ----------------Path segment for Class ID

        # ----------------Path segment for Instance ID
        common_packet_format.data.append(0x24)
        common_packet_format.data.append(1)
        # ----------------Path segment for Instance ID

        # ----------------Priority and Time/Tick - Table  3-5.16 (Vol. 1)
        common_packet_format.data.append(0x03)
        # ----------------Priority and Time/Tick - Table  3-5.16 (Vol. 1)

        # ----------------Timeout Ticks - Table 3-5.16 (Vol. 1)
        common_packet_format.data.append(0xFA)
        # ----------------Timeout Ticks - Table  3-5.16 (Vol. 1)

        # ----------------Connection serial number
        common_packet_format.data.append(self.__connection_serial_number & 0xFF)
        common_packet_format.data.append((self.__connection_serial_number & 0xFF00) >> 8)
        # ----------------Connection serial number

        # ----------------Originator Vendor ID
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0)
        # ----------------Originator Vendor ID

        # ----------------Originator Serial Number
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        common_packet_format.data.append(0xFF)
        # ----------------Originator Serial Number

        # Connection Path size
        common_packet_format.data.append(0x02 + (0 if self.__o_t_connection_type == ConnectionType.NULL else 1) + (
            0 if self.__t_o_connection_type == ConnectionType.NULL else 1))

        # ----------------Reserved
        common_packet_format.data.append(0x0)
        # ----------------Reserved

        # Verbindugspfad
        common_packet_format.data.append(0x20)
        common_packet_format.data.append(self.__assembly_object_class)
        common_packet_format.data.append(0x24)
        common_packet_format.data.append(self.__configuration_assembly_instance_id)
        if self.__o_t_connection_type != ConnectionType.NULL:
            common_packet_format.data.append(0x2C)
            common_packet_format.data.append(self.__o_t_instance_id)
        if self.__t_o_connection_type != ConnectionType.NULL:
            common_packet_format.data.append(0x2C)
            common_packet_format.data.append(self.__t_o_instance_id)
        try:
            data_to_write = __encapsulation.to_bytes() + common_packet_format.to_bytes()
            self.__receivedata = bytearray()
            self.__tcpClient_socket.send(bytearray(data_to_write))
        except Exception:       #Handle exception to allow to close the connection if closed from the target before
            pass




        try:
            while len(self.__receivedata) == 0:
                pass
        except Exception:
            raise Exception('Read Timeout')

        # --------------------------BEGIN Error?
        if len(self.__receivedata) > 41:
            if self.__receivedata[42] != 0:  # Exception codes see "Table B-1.1 CIP General Status Codes"
                raise cip.CIPException(cip.get_status_code(self.__receivedata[42]))
        # --------------------------END Error?

        self.__stoplistening_udp = True
        self.__stoplistening = True




    def __udp_listen(self):
        self.__stoplistening_udp = False
        self.__receivedata_udp = bytearray()
        try:
            while not self.__stoplistening_udp:
                bytesAddressPair = self.__udp_server_socket.recvfrom(564)
                message = bytesAddressPair[0]
                address = bytesAddressPair[1]
                __receivedata_udp = message
                print (message)
                if len(__receivedata_udp) > 20:
                    connection_id = __receivedata_udp[6] + (__receivedata_udp[7] << 8) + (__receivedata_udp[8] << 16) + (__receivedata_udp[9] << 24)
                if connection_id == self.__connection_id_t_o:
                    header_offset = 0
                    if self.__t_o_realtime_format == RealTimeFormat.HEADER32BIT:
                        header_offset = 4
                    self.__lock_receive_data.acquire()
                    self.__t_o_iodata = list()
                    for i in range(0, len(__receivedata_udp)-20-header_offset):
                        self.__t_o_iodata.append(__receivedata_udp[20+i+header_offset])
                    self.__lock_receive_data.release()
                    self.__last_received_implicit_message = datetime.datetime.utcnow()
                    print(self.__t_o_iodata)

        except Exception:
            if self.__lock_receive_data.locked():
                self.__lock_receive_data.release()

            self.__receivedata = bytearray()

    def __send_udp(self):
        sequence_count = 0
        sequence = 0
        while not self.__stoplistening_udp:
            message = list()

            #-------------------Item Count
            message.append(2)
            message.append(0)
            # -------------------Item Count

            # -------------------Type ID
            message.append(0x02)
            message.append(0x80)
            # -------------------Type ID

            # -------------------Length
            message.append(0x08)
            message.append(0x00)
            # -------------------Length

            # -------------------Connection ID
            message.append(self.__connection_id_o_t & 0xFF)
            message.append((self.__connection_id_o_t & 0xFF00) >> 8)
            message.append((self.__connection_id_o_t & 0xFF0000) >> 16)
            message.append((self.__connection_id_o_t & 0xFF000000) >> 24)
            # -------------------Connection ID

            # -------------------sequence count
            sequence_count += 1
            message.append(sequence_count & 0xFF)
            message.append((sequence_count & 0xFF00) >> 8)
            message.append((sequence_count & 0xFF0000) >> 16)
            message.append((sequence_count & 0xFF000000) >> 24)
            # -------------------sequence count

            # -------------------Type ID
            message.append(0xB1)
            message.append(0x00)
            # -------------------Type ID

            header_offset = 0
            if self.__o_t_realtime_format  == RealTimeFormat.HEADER32BIT:
                header_offset = 4
            o_t_length = self.__o_t_length + header_offset + 2

            # -------------------Length
            message.append(o_t_length & 0xFF)
            message.append((o_t_length & 0xFF00) >> 8)
            # -------------------Length

            # -------------------Sequence count
            sequence += sequence
            if self.__o_t_realtime_format != RealTimeFormat.HEARTBEAT:
                message.append(sequence & 0xFF)
                message.append((sequence & 0xFF00) >> 8)
            # -------------------Sequence count

            if self.__o_t_realtime_format == RealTimeFormat.HEADER32BIT:
                message.append(1)
                message.append(0)
                message.append(0)
                message.append(0)
            # -------------------write data
            self.o_t_iodata[0] = self.o_t_iodata[0] + 1
            for i in range(0, self.__o_t_length):
                message.append(self.o_t_iodata[i])
            # -------------------write data

            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP

            self.__udp_server_socket.sendto(bytearray(message), (self.__ip_address, self.__target_udp_port))
            time.sleep(self.__requested_packet_rate_o_t/1000000)


    def __listen(self):
        self.__stoplistening = False
        self.__receivedata = bytearray()
        try:
            while not self.__stoplistening:
                if len(self.__receivedata) == 0:
                    #self.__receivedata = bytearray()
                    self.__timeout = 500
                    if self.__tcpClient_socket is not None:
                        self.__receivedata = self.__tcpClient_socket.recv(255)
                        print (self.__receivedata)
        except socket.timeout:
            self.__receivedata = bytearray()

    def close(self):
        """
        Closes  TCP-Socket connection
        """
        if self.__tcpClientSocket is not None:
            self.__stoplistening = True
            self.__tcpClientSocket.shutdown(socket.SHUT_RDWR)
            self.__tcpClientSocket.close()
        self.__connected = False

    def get_epath(self, class_id, instance_id, attribute_id):
        """
        Get the Encrypted Request Path - See Volume 1 Appendix C (C9)
        e.g. for 8 Bit: 20 05 24 02 30 01
        for 16 Bit: 21 00 05 00 24 02 30 01
        :param class_id: Requested Class ID
        :param instance_id: Requested Instance ID
        :param attribute_id: Requested Attribute ID - if "0" the attribute will be ignored
        :return: Encrypted Request Path
        """
        returnvalue = list()
        if class_id < 0xff:
            returnvalue.append(0x20)
            returnvalue.append(class_id & 0xFF)

        else:
            returnvalue.append(0x21)
            returnvalue.append(0)
            returnvalue.append(class_id & 0x00FF)
            returnvalue.append((class_id & 0xFF00) >> 8)

        if instance_id < 0xff:
            returnvalue.append(0x24)
            returnvalue.append(instance_id & 0xFF)
        else:
            returnvalue.append(0x25)
            returnvalue.append(0)
            returnvalue.append(instance_id & 0x00FF)
            returnvalue.append((instance_id & 0xFF00) >> 8)

        if attribute_id != None:
            if attribute_id < 0xff:
                returnvalue.append(0x30)
                returnvalue.append(attribute_id & 0xFF)
            else:
                returnvalue.append(0x31)
                returnvalue.append(0)
                returnvalue.append(attribute_id & 0x00FF)
                returnvalue.append((attribute_id & 0xFF00) >> 8)
        return returnvalue


    def ip2int(addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    def int2ip(self, addr):
        return socket.inet_ntoa(struct.pack("!I", addr))

    def get_multicast_address (device_ip_address):
        cip_mcast_base_addr = 0xEFC00100
        cip_host_mask = 0x3FF
        netmask = 0

        #Class A Network?
        if device_ip_address <= 0x7FFFFFFF:
            netmask = 0xFF000000
        #Class B Network?
        if device_ip_address >= 0x80000000 and device_ip_address <= 0xBFFFFFFF:
            netmask = 0xFFFF0000
        #Class C Network?
        if device_ip_address >= 0xC0000000 and device_ip_address <= 0xDFFFFFFF:
            netmask = 0xFFFFFF00

        host_id = device_ip_address & ~netmask
        mcast_index = host_id - 1
        mcast_index = mcast_index & cip_host_mask

        return (cip_mcast_base_addr + mcast_index*32)

    @property
    def tcp_port(self):
        """
        TCP-Port of the Server
        """
        return self.__tcp_port

    @tcp_port.setter
    def tcp_port(self, tcp_port):
        """
        TCP-Port of the Server
        """
        self.__tcp_port = tcp_port

    @property
    def target_udp_port(self):
        """
        UDP-Port of the IO-Adapter - Standard is 0xAF12
        """
        return self.__target_udp_port

    @target_udp_port.setter
    def target_udp_port(self, target_udp_port):
        """
        UDP-Port of the IO-Adapter - Standard is 0xAF12
        """
        self.__target_udp_port = target_udp_port

    @property
    def originator_udp_port(self):
        """
        UDP-Port of the Scanner - Standard is 0xAF12
        """
        return self.__originator_udp_port

    @originator_udp_port.setter
    def originator_udp_port(self, originator_udp_port):
        """
        UDP-Port of the Scanner - Standard is 0xAF12
        """
        self.__originator_udp_port = originator_udp_port

    @property
    def ip_address(self):
        """
        IP-Address of the Ethernet/IP Device
        """
        return self.__ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """
        IP-Address of the Ethernet/IP Device
        """
        self.__ip_address = ip_address

    @property
    def requested_packet_rate_o_t(self):
        """
        Requested Packet Rate (RPI) in ms Originator -> Target for implicit messaging (Default 0x7A120 -> 500ms)
        """
        return self.__requested_packet_rate_o_t

    @requested_packet_rate_o_t.setter
    def requested_packet_rate_o_t(self, requested_packet_rate_o_t):
        """
        Requested Packet Rate (RPI) in ms Originator -> Target for implicit messaging (Default 0x7A120 -> 500ms)
        """
        self.__requested_packet_rate_o_t = requested_packet_rate_o_t

    @property
    def requested_packet_rate_t_o(self):
        """
        Requested Packet Rate (RPI) in ms Target -> Originator for implicit messaging (Default 0x7A120 -> 500ms)
        """
        return self.__requested_packet_rate_t_o

    @requested_packet_rate_t_o.setter
    def requested_packet_rate_t_o(self, requested_packet_rate_t_o):
        """
        Requested Packet Rate (RPI) in ms Target -> Originator for implicit messaging (Default 0x7A120 -> 500ms)
        """
        self.__requested_packet_rate_t_o = requested_packet_rate_t_o

    @property
    def o_t_owner_redundant(self):
        """
        "1" Indicates that multiple connections are allowed Target -> Originator for Implicit-Messaging (Default: TRUE)
        For forward open
        """
        return self.__o_t_owner_redundant

    @o_t_owner_redundant.setter
    def o_t_owner_redundant(self, o_t_owner_redundant):
        """
        "1" Indicates that multiple connections are allowed Target -> Originator for Implicit-Messaging (Default: TRUE)
        For forward open
        """
        self.__o_t_owner_redundant = o_t_owner_redundant

    @property
    def t_o_owner_redundant(self):
        """
        "1" Indicates that multiple connections are allowed Originator -> Target for Implicit-Messaging (Default: TRUE)
        For forward open
        """
        return self.__t_o_owner_redundant

    @t_o_owner_redundant.setter
    def t_o_owner_redundant(self, t_o_owner_redundant):
        """
        "1" Indicates that multiple connections are allowed Originator -> Target for Implicit-Messaging (Default: TRUE)
        For forward open
        """
        self.__t_o_owner_redundant = t_o_owner_redundant

    @property
    def o_t_variable_length(self):
        """
        With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.
        With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
        Originator -> Target for Implicit Messaging (Default: True (Variable length))        For forward open
        """
        return self.__o_t_variable_length

    @o_t_variable_length.setter
    def o_t_variable_length(self, o_t_variable_length):
        """
        With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.
        With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
        Originator -> Target for Implicit Messaging (Default: True (Variable length))        For forward open
        """
        self.__o_t_variable_length = o_t_variable_length

    @property
    def t_o_variable_length(self):
        """
        With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.
        With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
        Target -> Originator for Implicit Messaging (Default: True (Variable length))        For forward open
        """
        return self.__t_o_variable_length

    @t_o_variable_length.setter
    def t_o_variable_length(self, t_o_variable_length):
        """
        With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.
        With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
        Target -> Originator for Implicit Messaging (Default: True (Variable length))        For forward open
        """
        self.__t_o_variable_length = t_o_variable_length

    @property
    def o_t_length(self):
        """
        The maximum size in bytes (only pure data woithout sequence count and 32-Bit Real Time Header (if present)) from Target -> Originator for Implicit Messaging (Default: 505)
        Forward open max 505
        """
        return self.__o_t_length

    @o_t_length.setter
    def o_t_length(self, o_t_length):
        """
        The maximum size in bytes (only pure data without sequence count and 32-Bit Real Time Header (if present)) from Target -> Originator for Implicit Messaging (Default: 505)
        Forward open max 505
        """
        self.__o_t_length = o_t_length


    @property
    def t_o_length(self):
        """
        The maximum size in bytes (only pure data without sequence count and 32-Bit Real Time Header (if present)) from Originator -> Target for Implicit Messaging (Default: 505)
        Forward open max 505
        """
        return self.__t_o_length

    @t_o_length.setter
    def t_o_length(self, t_o_length):
        """
        The maximum size in bytes (only pure data without sequence count and 32-Bit Real Time Header (if present)) from Originator -> Target for Implicit Messaging (Default: 505)
        Forward open max 505
        """
        self.__t_o_length = t_o_length

    @property
    def o_t_connection_type(self):
        """
        Connection Type Target -> Originator for Implicit Messaging (Default: ConnectionType.Multicast)
        """
        return self.__o_t_connection_type

    @o_t_connection_type.setter
    def o_t_connection_type(self, o_t_connection_type):
        """
        Connection Type Target -> Originator for Implicit Messaging (Default: ConnectionType.Multicast)
        """
        self.__o_t_connection_type = o_t_connection_type

    @property
    def t_o_connection_type(self):
        """
        Priority Originator -> Target for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        return self.__t_o_connection_type

    @t_o_connection_type.setter
    def t_o_connection_type(self, t_o_connection_type):
        """
        Priority Originator -> Target for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        self.__t_o_connection_type = t_o_connection_type

    @property
    def o_t_priority(self):
        """
        Priority Originator -> Target for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        return self.__o_t_priority

    @o_t_priority.setter
    def o_t_priority(self, o_t_priority):
        """
        Priority Originator -> Target for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        self.__o_t_priority = o_t_priority

    @property
    def t_o_priority(self):
        """
        Priority Target -> Originator for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        return self.__t_o_priority

    @t_o_priority.setter
    def t_o_priority(self, t_o_priority):
        """
        Priority Target -> Originator for Implicit Messaging (Default: Priority.Scheduled)
        Could be: Priority.Scheduled; Priority.High; Priority.Low; Priority.Urgent
        """
        self.__t_o_priority = t_o_priority

    @property
    def o_t_instance_id(self):
        """
        Class Assembly (Consuming IO-Path - Outputs) Originator -> Target for Implicit Messaging (Default: 0x64)
        """
        return self.__o_t_instance_id

    @o_t_instance_id.setter
    def o_t_instance_id(self, o_t_instance_id):
        """
        Class Assembly (Consuming IO-Path - Outputs) Originator -> Target for Implicit Messaging (Default: 0x64)
        """
        self.__o_t_instance_id = o_t_instance_id


    @property
    def t_o_instance_id(self):
        """
        Class Assembly (Producing IO-Path - Inputs) Target -> Originator for Implicit Messaging (Default: 0x64)
        """
        return self.__t_o_instance_id

    @t_o_instance_id.setter
    def t_o_instance_id(self, t_o_instance_id):
        """
        Class Assembly (Producing IO-Path - Inputs) Target -> Originator for Implicit Messaging (Default: 0x64)
        """
        self.__t_o_instance_id = t_o_instance_id

    @property
    def o_t_iodata(self):
        """
        Provides Access to the Class 1 Real-Time IO-Data Originator -> Target for Implicit Messaging
        """
        return self.__o_t_iodata

    @o_t_iodata.setter
    def o_t_iodata(self, o_t_iodata):
        """
        Provides Access to the Class 1 Real-Time IO-Data Originator -> Target for Implicit Messaging
        """
        self.__o_t_iodata = o_t_iodata

    @property
    def t_o_iodata(self):
        """
        Provides Access to the Class 1 Real-Time IO-Data Target -> Originator for Implicit Messaging
        """
        return self.__t_o_iodata

    @t_o_iodata.setter
    def t_o_iodata(self, t_o_iodata):
        """
        Provides Access to the Class 1 Real-Time IO-Data Target -> Originator for Implicit Messaging
        """
        self.__lock_receive_data.acquire()
        self.__t_o_iodata = t_o_iodata
        self.__lock_receive_data.release()

    @property
    def o_t_realtime_format(self):
        """
        Used Real-Time Format Originator -> Target for Implicit Messaging (Default: RealTimeFormat.Header32Bit)
        Possible Values: RealTimeFormat.Header32Bit; RealTimeFormat.Heartbeat; RealTimeFormat.ZeroLength; RealTimeFormat.Modeless
        """
        return self.__o_t_realtime_format

    @o_t_realtime_format.setter
    def o_t_realtime_format(self, o_t_realtime_format):
        """
        Used Real-Time Format Originator -> Target for Implicit Messaging (Default: RealTimeFormat.Header32Bit)
        Possible Values: RealTimeFormat.Header32Bit; RealTimeFormat.Heartbeat; RealTimeFormat.ZeroLength; RealTimeFormat.Modeless
        """
        self.__o_t_realtime_format = o_t_realtime_format

    @property
    def t_o_realtime_format(self):
        """
        Used Real-Time Format Target -> Originator for Implicit Messaging (Default: RealTimeFormat.Modeless)
        Possible Values: RealTimeFormat.Header32Bit; RealTimeFormat.Heartbeat; RealTimeFormat.ZeroLength; RealTimeFormat.Modeless
        """
        return self.__t_o_realtime_format

    @t_o_realtime_format.setter
    def t_o_realtime_format(self, t_o_realtime_format):
        """
        Used Real-Time Format Target -> Originator for Implicit Messaging (Default: RealTimeFormat.Modeless)
        Possible Values: RealTimeFormat.Header32Bit; RealTimeFormat.Heartbeat; RealTimeFormat.ZeroLength; RealTimeFormat.Modeless
        """
        self.__t_o_realtime_format = t_o_realtime_format

    @property
    def assembly_object_class(self):
        """
        AssemblyObject for the Configuration Path in case of Implicit Messaging (Standard: 0x04)
        """
        return self.__assembly_object_class

    @assembly_object_class.setter
    def assembly_object_class(self, assembly_object_class):
        """
        AssemblyObject for the Configuration Path in case of Implicit Messaging (Standard: 0x04)
        """
        self.__assembly_object_class = assembly_object_class

    @property
    def configuration_assembly_instance_id(self):
        """
        ConfigurationAssemblyInstanceID is the InstanceID of the configuration Instance in the Assembly Object Class (Standard: 0x01)
        """
        return self.__configuration_assembly_instance_id

    @configuration_assembly_instance_id.setter
    def configuration_assembly_instance_id(self, configuration_assembly_instance_id):
        """
        ConfigurationAssemblyInstanceID is the InstanceID of the configuration Instance in the Assembly Object Class (Standard: 0x01)
        """
        self.__configuration_assembly_instance_id = configuration_assembly_instance_id

    @property
    def last_received_implicit_message(self):
        return self.__last_received_implicit_message

    @last_received_implicit_message.setter
    def last_received_implicit_message(self, last_received_implicit_message):
        self.__last_received_implicit_message = last_received_implicit_message

class ConnectionType(IntEnum):
    NULL = 0,
    MULTICAST = 1,
    POINT_TO_POINT = 2

class Priority(IntEnum):
    LOW = 0,
    HIGH = 1,
    SCHEDULED = 2
    URGENT = 3

class RealTimeFormat(IntEnum):
    MODELESS = 0,
    ZEROLENGTH = 1,
    HEARTBEAT = 2
    HEADER32BIT = 3


if __name__ == "__main__":
    eeipclient = EEIPClient()
    eeipclient.register_session('192.168.178.52')
    eeipclient.o_t_length = 1
    eeipclient.t_o_length = 8
    eeipclient.forward_open()
    #print(eeipclient.get_attribute_single(4,0x64,3))
    #eeipclient.set_attribute_single(4,0x64,3,[1])
    #print(eeipclient.get_attributes_all(1, 1))
    time.sleep(5)
    eeipclient.forward_close()
    eeipclient.unregister_session()

