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
3. [Library Documentation](#librarydocumentation)   
    3.1.	[Methods](#methods)  

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

<div id="librarydocumentation"/>

### 3. Library Documentation

<div id="methods"/>

#### 3.1 Methods

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
