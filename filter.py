import requests

def filter_vendors(location=None, service=None, price_range=None):
    # Base API URL
    api_url = 'http://localhost:8000/api/vendor/'

    # Construct query parameters dynamically
    params = {}
    if location:
        params['location'] = location
    if service:
        params['service'] = service
    if price_range:
        params['price_range'] = price_range

    # Make API request with query parameters
    try:
        response = requests.get(api_url, params=params)
        print(f"API URL called: {response.url}")  # Debug: View the constructed URL

        if response.status_code == 200:
            vendors = response.json()
            # print("Vendors:", vendors)

            # Format the price field for each vendor
            for vendor in vendors:
                if vendor.get('price') is not None:
                    vendor['price_formatted'] = "{:,.0f}".format(vendor['price'])

            return vendors  # Return the filtered vendors
        else:
            print(f"Failed to retrieve vendors. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
