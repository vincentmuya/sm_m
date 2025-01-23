from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import requests
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage

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

            self.clear_vendors()  # Clear any existing vendors before loading new ones
            for vendor in vendors:
                full_image_url = f"http://localhost:8000{vendor['profile_image']}"

                # Find the service name corresponding to the vendor's service_id
                service_id = vendor['service']
                service_name = 'Unknown Service'
                for service in services:
                    if service['id'] == service_id:
                        service_name = service['service']
                        break



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

