from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import requests
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

Builder.load_file('vendors.kv')

class VendorsCard(BoxLayout):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    location = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()

    def view_vendor(self):
        vendor_id = self.vendor_id
        # print(f"Fetching details for Vendor ID: {vendor_id}, Slug: {self.slug}")

        api_url = f"https://sherehemall.co.ke/api/vendor/{vendor_id}/{self.slug}/"
        response = requests.get(api_url)
        # print("API Response Status Code:", response.status_code)
        # print("API Response Content:", response.content.decode())

        if response.status_code == 200:
            vendor_details = response.json()
            # print("Vendor Details:", vendor_details)

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
        self.add_carousel()
        self.load_vendors()

    def create_carousel(self):
        carousel = Carousel(direction='right')
        image_urls = [
            "https://sherehemall.co.ke/static/images/sherehe_header.jpeg",
            "https://polokwanespa.co.za/wp-content/uploads/2020/03/March_amazing-Autumn-spa-treatments_resized-v2.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Jay_nyama_Choma.jpg/2560px-Jay_nyama_Choma.jpg",
            "https://hashtagmagazine.in/wp-content/uploads/2022/08/Popular-Night-Clubs-in-India-Hashtag-Magazine.png",
            "https://lompocwinefactory.com/wp-content/uploads/2019/03/alcohol-bar-beer-1283219.jpg",
            "https://www.mazeevents.in/wp-content/uploads/2024/04/event-management-companies-in-bangalore.jpg",
            "https://scwcontent.affino.com/AcuCustom/Sitename/DAM/019/Theme_park_AdobeStock_222547272_1.jpg"
        ]

        for src in image_urls:
            image = AsyncImage(source=src, allow_stretch=True)
            carousel.add_widget(image)

        return carousel

    def add_carousel(self):
        # Add the carousel to the top of the screen
        carousel = self.create_carousel()
        self.ids.carousel_layout.add_widget(carousel)

    def load_vendors(self):
        # Fetch all services (categories)
        services_response = requests.get('https://sherehemall.co.ke/api/services/')
        if services_response.status_code == 200:
            services = services_response.json()
            # print("Services:", services)
        else:
            services = []

        # Fetch all locations
        locations_response = requests.get('https://sherehemall.co.ke/api/locations/')
        if locations_response.status_code == 200:
            locations = locations_response.json()
            # print("Locations:", locations)
        else:
            locations = []

        # Fetch all vendors
        response = requests.get('https://sherehemall.co.ke/api/vendor/')
        if response.status_code == 200:
            vendors = response.json()
            # print("Vendors:", vendors)

            self.clear_vendors()  # Clear existing vendors before loading new ones

            # Build a map of services by ID
            services_map = {service['id']: service for service in services}

            # Identify parent categories
            parent_categories = {s['id']: s for s in services if s['parent'] is None}
            # print("Parent Categories:", parent_categories)

            # Group vendors by their parent category
            vendors_by_parent = {parent_id: [] for parent_id in parent_categories.keys()}
            for vendor in vendors:
                service_id = vendor['service']
                # Find the parent category for this vendor
                parent_id = service_id
                while services_map.get(parent_id) and services_map[parent_id]['parent'] is not None:
                    parent_id = services_map[parent_id]['parent']
                # Add vendor to the correct parent category
                if parent_id in vendors_by_parent:
                    vendors_by_parent[parent_id].append(vendor)

            # Display vendors grouped by parent category
            for parent_id, parent_category in parent_categories.items():
                parent_name = parent_category['service']
                # print(f"Displaying Vendors for Parent Category: {parent_name}")

                # Create a header for the parent category
                header = Factory.CategoryHeader(text=f"[b]{parent_name}[/b]")
                self.ids.vendors_layout.add_widget(header)

                # Add "View More" button
                view_more_button = Button(
                    text="View More",
                    font_size="15sp",
                    background_color=(1, 1, 1, 1),
                    color=(1, 1, 1, 1),
                    size=(70, 30),
                    size_hint=(None, None),
                    pos=(30, 20),
                )

                view_more_button.bind(
                    on_press=lambda x, parent_id=parent_id: self.switch_to_vendors_by_service(parent_id))
                self.ids.vendors_layout.add_widget(view_more_button)

                # Add vendors under this parent category
                if parent_id in vendors_by_parent:
                    # Create a GridLayout for vendors in this category
                    vendor_grid = GridLayout(cols=3, size_hint_y=None, spacing='10dp')
                    vendor_grid.bind(minimum_height=vendor_grid.setter('height'))  # Adjust height dynamically

                    for vendor in vendors_by_parent[parent_id][:3]: # Add only the first three vendors in this category
                        full_image_url = f"https://sherehemall.co.ke{vendor['profile_image']}"

                        # Find the location name
                        location_id = vendor.get('location')
                        location_name = 'Unknown Location'
                        for location in locations:
                            if location['id'] == location_id:
                                location_name = location['location']
                                break

                        vendors_card = VendorsCard(
                            institution_name=vendor['institution_name'],
                            price=str(vendor['price']),
                            image_source=full_image_url,
                            vendor_id=str(vendor['id']),
                            slug=vendor['slug'],
                            service=services_map[vendor['service']]['service'],  # Vendor's exact service
                            location=location_name
                        )
                        vendor_grid.add_widget(vendors_card)

                    # Add the vendor grid to the parent layout
                    self.ids.vendors_layout.add_widget(vendor_grid)
                else:
                    print(f"No vendors found for Parent Category: {parent_name}")
        else:
            print("Failed to fetch vendors.")

    def clear_vendors(self):
        """Clear the vendors_layout before adding new vendors."""
        vendors_layout = self.ids.vendors_layout
        vendors_layout.clear_widgets()

    def add_vendor(self, vendor):
        """Add a vendor card to the vendors_layout."""
        vendors_layout = self.ids.vendors_layout
        vendors_layout.add_widget(vendor)

    def switch_to_vendors_by_service(self, service_id, *args):
        """Switch to the 'vendors_by_service' screen and show vendors for the selected service."""
        app = App.get_running_app()
        # Pass the service_id (parent category) to the vendors_by_service screen
        vendors_by_service_screen = app.root.get_screen('vendors_by_service')
        vendors_by_service_screen.load_vendors_for_service(service_id)
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'vendors_by_service'