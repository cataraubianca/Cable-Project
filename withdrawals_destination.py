import pybgpstream
from aslookup import get_as_data
from ipaddress import IPv4Network
import datetime
import whois
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import sys 
import json

def save_to_files(timestamp, source, destination):
    def write_to_file(data, filename):
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    
    def get_as_number_from_prefix(prefix):
        url = f"https://bgpview.io/prefix/{prefix}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", class_="table table-hover")
            if table:
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        as_number_element = cells[1].find("a")
                        if as_number_element:
                            as_number = as_number_element.text.strip()[2:]
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
                
        
    def match_withdrawals_destination(timestamp, source, destination):
        real_withdrawal_L2 = []
        flap_L2 = []
        real_withdrawal_L1 = []
        flap_L1 = []
        withdrawal_dict = defaultdict(lambda: {"timestamps": [], "intervals": defaultdict(int), "total": 0})

        def path(from_time, until_time, dst_prefix):
            matches = []
            stream = []
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
                filter=f"prefix {dst_prefix} and elemtype withdrawals"
            )
            for rec in stream.records():
                for elem in rec:
                    prefix = elem.fields['prefix']
                    truncated_timestamp = elem.time // 600 * 600
                    matches.append([elem.peer_address, prefix, truncated_timestamp])
            return matches
        
        timestamp = int(timestamp)
        dst_prefix = get_prefix_from_ip(str(destination))
        L2 = path(timestamp + 10800, timestamp + 14400, dst_prefix)
        L1 = path(timestamp - 14400, timestamp - 10800, dst_prefix)

        def find_withdrawals_flaps(data, real_withdrawal, flap):
            withdrawal_dict.clear()
            for peer_time_pair in data:
                peer_address, pref, timestamp = peer_time_pair
                key = (peer_address, pref)
                withdrawal_dict[key]["timestamps"].append(timestamp)
                withdrawal_dict[key]["intervals"][timestamp] += 1
                withdrawal_dict[key]["total"] += 1

            for key, info in withdrawal_dict.items():
                peer_address, pref = key
                interval_counts = info["intervals"]
                for interval, count in sorted(interval_counts.items()):
                    if count >= 25:
                        real_withdrawal.append([peer_address, pref, interval, count])
                    else:
                        flap.append([peer_address, pref, interval, count])

        find_withdrawals_flaps(L2, real_withdrawal_L2, flap_L2)
        find_withdrawals_flaps(L1, real_withdrawal_L1, flap_L1)

        return real_withdrawal_L1, flap_L1, real_withdrawal_L2, flap_L2
        
    real_withdrawal_L1, flap_L1, real_withdrawal_L2, flap_L2 = match_withdrawals_destination(timestamp, source, destination)
  
    # Write arrays to files
    #print(real_withdrawal_L1, "real_withdrawal_L1_source.json")
    write_to_file(real_withdrawal_L1, "real_withdrawal_L1_destination.json")
    #print(flap_L1, "flap_L1_source.json")
    write_to_file(flap_L1, "flap_L1_destination.json")
    #print(real_withdrawal_L2, "real_withdrawal_L2_source.json")
    write_to_file(real_withdrawal_L2, "real_withdrawal_L2_destination.json")
    #print(flap_L2, "flap_L2_source.json")
    write_to_file(flap_L2, "flap_L2_destination.json")
    
def main():
    if len(sys.argv) != 4:
        print("Usage: python3 paths2.py timestamp source destination")
        return

    timestamp = int(sys.argv[1])
    source = sys.argv[2]
    destination = sys.argv[3]

    # Call the save_to_files function with the provided parameters
    save_to_files(timestamp, source, destination)

if __name__ == "__main__":
    main()