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
import concurrent.futures

def get_as_numbers_by_country(country_acronym):
    with open("as_country_mapping.json", "r") as file:
        as_country_mapping = json.load(file)
    return [as_number for as_number, country_code in as_country_mapping.items() if country_code == country_acronym]

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_as_number_from_prefix(prefix):
    url = f"https://bgpview.io/prefix/{prefix}"
    content = fetch_url(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find("table", class_="table table-hover")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    as_number_element = cells[1].find("a")
                    if as_number_element:
                        return as_number_element.text.strip()[2:]  # Remove the "AS" prefix
    return None

def get_country_from_bgpview(asn):
    url = f"https://bgpview.io/asn/{asn}"
    content = fetch_url(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img_tag = soup.find('img', {'title': True, 'alt': True})
        if img_tag:
            return img_tag['alt'].split('(')[-1].split(')')[0].strip()
    return None

def get_prefix_from_ip(ip_address):
    url = f"https://bgp.he.net/ip/{ip_address}"
    content = fetch_url(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        td_elements = soup.find_all('td', class_='nowrap')
        for td in td_elements:
            a_element = td.find('a')
            if a_element:
                return a_element.text.strip()
    return None

def unix_to_regular(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

def announcements_types(timestamp, source, destination):
    source_AS = get_as_data(str(source)).asn
    dest_AS = get_as_data(str(destination)).asn

    with concurrent.futures.ThreadPoolExecutor() as executor:
        source_country_future = executor.submit(get_country_from_bgpview, source_AS)
        destination_country_future = executor.submit(get_country_from_bgpview, dest_AS)
        source_country = source_country_future.result()
        destination_country = destination_country_future.result()

    source_list = get_as_numbers_by_country(source_country)
    destination_list = get_as_numbers_by_country(destination_country)
    
    L1, L2 = exact_match_announcements(timestamp, source, destination)
    
    if not L1 and not L2:
        for i in destination_list:
            if not L1 and not L2:
                L1, L2 = exact_match_announcements(timestamp, source, i)
    
    if not L1 and not L2:
        for s in source_list:
            for d in destination_list:
                if not L1 and not L2:
                    L1, L2 = exact_match_announcements(timestamp, s, d)
                    if L1 or L2:
                        break
            if L1 or L2:
                break
    
    return L1, L2

def exact_match_announcements(timestamp, source, destination):
    def path(timestamp, source, destination):
        from_time_ = unix_to_regular(timestamp - 1800)
        until_time_ = unix_to_regular(timestamp + 1800)
        matches = []

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
            filter=f"path ^{source}_.*_{destination}$ and elemtype announcements"
        )

        for rec in stream.records():
            for elem in rec:
                if 'as-path' in elem.fields:
                    as_path = elem.fields['as-path']
                    prefix = elem.fields['prefix']
                    if ':' not in prefix:
                        matches.append([as_path.split(), elem.time])
        return matches

    L1 = path(timestamp - 10800, source, destination)
    L2 = path(timestamp + 10800, source, destination)
    return L1, L2

def write_to_file(data, filename):
    with open(filename, "w") as file:
        json_data = []
        for item in data:
            truncated_timestamp = int(item[1]) // 600 * 600
            json_data.append([item[0], truncated_timestamp])
        json.dump(json_data, file)

def get_announcements(timestamp, source, destination):
    L1, L2 = announcements_types(timestamp, source, destination)
    write_to_file(L1, "announcements_before.json")
    write_to_file(L2, "announcements_after.json")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 paths2.py timestamp source destination")
        return

    timestamp = int(sys.argv[1])
    source = sys.argv[2]
    destination = sys.argv[3]

    get_announcements(timestamp, source, destination)

if __name__ == "__main__":
    main()
