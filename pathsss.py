import pybgpstream
from aslookup import get_as_data
from ipaddress import IPv4Network
import datetime
import whois
from bs4 import BeautifulSoup
import requests

def get_country_from_bgpview(asn):
    url = f"https://bgpview.io/asn/{asn}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tag = soup.find('img', {'title': True, 'alt': True})
        if img_tag:
            country_code = img_tag['alt'].split('(')[-1].split(')')[0].strip()
            return country_code
    return None
           
def unix_to_regular(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")
            
def exact_match_announcements(timestamp, source, destination):
    def path(timestamp, source, destination):
        source_AS = get_as_data(str(source)).asn
        dest_AS = get_as_data(str(destination)).asn
        dest_country = str(get_as_data(str(destination)).cc)
        source_country = str(get_as_data(str(source)).cc)
        print("source as", source_AS)
        print("dest as", dest_AS)
        print("source country",get_as_data(str(source)).cc)
        print("destination country", get_as_data(str(destination)).cc)
    
        from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
        until_time_ = unix_to_regular(timestamp + 1800)

        matches = []  # Initialize an empty list to store matches
        iteration_count = 0  # Counter for iterations

        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_.*_{dest_AS}$ and elemtype announcements"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
    
    L1 = path(timestamp - 10800, source, destination)
    L2 = path(timestamp + 10800, source, destination)
    
    return L1, L2
    
def exact_match_withdrawals(timestamp, source, destination):
    def path(timestamp, source, destination):
        source_AS = get_as_data(str(source)).asn
        dest_AS = get_as_data(str(destination)).asn
        dest_country = str(get_as_data(str(destination)).cc)
        source_country = str(get_as_data(str(source)).cc)
        print("source as", source_AS)
        print("dest as", dest_AS)
        print("source country",get_as_data(str(source)).cc)
        print("destination country", get_as_data(str(destination)).cc)
    
        from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
        until_time_ = unix_to_regular(timestamp + 1800)

        matches = []  # Initialize an empty list to store matches
        iteration_count = 0  # Counter for iterations

        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_.*_{dest_AS}$ and elemtype withdrawals"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
    
    L1 = path(timestamp - 10800, source, destination)
    L2 = path(timestamp + 10800, source, destination)
    
    return L1, L2
    
def partial_match_announcements(timestamp, source, destination):
    from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
    until_time_ = unix_to_regular(timestamp + 1800)
    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn
    dest_country = str(get_as_data(str(destination)).cc)
    source_country = str(get_as_data(str(source)).cc)
    print("source as", source_AS)
    print("dest as", dest_AS)
    print("source country",get_as_data(str(source)).cc)
    print("destination country", get_as_data(str(destination)).cc)
    def find_dest():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        if str(destination_c) == str(dest_country):
                            return destination
                        
                        
        
        return None
    
    dest_in_country = find_dest()
    def find_match(time):
        matches = []  
        from_time = unix_to_regular(time - 1800) #at least one hour
        until_time = unix_to_regular(time + 1800)
        stream = pybgpstream.BGPStream(
            from_time=from_time,
            until_time=until_time,
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
            record_type="updates",
            filter = f"path ^{source_AS}_.*_{dest_in_country}$ and elemtype announcements"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
        
    L1 = find_match(timestamp - 10800)
    L2 = find_match(timestamp + 10800)
    
    return L1, L2
    
def partial_match_withdrawals(timestamp, source, destination):
    from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
    until_time_ = unix_to_regular(timestamp + 1800)
    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn
    dest_country = str(get_as_data(str(destination)).cc)
    source_country = str(get_as_data(str(source)).cc)
    print("source as", source_AS)
    print("dest as", dest_AS)
    print("source country",get_as_data(str(source)).cc)
    print("destination country", get_as_data(str(destination)).cc)
    def find_dest():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        if str(destination_c) == str(dest_country):
                            return destination
                        
                        
        
        return None
    
    dest_in_country = find_dest()
    def find_match(time):
        matches = []  
        from_time = unix_to_regular(time - 1800) #at least one hour
        until_time = unix_to_regular(time + 1800)
        stream = pybgpstream.BGPStream(
            from_time=from_time,
            until_time=until_time,
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
            record_type="updates",
            filter = f"path ^{source_AS}_.*_{dest_in_country}$ and elemtype withdrawals"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
        
    L1 = find_match(timestamp - 10800)
    L2 = find_match(timestamp + 10800)
    
    return L1, L2

def random_match_announcements(timestamp, source, destination):
    from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
    until_time_ = unix_to_regular(timestamp + 1800)
    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn
    dest_country = str(get_as_data(str(destination)).cc)
    source_country = str(get_as_data(str(source)).cc)
    print("source as", source_AS)
    print("dest as", dest_AS)
    print("source country",get_as_data(str(source)).cc)
    print("destination country", get_as_data(str(destination)).cc)
    from_time_ = unix_to_regular(timestamp - 100) #at least one hour
    until_time_ = unix_to_regular(timestamp + 100)
    def find_source():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            #filter = f"path ^{source_AS}_"
        )
        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        as_array = as_path.split()
                        for asn in as_array:
                            if str(get_country_from_bgpview(asn)) == str(source_country):
                                return asn
        return None
    
    random_source = find_source()
    
    def find_dest():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        if str(destination_c) == str(dest_country):
                            return destination
                        
                        
        
        return None
        
    random_dest = find_dest()
    def find_match(time):
        matches = []  
        from_time = unix_to_regular(time - 1800) #at least one hour
        until_time = unix_to_regular(time + 1800)
        stream = pybgpstream.BGPStream(
            from_time=from_time,
            until_time=until_time,
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
            record_type="updates",
            filter = f"path ^{random_source}_.*_{random_dest} and elemtype announcements"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
        
    L1 = find_match(timestamp - 10800)
    L2 = find_match(timestamp + 10800)
    
    return L1, L2
    
def random_match_withdrawals(timestamp, source, destination):
    from_time_ = unix_to_regular(timestamp - 1800) #at least one hour
    until_time_ = unix_to_regular(timestamp + 1800)
    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn
    dest_country = str(get_as_data(str(destination)).cc)
    source_country = str(get_as_data(str(source)).cc)
    print("source as", source_AS)
    print("dest as", dest_AS)
    print("source country",get_as_data(str(source)).cc)
    print("destination country", get_as_data(str(destination)).cc)
    def find_source():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            #filter = f"path ^{source_AS}_"
        )
        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        as_array = as_path.split()
                        for asn in as_array:
                            if str(get_country_from_bgpview(asn)) == str(source_country):
                                return asn
        return None
    
    random_source = find_source()
    
    def find_dest():
        matches = []  # Initialize an empty list to store matches
        
        # Create and configure the stream
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
            record_type="updates",
            filter = f"path ^{source_AS}_"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        ip_address = IPv4Network(prefix).network_address
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        if str(destination_c) == str(dest_country):
                            return destination
                        
                        
        
        return None
        
    random_dest = find_dest()
    def find_match(time):
        matches = []  
        from_time = unix_to_regular(time - 1800) #at least one hour
        until_time = unix_to_regular(time + 1800)
        stream = pybgpstream.BGPStream(
            from_time=from_time,
            until_time=until_time,
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
            record_type="updates",
            filter = f"path ^{random_source}_.*_{random_dest} and elemtype withdrawals"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append(as_path.split())
                        
        matches = list(set(map(tuple, matches)))
        return matches
        
    L1 = find_match(timestamp - 10800)
    L2 = find_match(timestamp + 10800)
    
    return L1, L2
    
timestamp = 1708650000
source = '128.199.105.50'
destination = '185.25.205.152'

#L1, L2 = random_match_announcements(timestamp, source, destination)
#L1, L2 = random_match_withdrawals(timestamp, source, destination)
L1, L2 = partial_match_announcements(timestamp, source, destination)
#L1, L2 = partial_match_withdrawals(timestamp, source, destination)
#L1, L2 = exact_match_announcements(timestamp, source, destination)
#L1, L2 = exact_match_withdrawals(timestamp, source, destination)
print("L1:", L1)
print("L2:", L2)
