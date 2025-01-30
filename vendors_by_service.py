from kivy.uix.screenmanager import Screen, SlideTransition
from navbar import Navbar
from kivy.lang import Builder
import requests
from kivy.uix.gridlayout import GridLayout
from vendors import VendorsCard
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from header import Header
from kivy.factory import Factory
from filter_widget import Filter
from kivy.app import App
from search_widget import SearchWidget

Builder.load_file('vendors_by_service.kv')


class VendorsByServiceScreen(Screen):
    """A screen to show vendors for the selected parent category."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use a BoxLayout to stack the content and Navbar
        self.layout = BoxLayout(orientation='vertical')

        # Content layout at the top
        self.content_layout = ScrollView(size_hint=(1, 0.9))  # Takes 90% of the screen height
        self.vendor_grid = GridLayout(cols=3, size_hint_y=None, spacing='10dp')
        self.vendor_grid.bind(minimum_height=self.vendor_grid.setter('height'))  # Adjust height dynamically
        self.content_layout.add_widget(self.vendor_grid)

        # Create and add the Filter widget
        self.filter_widget = Filter(filter_callback=self.apply_filter)

        # Create and add the Search widget
        self.search_widget = SearchWidget(search_callback=self.display_search_results)

        # Navbar at the bottom
        self.navbar = Navbar(size_hint=(1, 0.1))  # Takes 10% of the screen height
        self.header = Header(size_hint=(1, 0.1))

        # Spacer widget to add space after the header
        spacer = Widget(size_hint=(1, None), height=30)

        # Add widgets to the layout
        self.layout.add_widget(self.header)  # Header at the top
        self.layout.add_widget(self.search_widget)
        self.layout.add_widget(self.filter_widget)
        self.layout.add_widget(spacer)
        self.layout.add_widget(self.content_layout)  # Content in the middle
        self.layout.add_widget(self.navbar)  # Navbar at the bottom
        self.add_widget(self.layout)

    def load_vendors_for_service(self, service_id):
        """Load vendors based on the selected parent service category."""
        # Fetch vendors for the selected parent category
        response = requests.get(f'http://localhost:8000/api/vendor/?parent_service={service_id}')

        # Fetch the parent service name
        services_response = requests.get('http://localhost:8000/api/services/')
        parent_service_name = "Unknown Category"  # Default name if the parent service is not found

        if services_response.status_code == 200:
            services = services_response.json()
            # Find the parent service name using the service_id
            for service in services:
                if service['id'] == service_id:
                    parent_service_name = service['service']
                    break
        else:
            print("Failed to fetch services for finding parent name.")

        # Create the header with the parent service name
        header = Factory.CategoryHeader(text=f"[b]{parent_service_name}[/b]")

        # Fetch and display vendors for the parent service
        if response.status_code == 200:
            vendors = response.json()
            print(f"Vendors for Parent Service ID {service_id}:", vendors)

            # Ensure layout is properly reset
            self.ids.vendors_layout.clear_widgets()  # Clear previous widgets if needed
            self.ids.vendors_layout.add_widget(header)  # Add the parent service header to the layout

            # Display vendors under this parent category
            self.display_vendors(vendors)  # Call display_vendors to render the vendors
        else:
            print("Failed to fetch vendors for this service.")

    def display_vendors(self, vendors):
        """Display the vendors on the screen."""
        # Clear the previous vendor grid
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

        for vendor in vendors:
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
                service=service_name,  # Use the service name instead of the ID
                location=location_name  # Include the location name
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