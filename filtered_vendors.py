from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
import requests
from navbar import Navbar
from header import Header

Builder.load_file('filtered_vendors.kv')

class FilteredVendorsCard(BoxLayout):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    location = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()

    def view_vendor(self):
        print(f"Viewing vendor: {self.institution_name}")


class FilteredVendorsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout setup
        self.layout = BoxLayout(orientation='vertical')

        self.navbar = Navbar(size_hint=(1, 0.1))
        self.header = Header(size_hint=(1, 0.1))

        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.grid_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        self.scroll_view.add_widget(self.grid_layout)

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.navbar)
        self.add_widget(self.layout)

    def load_filtered_vendors(self, filtered_vendors, services):
        print(f"Loading {len(filtered_vendors)} filtered vendors...")
        self.grid_layout.clear_widgets()

        locations_response = requests.get('http://localhost:8000/api/locations/')
        locations = {loc['id']: loc['location'] for loc in locations_response.json()} if locations_response.status_code == 200 else {}

        for vendor in filtered_vendors:
            service_name = next((s['service'] for s in services if s['id'] == vendor['service']), "Unknown Service")
            full_image_url = f"http://localhost:8000{vendor['profile_image']}"
            location_name = locations.get(vendor.get('location'), "Unknown Location")

            card = FilteredVendorsCard(
                institution_name=vendor['institution_name'],
                price=str(vendor['price']),
                image_source=full_image_url,
                service=service_name,
                location=location_name,
                slug=vendor['slug'],
                vendor_id=str(vendor['id'])
            )
            self.grid_layout.add_widget(card)
