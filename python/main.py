import DHT_lib as DHT
import asyncio


async def main():
    
    dht_instance = DHT.DhtManager()
    
    node_init = DHT.CreateDhtNode(ip_addr="127.0.0.1", port=1234)
    print("criado node de inicio da dht")

    t1 = asyncio.create_task(dht_instance.join(node=node_init))

    await t1

    node2 = DHT.CreateDhtNode(ip_addr="127.0.0.1", port=1235)
    t2 = asyncio.create_task(dht_instance.join(node=node2))
    await t2
    print("apos o join")

    

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
    asyncio.run(main())