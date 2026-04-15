# LINE 1-7: IMPORT LIBRARIES
from ryu.base import app_manager          # Base class for Ryu apps
from ryu.controller import ofp_event      # OpenFlow events (packet_in, etc.)
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER  # Switch states
from ryu.controller.handler import set_ev_cls  # Decorator to handle events
from ryu.ofproto import ofproto_v1_3      # OpenFlow 1.3 protocol
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, arp  # Packet parsers


# LINE 9-11: CLASS DEFINITION
class PacketLogger(app_manager.RyuApp):   # Create SDN application
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]  # Use OpenFlow version 1.3


# LINE 13-17: CONSTRUCTOR - RUNS WHEN APP STARTS
    def __init__(self, *args, **kwargs):
        super(PacketLogger, self).__init__(*args, **kwargs)  # Initialize parent class
        self.log_file = open("packet_logs.txt", "w")  # Open file to save logs
        self.blocked_ip = "10.0.0.1"  # FIREWALL: Block all traffic from h1


# LINE 19-27: WHEN SWITCH CONNECTS TO CONTROLLER
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath          # Get the switch
        parser = datapath.ofproto_parser    # Get message parser
        ofproto = datapath.ofproto          # Get OpenFlow constants
        
        match = parser.OFPMatch()           # Match ALL packets
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]  # Send to controller
        self.add_flow(datapath, 0, match, actions)  # Install this rule on switch


# LINE 29-37: HELPER FUNCTION TO INSTALL FLOW RULES ON SWITCH
    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        # Create instruction: "apply these actions"
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        # Create FlowMod message (adds/updates flow table)
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, 
                                match=match, instructions=inst)
        datapath.send_msg(mod)  # Send to switch


# LINE 39-40: THIS FUNCTION RUNS FOR EVERY PACKET
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg                       # Get packet_in message
        datapath = msg.datapath            # Get switch that sent packet
        parser = datapath.ofproto_parser   # Get parser
        in_port = msg.match['in_port']     # Which port packet came from
        pkt = packet.Packet(msg.data)      # Parse the raw packet
        
        self.logger.info("=== PACKET RECEIVED ===")  # Print separator


# LINE 48-51: EXTRACT AND LOG ETHERNET (MAC ADDRESSES)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth:
            self.logger.info(f"Ethernet: {eth.src} -> {eth.dst}")


# LINE 53-59: HANDLE ARP PACKETS (FIND MAC ADDRESSES)
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self.logger.info(f"ARP: {arp_pkt.src_ip} -> {arp_pkt.dst_ip}")
            # FIREWALL: Block ARP from h1
            if arp_pkt.src_ip == self.blocked_ip:
                self.logger.info(f"BLOCKED ARP: {arp_pkt.src_ip}")
                return  # Drop the packet


# LINE 61-78: HANDLE IP PACKETS
        ip = pkt.get_protocol(ipv4.ipv4)
        if ip:
            self.logger.info(f"IP: {ip.src} -> {ip.dst}")
            
            # FIREWALL: Block IP packets from h1
            if ip.src == self.blocked_ip:
                self.logger.info(f"BLOCKED IP: {ip.src} -> {ip.dst}")
                return  # Drop the packet
            
            # Check for TCP or UDP to show port numbers
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            udp_pkt = pkt.get_protocol(udp.udp)
            
            if tcp_pkt:
                self.logger.info(f"TCP port: {tcp_pkt.src_port} -> {tcp_pkt.dst_port}")
            elif udp_pkt:
                self.logger.info(f"UDP port: {udp_pkt.src_port} -> {udp_pkt.dst_port}")
            
            # Save to log file
            log_msg = f"IP: {ip.src} -> {ip.dst}"
            self.log_file.write(log_msg + "\n")
            self.log_file.flush()  # Save immediately


# LINE 80-86: FORWARD THE PACKET (FLOOD TO ALL PORTS)
        actions = [parser.OFPActionOutput(datapath.ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)  # Send packet out
