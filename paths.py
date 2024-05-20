import pybgpstream
from aslookup import get_as_data
from ipaddress import IPv4Network
import datetime
import whois
from bs4 import BeautifulSoup
import requests
from collections import defaultdict

def get_as_number_from_prefix(prefix):
    url = f"https://bgpview.io/prefix/{prefix}"
    
    try:
        # Fetch the HTML content of the page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the AS number associated with the prefix
        table = soup.find("table", class_="table table-hover")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    as_number_element = cells[1].find("a")
                    if as_number_element:
                        as_number = as_number_element.text.strip()[2:]  # Remove the "AS" prefix
                        return as_number
            print(f"No AS number found for prefix: {prefix}")
            return None
        else:
            print("No prefix information found on the page.")
            return None
    
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
        
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

def get_prefix_from_ip(ip_address):
    url = f"https://bgp.he.net/ip/{ip_address}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        td_elements = soup.find_all('td', class_='nowrap')
        for td in td_elements:
            a_element = td.find('a')
            if a_element:
                prefix = a_element.text.strip()
                return prefix
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
                timestamp = elem.time
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append([as_path.split(), timestamp])
                        
        #matches = list(set(map(tuple, matches)))
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
                timestamp = elem.time
                if 'as-path' in elem.fields:
                    # Access the AS path from the element
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append([as_path.split(), timestamp])
                        
        #matches = list(set(map(tuple, matches)))
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


def match_withdrawals_destination(timestamp, source, destination):
    real_withdrawal = []
    flap = []
    withdrawal_dict = defaultdict(lambda: {"timestamps": [], "intervals": defaultdict(int), "total": 0})  

    def path(timestamp, source, destination):
        source_AS = get_as_data(str(source)).asn
        dest_AS = get_as_data(str(destination)).asn
        dest_country = str(get_as_data(str(destination)).cc)
        source_country = str(get_as_data(str(source)).cc)
        dest_prefix = get_prefix_from_ip(str(destination))
        print("Dest prefix: ", dest_prefix)
        from_time_ = unix_to_regular(timestamp - 2800)  # at least one hour
        until_time_ = unix_to_regular(timestamp + 2800)

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
            filter=f"prefix any {dest_prefix} and elemtype withdrawals"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                prefix = elem.fields['prefix']
                truncated_timestamp = elem.time // 600 * 600  # Round down to nearest 10 minutes
                matches.append([elem.peer_address, prefix, truncated_timestamp])

        return matches

    L2 = path(timestamp + 10800 , source, destination)
    def find_withdrawals_flaps(destination):
        # Group timestamps by peer_address and prefix, count by 10-minute intervals
        for peer_time_pair in L2:
            peer_address, pref, timestamp = peer_time_pair
            key = (peer_address, pref)
            withdrawal_dict[key]["timestamps"].append(timestamp)
            withdrawal_dict[key]["intervals"][timestamp] += 1
            withdrawal_dict[key]["total"] += 1

        # Print or do something with the grouped timestamps and interval counts
        for key, info in withdrawal_dict.items():
            peer_address, pref = key
            timestamps = info["timestamps"]
            interval_counts = info["intervals"]
            total_withdrawals = info["total"]
            print(f"Peer: {peer_address}, Prefix: {pref}")
            for interval, count in sorted(interval_counts.items()):
                print(f"Interval: {interval}, Count: {count}")
                # Add intervals with at least 8 withdrawals to real_withdrawal
                if count >= 8:
                    real_withdrawal.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
                else:
                    flap.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
            # Add peer_address and prefixes with more than 20 withdrawals in total to real_withdrawal
            if total_withdrawals > 20:
                real_withdrawal.append({"peer_address": peer_address, "prefix": pref, "total_withdrawals": total_withdrawals})
    find_withdrawals_flaps(destination)
    return real_withdrawal, flap
    
    
def match_withdrawals_source(timestamp, source, destination):
    real_withdrawal_L2 = []
    flap_L2 = []
    real_withdrawal_L1 = []
    flap_L1 = []
    withdrawal_dict = defaultdict(lambda: {"timestamps": [], "intervals": defaultdict(int), "total": 0})  

    def path(timestamp, source, destination):
        source_AS = get_as_data(str(source)).asn
        dest_AS = get_as_data(str(destination)).asn
        dest_country = str(get_as_data(str(destination)).cc)
        source_country = str(get_as_data(str(source)).cc)
        src_prefix = get_prefix_from_ip(str(source))
        print("Source prefix: ", src_prefix)
        from_time_ = unix_to_regular(timestamp - 1800)  # at least one hour
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
            filter=f"prefix {src_prefix} and elemtype withdrawals"
        )

        # Read elems
        for rec in stream.records():
            for elem in rec:
                prefix = elem.fields['prefix']
                truncated_timestamp = elem.time // 600 * 600  # Round down to nearest 10 minutes
                matches.append([elem.peer_address, prefix, truncated_timestamp])

        return matches
    L1 = path(timestamp - 10800 , source, destination)
    L2 = path(timestamp + 10800 , source, destination)
    def find_withdrawals_flaps_L2(destination):
        # Group timestamps by peer_address and prefix, count by 10-minute intervals
        for peer_time_pair in L2:
            peer_address, pref, timestamp = peer_time_pair
            key = (peer_address, pref)
            withdrawal_dict[key]["timestamps"].append(timestamp)
            withdrawal_dict[key]["intervals"][timestamp] += 1
            withdrawal_dict[key]["total"] += 1

        # Print or do something with the grouped timestamps and interval counts
        for key, info in withdrawal_dict.items():
            peer_address, pref = key
            timestamps = info["timestamps"]
            interval_counts = info["intervals"]
            total_withdrawals = info["total"]
            print(f"Peer: {peer_address}, Prefix: {pref}")
            for interval, count in sorted(interval_counts.items()):
                print(f"Interval: {interval}, Count: {count}")
                # Add intervals with at least 8 withdrawals to real_withdrawal
                if count >= 25:
                    real_withdrawal_L2.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
                else:
                    flap_L2.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
            # Add peer_address and prefixes with more than 20 withdrawals in total to real_withdrawal
    def find_withdrawals_flaps_L1(destination):
        # Group timestamps by peer_address and prefix, count by 10-minute intervals
        for peer_time_pair in L2:
            peer_address, pref, timestamp = peer_time_pair
            key = (peer_address, pref)
            withdrawal_dict[key]["timestamps"].append(timestamp)
            withdrawal_dict[key]["intervals"][timestamp] += 1
            withdrawal_dict[key]["total"] += 1

        # Print or do something with the grouped timestamps and interval counts
        for key, info in withdrawal_dict.items():
            peer_address, pref = key
            timestamps = info["timestamps"]
            interval_counts = info["intervals"]
            total_withdrawals = info["total"]
            print(f"Peer: {peer_address}, Prefix: {pref}")
            for interval, count in sorted(interval_counts.items()):
                print(f"Interval: {interval}, Count: {count}")
                # Add intervals with at least 8 withdrawals to real_withdrawal
                if count >= 25:
                    real_withdrawal_L1.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
                else:
                    flap_L1.append({"peer_address": peer_address, "prefix": pref, "timestamp": interval, "number of withdrawals": count})
            # Add peer_address and prefixes with more than 20 withdrawals in total to real_withdrawal
    find_withdrawals_flaps_L2(destination)
    find_withdrawals_flaps_L1(destination)
    return real_withdrawal_L1, flap_L1, real_withdrawal_L2, flap_L2
    
timestamp = 1708650000
#source='37.10.41.14'
#source = '38.47.189.189'
#destination = '38.62.206.0'
destination='185.25.205.152'
#timestamp = 1708660000
source = '128.199.105.50'
#destination = '129.122.18.18'

#L1, L2 = random_match_announcements(timestamp, source, destination)
#L1, L2 = partial_match_announcements(timestamp, source, destination)
L1, L2 = exact_match_announcements(timestamp, source, destination)
#real_withdrawal_L1, flap_L1, real_withdrawal_L2, flap_L2 = match_withdrawals_source(timestamp, source, destination)
#real_withdrawal_L1, flap_L1, real_withdrawal_L2, flap_L2 = match_withdrawals_destination(timestamp, source, destination)

#print("real_withdrawal_L1:", real_withdrawal_L1)
#print("flap_L1:", flap_L1)
#print("real_withdrawal_L2:", real_withdrawal_L2)
#print("flap_L2:", flap_L2)
print("L1:", L1)
print("L2:", L2)
