import pytest
from apps.discovery.models import RawOutput
from asgiref.sync import sync_to_async

from netdoc_sdk.client import NetDocClient

RAW_SHOW_VERSION = """
Cisco IOS Software, Catalyst 4500 L3 Switch Software (cat4500e-ENTSERVICESK9-M), Version 12.2(54)SG1, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2011 by Cisco Systems, Inc.
Compiled Thu 27-Jan-11 12:07 by prod_rel_team
Image text-base: 0x10000000, data-base: 0x12E16D24

ROM: 12.2(44r)SG9
Hobgoblin Revision 20, Fortooine Revision 1.22

router1 uptime is 2 years, 31 weeks, 6 days, 9 hours, 55 minutes
System returned to ROM by reload
System restarted at 09:09:22 UTC Tue Apr 9 2013
System image file is "bootflash:cat4500e-entservicesk9-mz.122-54.SG1.bin"


This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

cisco WS-C4948E (MPC8548) processor (revision 4) with 1048576K bytes of memory.
Processor board ID CAT1451S15C
MPC8548 CPU at 1GHz, Cisco Catalyst 4948E
Last reset from Reload
17 Virtual Ethernet interfaces
48 Gigabit Ethernet interfaces
4 Ten Gigabit Ethernet interfaces
511K bytes of non-volatile configuration memory.

Configuration register is 0x2102
"""
PARSED_SHOW_VERSION = [
    {
        'config_register': '0x2102',
        'hardware': ['WS-C4948E'],
        'hostname': 'router1',
        'mac_address': [],
        'release': 'fc1',
        'reload_reason': 'reload',
        'restarted': '09:09:22 UTC Tue Apr 9 2013',
        'rommon': '12.2(44r)SG9',
        'running_image': 'cat4500e-entservicesk9-mz.122-54.SG1.bin',
        'serial': ['CAT1451S15C'],
        'software_image': 'cat4500e-ENTSERVICESK9-M',
        'uptime': '2 years, 31 weeks, 6 days, 9 hours, 55 minutes',
        'uptime_days': '6',
        'uptime_hours': '9',
        'uptime_minutes': '55',
        'uptime_weeks': '31',
        'uptime_years': '2',
        'version': '12.2(54)SG1',
    }
]
RAW_SHOW_INTERFACES = """
GigabitEthernet0/0 is reset, line protocol is down (notconnect)
  Hardware is iGbE, address is fa16.3e57.336f (bia fa16.3e57.336f)
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Unknown, Unknown, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  Auto-duplex, Auto-speed, link type is auto, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 1d21h, output 1d21h, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     324 packets input, 48614 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     703 packets output, 62737 bytes, 0 underruns
     0 output errors, 0 collisions, 2 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
GigabitEthernet0/1 is up, line protocol is up (connected)
  Hardware is iGbE, address is fa16.3e4f.41cc (bia fa16.3e4f.41cc)
  Description: to iosvl2-2
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Auto Duplex, Auto Speed, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  Auto-duplex, Auto-speed, link type is auto, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 1d21h, output 00:00:02, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     83 packets input, 14855 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     15513 packets output, 2510810 bytes, 0 underruns
     0 output errors, 0 collisions, 3 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
GigabitEthernet0/2 is up, line protocol is up (connected)
  Hardware is iGbE, address is fa16.3ea3.3e49 (bia fa16.3ea3.3e49)
  Description: to iosvl2-4
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Unknown, Unknown, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  Auto-duplex, Auto-speed, link type is auto, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:13, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 1000 bits/sec, 2 packets/sec
     8677 packets input, 1698461 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     420798 packets output, 29058795 bytes, 0 underruns
     0 output errors, 0 collisions, 2 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
GigabitEthernet0/3 is up, line protocol is up (connected)
  Hardware is iGbE, address is fa16.3e31.2c47 (bia fa16.3e31.2c47)
  Description: to iosvl2-3
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Unknown, Unknown, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  Auto-duplex, Auto-speed, link type is auto, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:28, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 1000 bits/sec, 2 packets/sec
     8638 packets input, 1689698 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     420819 packets output, 29060539 bytes, 0 underruns
     0 output errors, 0 collisions, 2 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
GigabitEthernet1/0 is up, line protocol is up (connected)
  Hardware is iGbE, address is fa16.3ec8.50ab (bia fa16.3ec8.50ab)
  Description: to iosvl2-3
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Unknown, Unknown, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  Auto-duplex, Auto-speed, link type is auto, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:26, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 2000 bits/sec, 2 packets/sec
     8627 packets input, 1690235 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     420790 packets output, 29056035 bytes, 0 underruns
     0 output errors, 0 collisions, 2 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
Port-channel1 is down, line protocol is down (notconnect)
  Hardware is EtherChannel, address is fa16.3e4f.41cc (bia fa16.3e4f.41cc)
  MTU 1500 bytes, BW 100000 Kbit/sec, DLY 100 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Auto-duplex, Auto-speed, media type is unknown
  input flow-control is off, output flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 1d21h, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/2000/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     85 packets input, 7037 bytes, 0 no buffer
     Received 0 broadcasts (0 multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 input packets with dribble condition detected
     0 packets output, 0 bytes, 0 underruns
     0 output errors, 0 collisions, 0 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier
     0 output buffer failures, 0 output buffers swapped out
Loopback0 is up, line protocol is up
  Hardware is Loopback
  Description: Loopback
  MTU 1514 bytes, BW 8000000 Kbit/sec, DLY 5000 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation LOOPBACK, loopback not set
  Keepalive set (10 sec)
  Last input never, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/0 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
     0 packets output, 0 bytes, 0 underruns
     0 output errors, 0 collisions, 0 interface resets
     0 unknown protocol drops
     0 output buffer failures, 0 output buffers swapped out
Vlan1 is up, line protocol is up
  Hardware is Ethernet SVI, address is fa16.3e57.8001 (bia fa16.3e57.8001)
  Description: OOB Management
  Internet address is 10.255.0.16/16
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive not supported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input never, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     4 packets output, 240 bytes, 0 underruns
     0 output errors, 0 interface resets
     0 unknown protocol drops
     0 output buffer failures, 0 output buffers swapped out
GigabitEthernet0/2 is administratively down, line protocol is down
  Hardware is ASR1001, address is 78da.6eaf.3b82 (bia 78da.6eaf.3b82)
  Description: Port
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive not supported
  Full Duplex, 1000Mbps, link type is auto, media type is unknown media type
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input never, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/375/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     0 packets output, 0 bytes, 0 underruns
     0 output errors, 0 collisions, 1 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
"""
PARSED_SHOW_INTERFACES = [
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3e57.336f',
        'crc': '0',
        'delay': '10 usec',
        'description': '',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'iGbE',
        'input_errors': '0',
        'input_packets': '324',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet0/0',
        'ip_address': '',
        'last_input': '1d21h',
        'last_output': '1d21h',
        'last_output_hang': 'never',
        'link_status': 'reset',
        'mac_address': 'fa16.3e57.336f',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '703',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'down (notconnect)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3e4f.41cc',
        'crc': '0',
        'delay': '10 usec',
        'description': 'to iosvl2-2',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'iGbE',
        'input_errors': '0',
        'input_packets': '83',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet0/1',
        'ip_address': '',
        'last_input': '1d21h',
        'last_output': '00:00:02',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': 'fa16.3e4f.41cc',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '15513',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'up (connected)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3ea3.3e49',
        'crc': '0',
        'delay': '10 usec',
        'description': 'to iosvl2-4',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'iGbE',
        'input_errors': '0',
        'input_packets': '8677',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet0/2',
        'ip_address': '',
        'last_input': '00:00:13',
        'last_output': '00:00:00',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': 'fa16.3ea3.3e49',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '420798',
        'output_pps': '2',
        'output_rate': '1000',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'up (connected)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3e31.2c47',
        'crc': '0',
        'delay': '10 usec',
        'description': 'to iosvl2-3',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'iGbE',
        'input_errors': '0',
        'input_packets': '8638',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet0/3',
        'ip_address': '',
        'last_input': '00:00:28',
        'last_output': '00:00:00',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': 'fa16.3e31.2c47',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '420819',
        'output_pps': '2',
        'output_rate': '1000',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'up (connected)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3ec8.50ab',
        'crc': '0',
        'delay': '10 usec',
        'description': 'to iosvl2-3',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'iGbE',
        'input_errors': '0',
        'input_packets': '8627',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet1/0',
        'ip_address': '',
        'last_input': '00:00:26',
        'last_output': '00:00:00',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': 'fa16.3ec8.50ab',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '420790',
        'output_pps': '2',
        'output_rate': '2000',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'up (connected)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '100000 Kbit',
        'bia': 'fa16.3e4f.41cc',
        'crc': '0',
        'delay': '100 usec',
        'description': '',
        'duplex': 'Auto-duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'EtherChannel',
        'input_errors': '0',
        'input_packets': '85',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'Port-channel1',
        'ip_address': '',
        'last_input': '1d21h',
        'last_output': 'never',
        'last_output_hang': 'never',
        'link_status': 'down',
        'mac_address': 'fa16.3e4f.41cc',
        'media_type': 'unknown',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '0',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'down (notconnect)',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '2000',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': 'Auto-speed',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '0',
        'bandwidth': '8000000 Kbit',
        'bia': '',
        'crc': '0',
        'delay': '5000 usec',
        'description': 'Loopback',
        'duplex': '',
        'encapsulation': 'LOOPBACK',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'Loopback',
        'input_errors': '0',
        'input_packets': '0',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'Loopback0',
        'ip_address': '',
        'last_input': 'never',
        'last_output': 'never',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': '',
        'media_type': '',
        'mtu': '1514',
        'output_errors': '0',
        'output_packets': '0',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'up',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': '',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': 'fa16.3e57.8001',
        'crc': '0',
        'delay': '10 usec',
        'description': 'OOB Management',
        'duplex': '',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'Ethernet SVI',
        'input_errors': '0',
        'input_packets': '0',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'Vlan1',
        'ip_address': '10.255.0.16',
        'last_input': 'never',
        'last_output': 'never',
        'last_output_hang': 'never',
        'link_status': 'up',
        'mac_address': 'fa16.3e57.8001',
        'media_type': '',
        'mtu': '1500',
        'output_errors': '',
        'output_packets': '4',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '16',
        'protocol_status': 'up',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '75',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': '',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
    {
        'abort': '',
        'bandwidth': '1000000 Kbit',
        'bia': '78da.6eaf.3b82',
        'crc': '0',
        'delay': '10 usec',
        'description': 'Port',
        'duplex': 'Full Duplex',
        'encapsulation': 'ARPA',
        'frame': '0',
        'giants': '0',
        'hardware_type': 'ASR1001',
        'input_errors': '0',
        'input_packets': '0',
        'input_pps': '0',
        'input_rate': '0',
        'interface': 'GigabitEthernet0/2',
        'ip_address': '',
        'last_input': 'never',
        'last_output': 'never',
        'last_output_hang': 'never',
        'link_status': 'administratively down',
        'mac_address': '78da.6eaf.3b82',
        'media_type': 'unknown media type',
        'mtu': '1500',
        'output_errors': '0',
        'output_packets': '0',
        'output_pps': '0',
        'output_rate': '0',
        'overrun': '0',
        'prefix_length': '',
        'protocol_status': 'down',
        'queue_drops': '0',
        'queue_flushes': '0',
        'queue_max': '375',
        'queue_output_drops': '0',
        'queue_size': '0',
        'queue_strategy': 'fifo',
        'runts': '0',
        'speed': '1000Mbps',
        'vlan_id': '',
        'vlan_id_inner': '',
        'vlan_id_outer': '',
    },
]


@pytest.mark.django_db(databases=['default', 'logs'])
class TestScanWorkflow:
    async def test_workflow_existent(self, admin_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        await admin_client.users_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = await NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create canonical device
        credential = await admin_client.credentials_add(
            label='test', username='admin', password='cisco'
        )
        site = await admin_client.sites_add(name='test-site')
        canonical_device = await admin_client.canonical_devices_add(
            label='router1.example.com',
            discovery_mode='netmiko:cisco:ios:ssh',
            is_discoverable=True,
            identifiers={'hostname': 'router1'},
            site=site.id,
            credential=credential.id,
        )

        # Create collector (heartbeat)
        collector = await collector_client.collectors_heartbeat(
            name='collector@host.example.com',
            version='0.1.0',
        )

        # Activate collector
        await admin_client.collectors_update(
            collector.id,
            is_active=True,
            scan_networks=True,
            network_ranges=['10.0.1.0/24', '10.0.2.0/24'],
        )

        # Create run
        discoveries_run = await admin_client.discoveries_add()
        res = await admin_client.discoveries_list()
        assert res.count == 1
        await admin_client.discoveries_get(id=discoveries_run.id)

        # Verify jobs
        await admin_client.discoveries_jobs_list(id=discoveries_run.id)

        # Claim job
        res = await collector_client.discovery_jobs_claim()
        claim_token = res.claim_token
        idempotency_key = res.idempotency_key
        job_id = res.id

        # Verify inventory
        inventory = res.inventory
        assert len(inventory['all']['hosts']) == 1

        # Push discovered devices
        discovery_payload = {
            'canonical_device': canonical_device.id,
            'raw_payload': {
                'raw_outputs': {
                    'show version': RAW_SHOW_VERSION,
                    'show interfaces': RAW_SHOW_INTERFACES,
                },
                'parsed_outputs': {
                    'show version': PARSED_SHOW_VERSION,
                    'show interfaces': PARSED_SHOW_INTERFACES,
                },
            },
            'idempotency_key': idempotency_key,
        }
        scan_payload = {
            'raw_payload': {
                'raw_outputs': {
                    'show version': RAW_SHOW_VERSION,
                    'show interfaces': RAW_SHOW_INTERFACES,
                },
                'parsed_outputs': {
                    'show version': PARSED_SHOW_VERSION,
                    'show interfaces': PARSED_SHOW_INTERFACES,
                },
            },
            'idempotency_key': idempotency_key,
            'discovery_mode': 'netmiko:cisco:ios:ssh',
            'discovery_address': '10.0.3.254',
            'credential': str(credential.id),
        }
        await collector_client.discovery_jobs_push_discovered_device(
            id=job_id, claim_token=claim_token, **discovery_payload
        )
        await collector_client.discovery_jobs_push_discovered_device(
            id=job_id, claim_token=claim_token, **scan_payload
        )

        # Complete job
        payload = {
            'status': 'completed',
        }
        await collector_client.discovery_jobs_complete(id=job_id, claim_token=claim_token, **payload)

        # Verify run
        run = await admin_client.discoveries_get(id=discoveries_run.id)
        assert run.status.value == 'completed'

        # Verify jobs
        jobs = await admin_client.discoveries_jobs_list(id=discoveries_run.id)
        assert jobs.count == 1
        assert jobs.results[0].status.value == 'completed'

        # Verify raw logs
        raw_outputs = await sync_to_async(list)(RawOutput.objects.unfiltered().all())
        assert len(raw_outputs) == 2

        discovery_raw_output = raw_outputs[0]
        raw_payload = discovery_raw_output.raw_payload
        assert raw_payload is not None
        assert discovery_raw_output.status == 'parsed'
        # Check canonical device
        assert discovery_raw_output.canonical_device_id is not None
        # Check raw output
        assert 'raw_outputs' in raw_payload
        assert 'show version' in raw_payload['raw_outputs']
        assert len(raw_payload['raw_outputs']['show version']) > 10
        # Check parsed output
        assert 'parsed_outputs' in raw_payload
        assert 'show version' in raw_payload['parsed_outputs']

        scan_raw_output = raw_outputs[1]
        raw_payload = scan_raw_output.raw_payload
        assert raw_payload is not None
        assert scan_raw_output.status == 'duplicated'
        # Check canonical device
        assert scan_raw_output.canonical_device_id is None

        # Verify devices
        devices = await admin_client.devices_list()
        assert devices.count == 1

        # Verify canonical devices
        canonical_devices = await admin_client.canonical_devices_list()
        assert canonical_devices.count == 1
        canonical_device = canonical_devices.results[0]
        assert '10.0.3.254' in canonical_device.secondary_ip_addresses

    async def test_workflow_new(self, admin_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        admin_client.users_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create credential
        credential = await admin_client.credentials_add(
            label='test', username='admin', password='cisco'
        )
        admin_client.sites_add(name='test-site')

        # Create collector (heartbeat)
        collector = await collector_client.collectors_heartbeat(
            name='collector@host.example.com',
            version='0.1.0',
        )

        # Activate collector
        await admin_client.collectors_update(
            collector.id,
            is_active=True,
            scan_networks=True,
            network_ranges=['10.0.1.0/24', '10.0.2.0/24'],
        )

        # Create run
        discoveries_run = await admin_client.discoveries_add()
        res = await admin_client.discoveries_list()
        assert res.count == 1
        await admin_client.discoveries_get(id=discoveries_run.id)

        # Verify jobs
        await admin_client.discoveries_jobs_list(id=discoveries_run.id)

        # Claim job
        res = await collector_client.discovery_jobs_claim()
        claim_token = res.claim_token
        idempotency_key = res.idempotency_key
        job_id = res.id

        # Push discovered devices
        payload = {
            'raw_payload': {
                'raw_outputs': {
                    'show version': RAW_SHOW_VERSION,
                    'show interfaces': RAW_SHOW_INTERFACES,
                },
                'parsed_outputs': {
                    'show version': PARSED_SHOW_VERSION,
                    'show interfaces': PARSED_SHOW_INTERFACES,
                },
            },
            'idempotency_key': idempotency_key,
            'discovery_mode': 'netmiko:cisco:ios:ssh',
            'discovery_address': '10.0.3.254',
            'credential': str(credential.id),
        }
        collector_client.discovery_jobs_push_discovered_device(
            id=job_id, claim_token=claim_token, **payload
        )

        # Complete job
        payload = {
            'status': 'completed',
        }
        collector_client.discovery_jobs_complete(id=job_id, claim_token=claim_token, **payload)

        # Verify run
        run = await admin_client.discoveries_get(id=discoveries_run.id)
        assert run.status.value == 'completed'

        # Verify jobs
        jobs = await admin_client.discoveries_jobs_list(id=discoveries_run.id)
        assert jobs.count == 1
        assert jobs.results[0].status.value == 'completed'

        # Verify raw logs
        raw_outputs = RawOutput.objects.unfiltered().all()
        raw_output = raw_outputs.first()
        raw_payload = raw_output.raw_payload
        assert raw_payload is not None
        assert raw_output.status == 'parsed'
        # Check canonical device
        assert raw_output.canonical_device is None
        # Check raw output
        assert 'raw_outputs' in raw_payload
        assert 'show version' in raw_payload['raw_outputs']
        assert len(raw_payload['raw_outputs']['show version']) > 10
        # Check parsed output
        assert 'parsed_outputs' in raw_payload
        assert 'show version' in raw_payload['parsed_outputs']

        # Verify devices
        devices = await admin_client.devices_list()
        assert devices.count == 1

        # Verify canonical devices
        canonical_devices = await admin_client.canonical_devices_list()
        assert canonical_devices.count == 1
        canonical_device = canonical_devices.results[0]
        assert '10.0.3.254' in canonical_device.mgmt_address
