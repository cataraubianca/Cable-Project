import json

def get_as_numbers_by_country(country_acronym):
    # Load the contents of the as_country_mapping.json file
    with open("as_country_mapping.json", "r") as file:
        as_country_mapping = json.load(file)
    
    # Initialize a list to store AS numbers
    as_numbers = []
    
    # Iterate through the items in the mapping
    for as_number, country_code in as_country_mapping.items():
        # Check if the country code matches the provided acronym
        if country_code == country_acronym:
            # Append the AS number to the list
            as_numbers.append(as_number)
    
    return as_numbers

# Example usage:
country_acronym = "US"  # Replace with the desired country acronym
as_numbers_us = get_as_numbers_by_country(country_acronym)
print("AS numbers for US:", as_numbers_us)
