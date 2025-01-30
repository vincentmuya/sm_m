from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
from navbar import Navbar
from header import Header
from vendors import VendorsCard
from kivy.uix.widget import Widget
from filter_widget import Filter
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from search_widget import SearchWidget

Builder.load_file('filtered_vendors.kv')

class FilteredVendorsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout setup
        self.layout = BoxLayout(orientation='vertical')

        # Content layout at the top
        self.content_layout = ScrollView(size_hint=(1, 0.9))  # Takes 90% of the screen height
        self.vendor_grid = GridLayout(cols=3, size_hint_y=None, spacing='10dp')
        self.vendor_grid.bind(minimum_height=self.vendor_grid.setter('height'))  # Adjust height dynamically
        self.content_layout.add_widget(self.vendor_grid)

        self.navbar = Navbar(size_hint=(1, 0.1))
        self.header = Header(size_hint=(1, 0.1))

        # Create and add the Filter widget
        self.filter_widget = Filter(filter_callback=self.apply_filter)

        # Spacer widget to add space after the header
        spacer = Widget(size_hint=(1, None), height=30)

        # Create and add the Search widget
        self.search_widget = SearchWidget(search_callback=self.display_search_results)

        # Add widgets to layout
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.search_widget)
        self.layout.add_widget(self.filter_widget)
        self.layout.add_widget(spacer)
        self.layout.add_widget(self.content_layout)
        self.layout.add_widget(self.navbar)
        self.add_widget(self.layout)

    def load_filtered_vendors(self, filtered_vendors, services, location, service, price_range):
        print(f"Loading {len(filtered_vendors)} filtered vendors...")

        # Update the filter display text
        filter_text = "Viewing filtered vendors:"
        if location:
            filter_text += f" Location: {location}"
        if service:
            filter_text += f" Service: {service}"
        if price_range:
            filter_text += f" Price Range: {price_range}"

        self.ids.filter_info_label.text = filter_text

        # Clear grid before adding new vendors
        self.vendor_grid.clear_widgets()

        # Fetch all services and locations to map their IDs to names
        services_response = requests.get('http://localhost:8000/api/services/')
        locations_response = requests.get('http://localhost:8000/api/locations/')

        if services_response.status_code == 200:
            services = {service['id']: service['service'] for service in services_response.json()}
        else:
            services = {}

        if locations_response.status_code == 200:
            locations = {location['id']: location['location'] for location in locations_response.json()}
        else:
            locations = {}

        for vendor in filtered_vendors:
            full_image_url = f"http://localhost:8000{vendor['profile_image']}"

            # Get the location name
            location_id = vendor.get('location')
            location_name = locations.get(location_id, "Unknown Location")

            # Get the service name
            service_id = vendor.get('service')
            service_name = services.get(service_id, "Unknown Service")

            # Create the vendor card
            vendor_card = VendorsCard(
                institution_name=vendor['institution_name'],
                price=str(vendor['price']),
                image_source=full_image_url,
                vendor_id=str(vendor['id']),
                slug=vendor['slug'],
                service=service_name,
                location=location_name
            )
            self.vendor_grid.add_widget(vendor_card)

    def apply_filter(self, location=None, service=None, price_range=None):
        print(f"Applying filter with location={location}, service={service}, price_range={price_range}")

        # Fetch services to resolve the service name to ID
        services_response = requests.get('http://localhost:8000/api/services/')
        services = services_response.json() if services_response.status_code == 200 else []

        # Get the service ID from the service name (if the service exists)
        service_id = None
        if service:
            for s in services:
                if s['service'] == service:
                    service_id = s['id']
                    break

        # Construct the API URL with the service ID
        api_url = 'http://localhost:8000/api/vendor/'
        filters = {}
        if location:
            filters['location'] = location
        if service_id:
            filters['service'] = service_id  # Use the service ID instead of the name
        if price_range:
            filters['price_range'] = price_range

        # Call the API with the updated filters
        response = requests.get(api_url, params=filters)

        if response.status_code == 200:
            filtered_vendors = response.json()
            print("Filtered Vendors:", filtered_vendors)

            app = App.get_running_app()
            # Pass the service_id (parent category) to the vendors_by_service screen
            filtered_vendors_screen = app.root.get_screen('filtered_vendors')
            filtered_vendors_screen.load_filtered_vendors(filtered_vendors, services, location, service, price_range)
            app.root.transition = SlideTransition(direction='left')
            app.root.current = 'filtered_vendors'

    def display_search_results(self, vendors, search_query):
        # print(f"Search results: {len(vendors)}")
        # print("Search results:", vendors)
        app = App.get_running_app()
        # Pass the service_id (parent category) to the search_results screen
        search_results_screen = app.root.get_screen('search_results')
        search_results_screen.load_search_results(vendors, search_query)
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'search_results'