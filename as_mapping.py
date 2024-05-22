import pybgpstream
import networkx as nx
from collections import defaultdict
from itertools import groupby
import datetime
import json
import sys
from aslookup import get_as_data

def unix_to_regular(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

def get_delay_info(timestamp, source, destination):
    with open('as_country_mapping.json') as f:
        as_country_mapping = json.load(f)

    as_graph = nx.Graph()

    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn
    source_country = get_as_data(str(source)).cc
    destination_country = get_as_data(str(destination)).cc

    bgp_lens = defaultdict(lambda: defaultdict(lambda: None))

    from_time_ = unix_to_regular(timestamp - 3600)
    until_time_ = unix_to_regular(timestamp + 3600)

    source_country_asns = [asn for asn, country in as_country_mapping.items() if country == source_country]
    destination_country_asns = [asn for asn, country in as_country_mapping.items() if country == destination_country]

    print("Source ASNs:", source_country_asns)
    print("Destination ASNs:", destination_country_asns)

    stream = pybgpstream.BGPStream(
        from_time=from_time_,
        until_time=until_time_,
        collectors=[
            "route-views.routeviews.org",
            "route-views2.routeviews.org",
            "route-views.linx",
            "route-views.isc",
            "rrc00.ripe.net",
            "rrc01.ripe.net",
            "rrc07.ripe.net",
            "route-views.oregon-ix.net",
            "route-views.eqix",
            "route-views.saopaulo",
            "route-views.nap.africa-ix.net",
            "route-views.tokyo",
            "route-views.hkix.net",
            "route-views.sg",
            "route-views.apnic.net",
            "route-views.nordu.net",
            "route-server.bcix.de",
            "route-server.cernet.net",
            "route-server.sgix.sg",
            "route-views.pie.net.au"
        ],
        record_type="ribs",
    )

    delays = []

    for rec in stream.records():
        for elem in rec:
            peer = str(elem.peer_asn)
            hops = [k for k, g in groupby(elem.fields['as-path'].split(" "))]
            if len(hops) > 1 and hops[0] == peer:
                origin = hops[-1]
                for i in range(0, len(hops) - 1):
                    as_graph.add_edge(hops[i], hops[i + 1])
                bgp_lens[peer][origin] = min(list(filter(bool, [bgp_lens[peer][origin], len(hops)])))

    for peer in bgp_lens:
        for origin in bgp_lens[peer]:
            try:
                nxlen = len(nx.shortest_path(as_graph, peer, origin))
                if origin in destination_country_asns and peer in source_country_asns:
                    print(peer, origin, bgp_lens[peer][origin], nxlen)
                    delays.append((peer, origin, bgp_lens[peer][origin], nxlen))
            except nx.NetworkXNoPath:
                print(f"No path found between {peer} and {origin} in the graph")

    return delays

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <timestamp> <source> <destination>")
        return

    timestamp = int(sys.argv[1])
    source = sys.argv[2]
    destination = sys.argv[3]

    delays = get_delay_info(timestamp, source, destination)

    with open('delays.json', 'w') as f:
        json.dump(delays, f)

if __name__ == "__main__":
    main()
