import pybgpstream
from aslookup import get_as_data
from ipaddress import IPv4Network
import datetime
import requests
from bs4 import BeautifulSoup

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

def match_withdrawals_destination():
    from_time_ = unix_to_regular(1708732800)
    until_time_ = unix_to_regular(1708819200)
    
    prefix = get_prefix_from_ip('38.47.189.189')
    
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
        filter=f"prefix {prefix} and elemtype withdrawals"
    )

    for rec in stream.records():
        for elem in rec:
            print(elem)

match_withdrawals_destination()
