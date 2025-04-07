from filter_widget import Filter
from filtered_vendors import FilteredVendorsScreen
from vendors import VendorsScreen
from header import Header
from navbar import Navbar
from search_widget import SearchWidget

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.toast import toast
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

class LandingPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super(LandingPage, self).__init__(**kwargs)

        self.scroll_type = ['bars']
        self.bar_width = 10
        self.do_scroll_x = False
        self.do_scroll_y = True

        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # ✅ Header (fixed), Search, and Filter inside a vertical container
        self.search_widget = SearchWidget(search_callback=self.display_search_results)
        self.filter_widget = Filter(filter_callback=self.apply_filter, height=100)
        header_spacer = Widget(size_hint=(1, None), height=120)
        # self.header = Header(size_hint=(1, None), height=50)

        self.header_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.header_container.bind(minimum_height=self.header_container.setter('height'))

        # Add components to header_container
        # self.header_container.add_widget(self.header)
        self.header_container.add_widget(header_spacer)
        self.header_container.add_widget(self.search_widget)
        self.header_container.add_widget(self.filter_widget)

        screen_height = Window.height

        self.vendors_grid = GridLayout(cols=3, spacing='10dp', size_hint_y=None, height=screen_height)
        self.vendors_grid.bind(minimum_height=self.vendors_grid.setter('height'))

        vendors_screen = VendorsScreen()
        vendors_screen.size_hint_y = None
        vendors_screen.height = screen_height
        self.vendors_grid.add_widget(vendors_screen)

        spacer = Widget(size_hint=(1, None), height=100)
        spacer_bottom = Widget(size_hint=(1, None), height=45)

        # ✅ Add widgets to scrollable content
        # self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.header_container)
        self.content_layout.add_widget(self.vendors_grid)
        self.content_layout.add_widget(spacer_bottom)

        scroll_view = ScrollView(size_hint=(1, 1), bar_width=20)
        scroll_view.add_widget(self.content_layout)

        self.add_widget(scroll_view)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        # Position header at the top using absolute coordinates
        header.pos_hint = {'top': 1}
        self.add_widget(header)

        # ✅ Fixed bottom navbar
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}
        self.add_widget(nav_bar)

        # # Create a dropdown for account actions
        # # Get the app instance to access account_button
        # app = App.get_running_app()
        # self.user_info_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(250, 100), pos_hint={'right': 1, 'top': 1})
        # self.user_info_layout.add_widget(app.account_button)
        # self.add_widget(self.user_info_layout)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()


    def apply_filter(self, location=None, service=None, price_range=None):
        # print(f"Applying filter with location={location}, service={service}, price_range={price_range}")

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