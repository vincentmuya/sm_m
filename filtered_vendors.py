from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import requests
from kivy.app import App


Builder.load_file('filtered_vendors.kv')


class FilteredVendorsCard(BoxLayout):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()

    def view_filtered_vendor(self):
        vendor_id = self.vendor_id
        print(f"Fetching details for Filtered Vendor ID: {vendor_id}, Slug: {self.slug}")

        api_url = f"http://localhost:8000/api/vendor/{vendor_id}/{self.slug}/"
        response = requests.get(api_url)
        print("API Response Status Code:", response.status_code)
        print("API Response Content:", response.content.decode())

        if response.status_code == 200:
            vendor_details = response.json()
            print("Vendor Details:", vendor_details)

            app = App.get_running_app()
            vendor_details_screen = app.root.get_screen('vendor_details')
            vendor_details_screen.load_details(vendor_details)

            app.root.transition = SlideTransition(direction='left')
            app.root.current = 'vendor_details'
        else:
            print("Failed to fetch filtered vendor details.")


class FilteredVendorsScreen(Screen):
    def __init__(self, **kwargs):
        super(FilteredVendorsScreen, self).__init__(**kwargs)

        # Initialize after the screen is fully constructed
        self.load_filtered_vendors()

    def load_filtered_vendors(self):
        # Fetch all services from the services API
        services_response = requests.get('http://localhost:8000/api/services/')
        if services_response.status_code == 200:
            services = services_response.json()
            print("Services:", services)
        else:
            services = []

        # Fetch all vendors from the vendor API
        response = requests.get('http://localhost:8000/api/vendor/')
        if response.status_code == 200:
            vendors = response.json()
            print("vendors:", vendors)

            self.clear_filtered_vendors()  # Clear any existing vendors before loading new ones
            for vendor in vendors:
                full_image_url = f"http://localhost:8000{vendor['profile_image']}"

                # Find the service name corresponding to the vendor's service_id
                service_id = vendor['service']
                service_name = 'Unknown Service'
                for service in services:
                    if service['id'] == service_id:
                        service_name = service['service']
                        break

                filtered_vendors_card = FilteredVendorsCard(
                    institution_name=vendor['institution_name'],
                    price=str(vendor['price']),
                    image_source=full_image_url,
                    vendor_id=str(vendor['id']),
                    slug=vendor['slug'],
                    service=service_name  # Pass service name to VendorsCard
                )
                self.add_filtered_vendor(filtered_vendors_card)

    def clear_filtered_vendors(self):
        # Clear the filtered_vendor_layout before adding new vendors
        filtered_vendor_layout = self.ids.filtered_vendor_layout
        filtered_vendor_layout.clear_widgets()

    def add_filtered_vendor(self, vendor):
        # Add a new vendor to the filtered_vendor_layout
        filtered_vendor_layout = self.ids.filtered_vendor_layout
        filtered_vendor_layout.add_widget(vendor)
