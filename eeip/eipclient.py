import encapsulation
import threading
import socket
import struct

class EEIPClient:
    def __init__(self):
        self.__tcpClient_socket = None
        self.__session_handle = 0
        self.__connection_id_o_t = 0
        self.__connection_id_t_o = 0
        self.multicast_address = 0
        self.connection_serial_number = 0

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

        self.__ip_address = encapsulation.Encapsulation.CIPIdentityItem.get_ip_address(address)
        if self.__tcpClient_socket is not None:
            self.__tcpClient_socket.settimeout(5)
            self.__tcpClientSocket.connect((self.__ip_address, self.__port))
            self.__thread = threading.Thread(target=self.__listen, args=())
            self.__thread.start()

    def __listen(self):
        self.__stoplistening = False
        self.__receivedata = bytearray()
        try:
            while not self.__stoplistening:
                if len(self.__receivedata) == 0:
                    self.__receivedata = bytearray()
                    self.__timeout = 500
                    if self.__tcpClientSocket is not None:
                        self.__receivedata = self.__tcpClientSocket.recv(256)
        except socket.timeout:
            self.__receivedata = None

    def close(self):
        """
        Closes  TCP-Socket connection
        """
        if self.__tcpClientSocket is not None:
            self.__stoplistening = True
            self.__tcpClientSocket.shutdown(socket.SHUT_RDWR)
            self.__tcpClientSocket.close()
        self.__connected = False

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
        self.__t_o_iodata = t_o_iodata

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

if __name__ == "__main__":
    eeipclient = EEIPClient()
    eeipclient.ListIdentity()

