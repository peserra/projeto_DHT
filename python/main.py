import dht


def main():
    with open("../lista_hosts_dht.txt", 'r+') as known_hosts:
        hosts = known_hosts.readlines()
    
    dht_instance = dht.Dht()

    for host in hosts:
        host = str(host).replace('\n', '')
        host_ip, host_port = host.split(':')
        new_node = dht.CreateDhtNode(host_ip, int(host_port))
        dht_instance.join(node = new_node)
    
    for node in dht_instance.known_hosts:
        print(f"Node id:{node.id} | Node prev: {node.id_prev} | Node next: {node.id_next} | Node hash: {node.id_hash}")

    #print(len(dht_instance.known_hosts))
    # host = hosts[0]
    # split_host = str.split(host, ":")
    # ip_addr , port = split_host

    # dht_node = dht.CreateDhtNode(ip_addr, int(port))
    # print(dht.nodes_participating)
    # dht_node.join(hosts)
    # print(dht_node.id)
    # host = hosts[1]
    # split_host = str.split(host, ":")
    # ip_addr , port = split_host
    # dht_node2 = dht.CreateDhtNode(ip_addr, int(port))
    # print(dht.nodes_participating)
    # dht_node2.join(hosts)
    # print(dht_node2.id)
    # print(dht.nodes_participating)
    # print("finalizou sem problema")


if __name__ == "__main__":
    main()