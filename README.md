## EEIP.py - THE Ethernet/IP compatible Python Module

- Support of Explicit and Implicit Messaging
- Supports IO Scanner and Explicit Message Client functionality

- Object Library with CIP-Definined Objects
- Provides a simple way to access Ethernet/IP Devices without special knowledge about Ethernet/IP. Only few lines of code are required

Visit www.eeip-library.de for more informations and Codesamples

### Table of Contents
1. [Installation](#installation)

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



