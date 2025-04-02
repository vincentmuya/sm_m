from navbar import Navbar
from header import Header
from vendors import VendorsCard
from kivy.uix.widget import Widget
from filter_widget import Filter
from search_widget import SearchWidget

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.button import Button

Builder.load_file('favorites.kv')

class FavoritesScreen(Screen):
    """A screen to display favorite vendors."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set up the ScrollView
        self.scroll_type = ['bars']
        self.bar_width = 10
        self.do_scroll_x = False
        self.do_scroll_y = True

        # Create a layout to contain the content and wrap it in a scrollview
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # Create and add the Search widget
        self.search_widget = SearchWidget(search_callback=self.display_search_results)

        # Create and add the Filter widget
        self.filter_widget = Filter(filter_callback=self.apply_filter)

        # Add other screens (VendorsScreen) to the content layout
        self.vendor_grid = GridLayout(cols=3, size_hint_y=None, spacing='10dp')

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=20)
        bottom_spacer = Widget(size_hint=(1, None), height=650)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.vendor_grid)
        self.content_layout.add_widget(bottom_spacer)

        # Create the ScrollView and add the content_layout inside it
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=20)
        scroll_view.add_widget(self.content_layout)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        header.pos_hint = {'x': 0, 'y': 0.95}
        # Add ScrollView and navbar to the FloatLayout
        self.add_widget(scroll_view)  # Add ScrollView with content on top
        self.add_widget(header)

        # Create and add the navbar, fixed at the bottom of the screen
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}
        # Add ScrollView and navbar to the FloatLayout
        self.add_widget(nav_bar)

        # ✅ Use a proxy button instead of moving the original button
        app = App.get_running_app()
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(150, 40),pos=(650, 560))
        # ✅ Create a proxy button
        self.account_proxy_button = Button(text=app.account_button.text)
        # ✅ Open dropdown manually when proxy button is clicked
        self.account_proxy_button.bind(on_release=self.open_account_dropdown)
        # ✅ Add proxy button instead of the real one
        self.user_info_layout.add_widget(self.account_proxy_button)
        self.add_widget(self.user_info_layout)

    def open_account_dropdown(self, instance):
        """Manually opens the account dropdown."""
        app = App.get_running_app()
        #Ensure dropdown is updated before opening
        app.update_account_dropdown()
        #Open dropdown manually
        app.account_dropdown.open(instance)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()
        #Ensure the proxy button always has updated text
        self.account_proxy_button.text = app.account_button.text

    def load_favorite_vendors(self, user_favorites):
        print(f"Loading {len(user_favorites)} Favorite vendors...")

        # Clear grid before adding new vendors
        self.vendor_grid.clear_widgets()

        favorite_label = Label(
            text=f"Viewing Favorite Vendors",
            size_hint_y=None,
            height=5,
            font_size="15sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        favorite_label2 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        favorite_label3 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )

        self.vendor_grid.add_widget(favorite_label2)
        self.vendor_grid.add_widget(favorite_label)
        self.vendor_grid.add_widget(favorite_label3)

        # Fetch all services and locations to map their IDs to names
        services_response = requests.get('https://sherehemall.co.ke/api/services/')
        locations_response = requests.get('https://sherehemall.co.ke/api/locations/')

        if services_response.status_code == 200:
            services = {service['id']: service['service'] for service in services_response.json()}
        else:
            services = {}

        if locations_response.status_code == 200:
            locations = {location['id']: location['location'] for location in locations_response.json()}
        else:
            locations = {}

        for favorite in user_favorites:
            vendor = favorite["vendor"]  # ✅ Extract vendor details

            full_image_url = f"https://sherehemall.co.ke{vendor['profile_image']}"  # ✅ Now it exists

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
        # print(f"Applying filter with location={location}, service={service}, price_range={price_range}")

        # Fetch services to resolve the service name to ID
        services_response = requests.get('https://sherehemall.co.ke/api/services/')
        services = services_response.json() if services_response.status_code == 200 else []

        # Get the service ID from the service name (if the service exists)
        service_id = None
        if service:
            for s in services:
                if s['service'] == service:
                    service_id = s['id']
                    break

        # Construct the API URL with the service ID
        api_url = 'https://sherehemall.co.ke/api/vendor/'
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
            # print("Filtered Vendors:", filtered_vendors)

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