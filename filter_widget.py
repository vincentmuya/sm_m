from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
import requests
from kivy.uix.label import Label
from kivy.utils import rgba


class Filter(BoxLayout):
    def __init__(self, filter_callback=None, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50

        # Introductory Label with color
        self.intro_label = Label(text="Filter By Location,\nService, Price Or All", size_hint_x=None, width=150)
        self.intro_label.color = rgba("#000000")  # Set color using RGBA hex format
        self.add_widget(self.intro_label)

        # Location Dropdown
        self.location_dropdown = DropDown()
        self.location_button = Button(text='Location', on_release=self.location_dropdown.open)
        self.location_dropdown.bind(on_select=lambda instance, x: setattr(self.location_button, 'text', x))
        self.add_widget(self.location_button)

        # Populate Location Dropdown dynamically from API
        self.populate_location_dropdown()

        # Service Dropdown
        self.service_dropdown = DropDown()
        self.service_button = Button(text='Service', on_release=self.service_dropdown.open)
        self.service_dropdown.bind(on_select=lambda instance, x: setattr(self.service_button, 'text', x))
        self.add_widget(self.service_button)

        # Populate Service Dropdown dynamically from API
        self.populate_service_dropdown()

        # Price Range Dropdown
        self.price_range_dropdown = DropDown()
        self.price_range_button = Button(text='Price Range', on_release=self.price_range_dropdown.open)
        self.price_range_dropdown.bind(on_select=lambda instance, x: setattr(self.price_range_button, 'text', x))
        self.add_widget(self.price_range_button)

        # Populate Price Range Dropdown dynamically from API
        self.populate_price_range_dropdown()

        # Apply Button
        self.apply_button = Button(text='Apply Filters', on_press=self.apply_filters)
        self.add_widget(self.apply_button)

        # Callback function to be called when filters are applied
        self.filter_callback = filter_callback

    def populate_location_dropdown(self):
        # Make an HTTP GET request to your Django API endpoint
        api_url = 'http://localhost:8000/api/locations/'
        response = requests.get(api_url)

        if response.status_code == 200:
            locations = response.json()

            # Iterate over locations and add them to the dropdown
            for location in locations:
                btn = Button(text=location['location'], size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.location_dropdown.select(btn.text))
                self.location_dropdown.add_widget(btn)
        else:
            print(f"Failed to retrieve locations. Status code: {response.status_code}")

    def populate_service_dropdown(self):
        # Make an HTTP GET request to your Django API endpoint
        api_url = 'http://localhost:8000/api/services/'
        response = requests.get(api_url)

        if response.status_code == 200:
            services = response.json()

            # Iterate over locations and add them to the dropdown
            for service in services:
                btn = Button(text=service['service'], size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.service_dropdown.select(btn.text))
                self.service_dropdown.add_widget(btn)
        else:
            print(f"Failed to retrieve locations. Status code: {response.status_code}")

    def populate_price_range_dropdown(self):
        # Make an HTTP GET request to your Django API endpoint for vendors
        api_url = 'http://localhost:8000/api/vendor/'
        response = requests.get(api_url)

        if response.status_code == 200:
            vendors = response.json()

            # Filter out vendors with non-null prices
            prices = [vendor['price'] for vendor in vendors if vendor['price'] is not None]

            # Calculate min and max prices
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0

            # Define step size for price range
            step = 10000  # Adjust this value according to your preference

            # Generate price range options
            while min_price <= max_price:
                price_range_text = f"{min_price} - {min(min_price + step, max_price)}"
                btn = Button(text=price_range_text, size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.price_range_dropdown.select(btn.text))
                self.price_range_dropdown.add_widget(btn)
                min_price += step
        else:
            print(f"Failed to retrieve vendors. Status code: {response.status_code}")

    def apply_filters(self, instance):
        location = self.location_button.text if self.location_button.text != 'Location' else None
        service = self.service_button.text if self.service_button.text != 'Service' else None
        price_range = self.price_range_button.text if self.price_range_button.text != 'Price Range' else None

        if self.filter_callback:
            filtered_vendors = self.filter_callback(location=location, service=service, price_range=price_range)
            # Perform actions with filtered_vendors (e.g., update UI)
            print("Filtered Vendors:", filtered_vendors)
