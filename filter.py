import requests


def filter_vendors(location=None, service=None, price_range=None):
    # Make API request to retrieve vendors
    api_url = 'http://localhost:8000/api/vendor/'
    response = requests.get(api_url)

    if response.status_code == 200:
        vendors = response.json()
        print("Vendors:", vendors)

        # Modify the price field for each vendor
        for vendor in vendors:
            if vendor.get('price') is not None:
                vendor['price_formatted'] = "{:,.0f}".format(vendor['price'])

        # Filter vendors based on location, service, and price range
        filtered_vendors = vendors

        if location:
            filtered_vendors = [vendor for vendor in filtered_vendors if vendor.get('location__slug') == location]
        if service:
            filtered_vendors = [vendor for vendor in filtered_vendors if vendor.get('service__slug') == service]
        if price_range:
            min_price, max_price = map(int, price_range.split('-'))
            filtered_vendors = [vendor for vendor in filtered_vendors if min_price <= vendor.get('price') <= max_price]

        return filtered_vendors

    else:
        print(f"Failed to retrieve vendors. Status code: {response.status_code}")
        return []
