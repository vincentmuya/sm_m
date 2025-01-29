from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
import requests
from navbar import Navbar
from header import Header
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.clock import Clock

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

        # Debug Label
        self.test_label = Label(text="Filtered Vendors Screen", font_size="20sp", color=(1, 0, 0, 1))

        # ScrollView and GridLayout
        self.scroll_view = ScrollView(size_hint=(1, 0.9), do_scroll_x=False)
        self.grid_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Force a larger height temporarily for debugging
        self.grid_layout.height = 1000  # Large fixed height for testing
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.scroll_view.add_widget(self.grid_layout)

        # Add widgets to layout
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.test_label)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.navbar)
        self.add_widget(self.layout)

        # ✅ Add a static test card to check if widgets are visible
        test_card = FilteredVendorsCard(
            institution_name="Test Vendor",
            price="5000",
            image_source="https://png.pngtree.com/png-vector/20210604/ourmid/pngtree-gray-network-placeholder-png-image_3416659.jpg",
            service="Test Service",
            location="Test Location",
            slug="test-vendor",
            vendor_id="1"
        )
        self.grid_layout.add_widget(test_card)

    def load_filtered_vendors(self, filtered_vendors, services):
        print(f"Loading {len(filtered_vendors)} filtered vendors...")

        # Clear grid before adding new vendors
        self.grid_layout.clear_widgets()

        # Fetch location data
        locations_response = requests.get('http://localhost:8000/api/locations/')
        if locations_response.status_code == 200:
            locations = {loc['id']: loc['location'] for loc in locations_response.json()}
        else:
            locations = {}

        # Print fetched vendors list
        print(f"Filtered Vendors List: {filtered_vendors}")

        for vendor in filtered_vendors:
            print(f"Processing vendor: {vendor}")

            # Check if essential fields exist
            if 'institution_name' not in vendor or 'profile_image' not in vendor:
                print(f"Skipping vendor due to missing fields: {vendor}")
                continue  # Skip if data is incomplete

            # Extract details
            service_name = next((s['service'] for s in services if s['id'] == vendor['service']), "Unknown Service")
            full_image_url = f"http://localhost:8000{vendor['profile_image']}"
            location_name = locations.get(vendor.get('location'), "Unknown Location")

            print(f"Creating card for: {vendor['institution_name']} with Image URL: {full_image_url}")

            # Create card
            card = FilteredVendorsCard(
                institution_name=vendor['institution_name'],
                price=str(vendor['price']),
                image_source=full_image_url,
                service=service_name,
                location=location_name,
                slug=vendor['slug'],
                vendor_id=str(vendor['id'])
            )

            # Add to GridLayout
            self.grid_layout.add_widget(card)
            print(f"Widget Count in GridLayout: {len(self.grid_layout.children)}")

            print(f"Added card for {vendor['institution_name']} to grid layout")

        # Print the number of widgets in the layout
        print(f"Total widgets in grid layout after loading: {len(self.grid_layout.children)}")

        self.grid_layout.do_layout()
        self.layout.do_layout()

        Clock.schedule_once(lambda dt: self.grid_layout.do_layout(), 0)
        Clock.schedule_once(lambda dt: self.layout.do_layout(), 0)