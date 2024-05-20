import requests
from bs4 import BeautifulSoup

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

# Example usage:
prefix = "38.52.196.0/24"  # Replace with the desired prefix
as_number = get_as_number_from_prefix(prefix)
if as_number:
    print(f"The AS number for prefix {prefix} is: {as_number}")
else:
    print("AS number not found.")
