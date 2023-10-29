import netifaces
import socket
import struct

def get_local_ip():
    try:
        # Cria um socket UDP para obter o endereço IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return None

def get_dhcp_range(local_ip):
    # Obtém o prefixo da rede (exemplo: '192.168.1.')
    network_prefix = '.'.join(local_ip.split('.')[:-1]) + '.'

    # Infere o intervalo de IP do DHCP
    start_ip = network_prefix + '100'
    end_ip = network_prefix + '200'

    return f"{start_ip}-{end_ip}"

def get_assigned_ips(interface):
    assigned_ips = set()
    pcap_filter = b'udp and (port 67 or port 68)'

    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    conn.bind((interface, 0))
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**30)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.setsockopt(socket.SOL_SOCKET, 25, b'dhcp discover')

    while True:
        packet, _ = conn.recvfrom(65536)
        eth_length = 14
        ip_header = packet[eth_length:eth_length+20]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4

        src_ip = socket.inet_ntoa(iph[8])

        if src_ip != '0.0.0.0':
            assigned_ips.add(src_ip)

    return assigned_ips

def calculate_total_ips(start_ip, end_ip):
    start_ip_int = int(start_ip.split('.')[-1])
    end_ip_int = int(end_ip.split('.')[-1])
    total_ips = end_ip_int - start_ip_int + 1
    return total_ips

def check_dhcp_full(interface, dhcp_range):
    assigned_ips = get_assigned_ips(interface)
    num_assigned_ips = len(assigned_ips)

    start_ip, end_ip = dhcp_range.split('-')
    total_ips = calculate_total_ips(start_ip, end_ip)

    print(f"Total de endereços atribuídos: {num_assigned_ips}")
    print(f"Total de endereços disponíveis: {total_ips - num_assigned_ips}")

    if num_assigned_ips == total_ips:
        print("O DHCP está cheio.")
    else:
        print("O DHCP não está cheio.")

if __name__ == "__main__":
    # Obtém a interface de rede com IP local
    interfaces = netifaces.interfaces()
    local_ip = get_local_ip()

    # Verifica se o IP local é atribuído a uma das interfaces
    interface_name = None
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for address in addresses[netifaces.AF_INET]:
                if 'addr' in address and address['addr'] == local_ip:
                    interface_name = interface
                    break
        if interface_name:
            break

    if interface_name:
        print(f"Interface de rede selecionada: {interface_name}")
        dhcp_range = get_dhcp_range(local_ip)
        print(f"Intervalo de IP do DHCP: {dhcp_range}")
        check_dhcp_full(interface_name, dhcp_range)
    else:
        print("Não foi possível obter a interface de rede e o intervalo do DHCP automaticamente.")
