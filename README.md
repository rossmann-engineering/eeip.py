## EEIP.py - THE Ethernet/IP compatible Python Module

- Support of Explicit and Implicit Messaging
- Supports IO Scanner and Explicit Message Client functionality

- Object Library with CIP-Definined Objects
- Provides a simple way to access Ethernet/IP Devices without special knowledge about Ethernet/IP. Only few lines of code are required

Visit www.eeip-library.de for more informations and Codesamples

### Table of Contents
1. [Installation](#installation)
2. [Explicit Messaging](#explicitmessaging)   
   2.1.	[Supported Common Services](#supportedcommonservices)  
3. [Examples](#examples)  
   3.1.	[Usage of Implicit Messaging to Read and Write data to Rockwell Point I/O](#example1)  
4. [Library Documentation](#librarydocumentation)   
    4.1.	[Methods](#methods)  
    4.2.	[Properties](#properties)  

<div id="installation"/>

### 1. Installation:

pip install eeip

### Requirements:

Python 3.9

<div id="explicitmessaging"/>

### 2. Explicit Messaging

<div id="supportedcommonservices"/>

#### 2.1 Supported Common Services

Appendix A of the Commmon Industrial Specifiction (Vol. 1) provides informations about the Explicit Messaging Services.  
The following services are supported by the library:

- Get\_Attributes\_All - Service Code: 0x01
- Set\_Attributes\_All - Service Code: 0x02
- Get\_Attribute\_List - Service Code: 0x03
- Set\_Attribute\_List - Service Code: 0x04
- Reset - Service Code: 0x05
- Start - Service Code: 0x06
- Start - Service Code: 0x07
- Create - Service Code: 0x08
- Delete - Service Code: 0x09
- Get\_Attribute\_Single - Service Code: 0x0E
- Set\_Attribute\_Single - Service Code: 0x10
- No Operation (NOP) - Service Code: 0x17

<div id="examples"/>

### 3. Examples

All examples are available in the folder "examples" in the Git-Repository

<div id="example1"/>

#### 3.1 Usage of Implicit Messaging to Read and Write data to Rockwell Point I/O

The Following Hardware Configuration is used in this example  

Allen-Bradley 1734-AENT Ethernet/IP Coupler  
Allen-Bradley 1734-IB4 4-Channel Digital Input Module  
Allen-Bradley 1734-IB4 4-Channel Digital Input Module  
Allen-Bradley 1734-IB4 4-Channel Digital Input Module  
Allen-Bradley 1734-IB4 4-Channel Digital Input Module  
Allen-Bradley 1734-OB4E 4-Channel Digital Output Module  
Allen-Bradley 1734-OB4E 4-Channel Digital Output Module  
Allen-Bradley 1734-OB4E 4-Channel Digital Output Module  
Allen-Bradley 1734-OB4E 4-Channel Digital Output Module  
IP-Address: 192.168.178.107 (By DHCP-Server)  
This example also handles a reconnection procedure if the Impicit Messaging has Timed out  
(If the Property "LastReceivedImplicitMessage" is more than one second ago)  

```python
from eeip import *
import time

eeipclient = EEIPClient()
#Ip-Address of the Ethernet-IP Device (In this case Allen-Bradley 1734-AENT Point I/O)
#A Session has to be registered before any communication can be established
eeipclient.register_session('192.168.178.107')

#Parameters from Originator -> Target
eeipclient.o_t_instance_id = 0x64
eeipclient.o_t_length = 4
eeipclient.o_t_requested_packet_rate = 100000  #Packet rate 100ms (default 500ms)
eeipclient.o_t_realtime_format = RealTimeFormat.HEADER32BIT
eeipclient.o_t_owner_redundant = False
eeipclient.o_t_variable_length = False
eeipclient.o_t_connection_type = ConnectionType.POINT_TO_POINT

#Parameters from Target -> Originator
eeipclient.t_o_instance_id = 0x65
eeipclient.t_o_length = 16
eeipclient.t_o_requested_packet_rate = 100000  #Packet rate 100ms (default 500ms)
eeipclient.t_o_realtime_format = RealTimeFormat.MODELESS
eeipclient.t_o_owner_redundant = False
eeipclient.t_o_variable_length = False
eeipclient.t_o_connection_type = ConnectionType.MULTICAST

#Forward open initiates the Implicit Messaging
eeipclient.forward_open()
while 1:
    print('State of the first Input byte: {0}'.format(eeipclient.t_o_iodata[8]))
    print('State of the second Input byte: {0}'.format(eeipclient.t_o_iodata[9]))
    time.sleep(0.1)

#Close the Session (First stop implicit Messaging then unregister the session)
eeipclient.forward_close()
eeipclient.unregister_session()
```

<div id="librarydocumentation"/>

### 4. Library Documentation

<div id="methods"/>

#### 4.1 Methods

**Constructor def \_\_init__(self)**

Instantiation of the eeip class. The constructor doesn not need any parameters.

**def register_session(self, address, port = 0xAF12)**

Sends a RegisterSession command to target to initiate the session and to take the Session-ID for further use.
address: address IP-Address of the target device
port: Port of the target device (Default is 0xAF12)  
returns: Session Handle

**def unregister_session(self)**

Sends an UnRegisterSession command to a target to terminate the session

**def get_attributes_all(self, class_id, instance_id)**

Implementation of Common Service "Get_Attributes_All" - Service Code: 0x01  
Specification Vol. 1 Appendix A - Chapter A-4.1 - Page A-7
class_id: Class id of requested Attributes  
instance_id Instance of Requested Attributes (0 for class Attributes)  
returns: contents of the instance or class attributes defined in the object definition.

**def get_attribute_single(self, class_id, instance_id, attribute_id)**

Implementation of Common Service "Get_Attribute_Single" - Service Code: 0x0E  
Specification Vol. 1 Appendix A - Chapter A-4.12 - Page A-20
class_id: Class id of requested Attribute  
instance_id: Instance of Requested Attributes (0 for class Attributes)  
attribute_id Requested attribute  
returns: Requested Attribute value

**def set_attribute_single(self, class_id, instance_id, attribute_id, value)**

Implementation of Common Service "Set_Attribute_Single" - Service Code: 0x10  
Modifies an attribute value  
Specification Vol. 1 Appendix A - Chapter A-4.13 - Page A-21  
class_id: Class id of requested Attribute to write  
instance_id: Instance of Requested Attribute to write (0 for class Attributes)  
attribute_id: Attribute to write  
returns: value(s) to write in the requested attribute

**def forward_open(self, large_forward_open = False)**

The Forward Open Service (Service Code 0x54 and Large_Forward_Open service (Service  
Code 0x5B) are used to establish a Connection with a Target Device.  
The maximum data size for Forward open is 511 bytes, and 65535 for large forward open  
Two independent Threads are opened to send and receive data via UDP (Implicit Messaging)
large_forward_open: Use Service code 0x58 (Large_Forward_Open) if true, otherwise 0x54 (Forward_Open) 

**def forward_close(self)**

Closes a connection (Service code 0x4E)  

<div id="properties"/>

#### 4.2 Properties

**tcp_port**

TCP of the Remote Device (Default is 0xAF12)

**target_udp_port**

Only for Implicit Messaging  
UDP-Port of the IO-Adapter for explicit Messaging - Standard is 0x08AE

**originator_udp_port**

Only for Implicit Messaging  
UDP-Port of the Scanner for explicit Messaging - Standard is 0x08AE

**ip_address**

IP-Address of the Ethernet/IP Device

**o_t_requested_packet_rate**

Only for Implicit Messaging  
Requested Packet Rate (RPI) in ms Originator -> Target for implicit messaging (Default 0x7A120 -> 500ms)

**t_o_requested_packet_rate**

Only for Implicit Messaging  
Requested Packet Rate (RPI) in ms Target -> Originator for implicit messaging (Default 0x7A120 -> 500ms)

**o_t_owner_redundant**

Only for Implicit Messaging  
"1" Indicates that multiple connections are allowed Target -> Originator for Implicit-Messaging (Default: TRUE)
For forward open

**t_o_owner_redundant**

Only for Implicit Messaging  
"1" Indicates that multiple connections are allowed Originator -> Target for Implicit-Messaging (Default: TRUE)
For forward open

**o_t_variable_length**

Only for Implicit Messaging  
With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.  
With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
Originator -> Target for Implicit Messaging (Default: True (Variable length))
For forward open

**t_o_variable_length**

Only for Implicit Messaging  
With a fixed size connection, the amount of data shall be the size of specified in the "Connection Size" Parameter.  
With a variable size, the amount of data could be up to the size specified in the "Connection Size" Parameter
Target -> Originator for Implicit Messaging (Default: True (Variable length))
For forward open

**o_t_length**

Only for Implicit Messaging  
The maximum size in bytes (only pure data without sequence count and 32-Bit Real Time Header (if present)) from Target -> Originator for Implicit Messaging (Default: 505)
Forward open max 505

**t_o_length**

Only for Implicit Messaging  
The maximum size in bytes (only pure data without sequence count and 32-Bit Real Time Header (if present)) from Originator -> Target for Implicit Messaging (Default: 505)
Forward open max 505

**o_t_connection_type**

Only for Implicit Messaging  
Connection Type Originator -> Target for Implicit Messaging (Default: ConnectionType.MULTICAST)
Possible values: ConnectionType.NULL, ConnectionType.MULTICAST, ConnectionType.POINT_TO_POINT

**t_o_connection_type**

Only for Implicit Messaging  
Connection Type Target -> Originator for Implicit Messaging (Default: ConnectionType.MULTICAST)
Possible values: ConnectionType.NULL, ConnectionType.MULTICAST, ConnectionType.POINT_TO_POINT

**o_t_priority**

Only for Implicit Messaging  
Priority Originator -> Target for Implicit Messaging (Default: Priority.SCHEDULED)
Could be: Priority.SCHEDULED; Priority.HIGH; Priority.LOW; Priority.URGENT

**t_o_priority**

Only for Implicit Messaging  
Priority Target -> Originator for Implicit Messaging (Default: Priority.SCHEDULED)
Could be: Priority.SCHEDULED; Priority.HIGH; Priority.LOW; Priority.URGENT

**o_t_instance_id**

Only for Implicit Messaging  
Class Assembly (Consuming IO-Path - Outputs) Originator -> Target for Implicit Messaging (Default: 0x64)

**t_o_instance_id**

Only for Implicit Messaging  
Class Assembly (Consuming IO-Path - Outputs) Target -> Originator for Implicit Messaging (Default: 0x64)

**o_t_iodata**

Only for Implicit Messaging  
Provides Access to the Class 1 Real-Time IO-Data Originator -> Target for Implicit Messaging

**t_o_iodata**

Only for Implicit Messaging  
Provides Access to the Class 1 Real-Time IO-Data Target -> Originator for Implicit Messaging

**o_t_realtime_format**

Only for Implicit Messaging  
Used Real-Time Format Originator -> Target for Implicit Messaging (Default: RealTimeFormat.HEADER32BIT)
Possible Values: RealTimeFormat.HEADER32BIT; RealTimeFormat.HEARTBEAT; RealTimeFormat.ZEROLENGTH; RealTimeFormat.MODELESS

**t_o_realtime_format**

Only for Implicit Messaging  
Used Real-Time Format Target -> Originator for Implicit Messaging (Default: RealTimeFormat.HEADER32BIT)
Possible Values: RealTimeFormat.HEADER32BIT; RealTimeFormat.HEARTBEAT; RealTimeFormat.ZEROLENGTH; RealTimeFormat.MODELESS

**assembly_object_class**

Only for Implicit Messaging  
AssemblyObject for the Configuration Path in case of Implicit Messaging (Standard: 0x04)

**configuration_assembly_instance_id**

Only for Implicit Messaging  
ConfigurationAssemblyInstanceID is the InstanceID of the configuration Instance in the Assembly Object Class (Standard: 0x01)

**last_received_implicit_message**

Only for Implicit Messaging  
Date and time when the last Message has been received

