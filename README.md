# SDN Packet Logger with Firewall

## Project Overview

This project implements a Software-Defined Networking based Packet Logger using the Ryu controller and Mininet. The controller captures, logs, and analyzes all network packets in real-time. Additionally, it includes a firewall feature that blocks traffic from a specific IP address (10.0.0.1), demonstrating SDN's programmability and centralized control.

## Problem Statement

In traditional networks, monitoring and filtering traffic requires configuring each switch individually, which is time-consuming and error-prone. This project demonstrates how SDN simplifies network management by providing centralized packet logging, programmable firewall capabilities, flow rule installation for performance improvement, and protocol analysis for ARP, IP, TCP, UDP, and ICMP traffic.

## Network Topology

The topology consists of one Open vSwitch (s1) running OpenFlow 1.3 and three hosts (h1, h2, h3) with IP addresses 10.0.0.1, 10.0.0.2, and 10.0.0.3 respectively. The Ryu controller connects to the switch via OpenFlow protocol on port 6653. The firewall rule blocks all traffic originating from h1 (10.0.0.1).

## Features Implemented

The project implements packet logging that captures all packets with timestamps and saves them to a file. MAC learning allows the switch to learn and forward based on MAC addresses. The firewall blocks both ARP and IP traffic from 10.0.0.1. Flow installation creates flow rules after the first packet for performance improvement. Protocol detection identifies ARP, IP, TCP, UDP, and ICMP traffic. Port logging captures TCP and UDP source and destination ports. All logs are saved to packet_logs.txt file.

## Prerequisites

You need to install Mininet and Ryu controller. Install Mininet using the command sudo apt-get install mininet. Install Ryu using pip install ryu. Verify installations with ryu-manager --version and sudo mn --version.

## Setup and Execution Steps

First, clone the repository using git clone https://github.com/yourusername/sdn-packet-logger.git and navigate into the directory.

In Terminal 1, start the Ryu controller with the command ryu-manager packet_logger.py. You should see output indicating the app is loading and instantiating.

In Terminal 2, start the Mininet topology with the command sudo mn --topo single,3 --controller remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13. This creates three hosts connected to one switch and connects to the Ryu controller.

## Test Scenarios

For Scenario 1 which tests the firewall on blocked traffic, run h1 ping h2 in the Mininet console. The expected result is Destination Host Unreachable because the firewall blocks traffic from h1.

For Scenario 2 which tests allowed traffic, run h2 ping h3. The expected result is successful ping replies with 64 bytes from 10.0.0.3.

For Scenario 3 which tests overall connectivity, run pingall. The expected result shows 66 percent dropped packets because h1 cannot reach h2 or h3 while h2 and h3 can communicate with each other.

For Scenario 4 which tests performance using iperf, first start the iperf server on h3 with the command h3 iperf -s and. Then run the client on h2 with h2 iperf -c 10.0.0.3 -t 5. The expected throughput is around 6.5 Gbits per second.

For Scenario 5 which views the flow table, run sh ovs-ofctl dump-flows s1. This shows the flow rules installed by the controller.

To view the packet logs, run cat packet_logs.txt. To exit Mininet, type exit.

## Expected Output

On the Ryu controller terminal, you will see output similar to this. When h1 tries to send ARP, you see Ethernet MAC addresses followed by ARP request from 10.0.0.1 to 10.0.0.2 and then BLOCKED ARP message. When h2 pings h3, you see Ethernet addresses, IP addresses, and ICMP ping indication for both request and reply.

On the Mininet terminal, when you run pingall, you see h1 shows X X indicating no connectivity, h2 shows X h3 meaning it can reach h3 but not h1, and h3 shows X h2 meaning it can reach h2 but not h1. The results show 66 percent dropped with 2 out of 6 received.

When you run h2 ping h3, you see successful replies with time around 1.2 milliseconds for the first ping and around 0.09 milliseconds for subsequent pings.

When you run iperf, you see throughput of approximately 3.77 GBytes transferred at 6.46 Gbits per second.

When you dump the flow table, you see flow rules for traffic between h2 and h3 with actions to output to specific ports, and the default rule to send all packets to the controller.

## Performance Analysis

The first ping takes approximately 1.2 milliseconds because the packet goes to the controller for logging and flow installation. Subsequent pings take only about 0.09 milliseconds because the switch handles them directly using the installed flow rule. This represents a 93 percent performance improvement. The first packet is processed in software by the controller, while later packets are processed in hardware by the switch.

## Code Explanation

The code begins by importing necessary libraries including app_manager for the Ryu application base class, ofp_event for OpenFlow events, ofproto_v1_3 for OpenFlow 1.3 protocol, and packet libraries for parsing Ethernet, IP, TCP, UDP, and ARP headers.

The PacketLogger class inherits from app_manager.RyuApp and specifies OpenFlow version 1.3. In the constructor, it opens the log file packet_logs.txt for writing and sets the blocked IP address to 10.0.0.1.

The switch_features_handler function runs when a switch connects to the controller. It installs a default table-miss rule that matches all packets and sends them to the controller using OFPP_CONTROLLER action.

The add_flow function is a helper that creates and sends FlowMod messages to install flow rules on the switch. It takes datapath, priority, match conditions, and actions as parameters.

The packet_in_handler function runs for every packet received from the switch. It extracts the packet, logs a separator line, and then processes Ethernet, ARP, and IP headers sequentially.

For ARP packets, it logs the source and destination IP addresses. If the source IP matches the blocked IP, it logs BLOCKED ARP and returns, dropping the packet.

For IP packets, it logs the source and destination IP addresses. If the source IP matches the blocked IP, it logs BLOCKED IP and returns. For TCP and UDP packets, it also logs the source and destination port numbers. It then writes the IP information to the log file.

Finally, it creates a PacketOut message with the OFPP_FLOOD action to send the packet out all ports and sends it to the switch.

## Validation and Testing

Validation was performed using multiple tools. Wireshark was used for packet capture analysis. iperf was used for throughput measurement. ovs-ofctl was used for flow table inspection. ping was used for latency testing.

All test cases passed successfully. The firewall successfully blocks traffic from 10.0.0.1 as shown by Destination Host Unreachable messages. Hosts h2 and h3 communicate successfully with ping replies. Flow rules are installed correctly as shown by ovs-ofctl dump-flows. Performance improves dramatically after the first packet. iperf shows high throughput of 6.46 Gbits per second.

