from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
import requests

Builder.load_file('vendors.kv')

class VendorsCard(BoxLayout):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()

    def view_vendor(self):
        vendor_id = self.vendor_id
        print(f"Fetching details for Vendor ID: {vendor_id}, Slug: {self.slug}")

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
            print("Failed to fetch vendor details.")

class VendorsScreen(Screen):
    def __init__(self, **kwargs):
        super(VendorsScreen, self).__init__(**kwargs)

        # Initialize after the screen is fully constructed
        self.load_vendors()

    def load_vendors(self):
        response = requests.get('http://localhost:8000/api/vendor/')
        if response.status_code == 200:
            vendors = response.json()
            print("vendors:", vendors)

            self.clear_vendors()  # Clear any existing vendors before loading new ones
            for vendor in vendors:
                full_image_url = f"http://localhost:8000{vendor['profile_image']}"

                # Fetch service details from the API using service ID
                service_response = requests.get(f'http://localhost:8000/api/service/{vendor["service"]}/')
                if service_response.status_code == 200:
                    service_details = service_response.json()
                    service_name = service_details.get('name', 'Unknown Service')
                else:
                    service_name = 'Unknown Service'

                vendors_card = VendorsCard(
                    institution_name=vendor['institution_name'],
                    price=str(vendor['price']),
                    image_source=full_image_url,
                    vendor_id=str(vendor['id']),
                    slug=vendor['slug'],
                    service=service_name  # Pass service name to VendorsCard
                )
                self.add_vendor(vendors_card)

    def clear_vendors(self):
        # Clear the vendors_layout before adding new vendors
        vendors_layout = self.ids.vendors_layout
        vendors_layout.clear_widgets()

    def add_vendor(self, vendor):
        # Add a new vendor to the vendors_layout
        vendors_layout = self.ids.vendors_layout
        vendors_layout.add_widget(vendor)
