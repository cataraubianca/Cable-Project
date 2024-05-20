import pybgpstream
from aslookup import get_as_data
from ipaddress import IPv4Network
import datetime
import whois
from bs4 import BeautifulSoup
import requests
import json

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

def find_source():
    as_country_mapping = {}  # Dictionary to store ASN-country mappings
#1708762800
    stream = pybgpstream.BGPStream(
        from_time=1708680000,
        until_time=1708680060,
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
                    try:
                        destination = get_as_data(str(ip_address)).asn
                        destination_c = get_as_data(str(ip_address)).cc
                        as_array = as_path.split()
                        for asn in as_array:
                            if asn not in as_country_mapping:
                                # Retrieve country for ASN and store in dictionary
                                country = get_country_from_bgpview(asn)
                                as_country_mapping[asn] = country
                    except Exception as e:
                        print(f"Error occurred: {e}")
                        continue  # Skip to the next IP address
    
    # Write ASNs and their associated countries to a file
    with open("as_country_mapping.json", "w") as file:
        json.dump(as_country_mapping, file)
    
    return None

find_source()
