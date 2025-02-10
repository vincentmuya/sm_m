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

class LandingPage(Screen):  # Change from FloatLayout to Screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super(LandingPage, self).__init__(**kwargs)

        # Set up the main layout
        self.layout = FloatLayout()

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

        # Initialize and add FilteredVendorsScreen
        self.filtered_vendors_screen = FilteredVendorsScreen()
        self.content_layout.add_widget(self.filtered_vendors_screen)

        # Add other screens (VendorsScreen) to the content layout
        vendors = self.wrap_screen(VendorsScreen(), height=400)

        # Spacer widget to add space after the header
        spacer = Widget(size_hint=(1, None), height=45)

        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(vendors)

        # Create the ScrollView and add the content_layout inside it
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=20)
        scroll_view.add_widget(self.content_layout)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        header.pos_hint = {'x': 0, 'y': 0.95}
        # Add ScrollView and header to the FloatLayout
        self.layout.add_widget(scroll_view)  # Add ScrollView with content on top
        self.layout.add_widget(header)  # Add navbar at the top

        # Create and add the navbar, fixed at the bottom of the screen
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}
        # Add Nav to the Screen widget
        self.layout.add_widget(nav_bar)

        # User Info Label (default text: "Not logged in")
        self.user_label = Label(text="Not logged in", size_hint=(None, None), pos=(90, 530))
        self.layout.add_widget(self.user_label)
        # Add everything to the Screen widget
        self.add_widget(self.layout)

        # Create Logout Button
        self.logout_button = Button(text="Logout", size_hint=(None, None), pos=(120, 530))
        self.logout_button.bind(on_release=self.logout)

        self.add_widget(self.logout_button)

    def on_pre_enter(self):
        """Update the label when the screen is entered."""
        print("🚀 LandingPage on_pre_enter triggered")  # Debug

        app = App.get_running_app()

        if "username" in app.user_data:
            username = app.user_data["username"]
            self.user_label.text = f"Logged in as: {username}"
            print(f"User is logged in as: {username}")

            # Call the globally defined function to get authenticated data
            user_data = app.get_authenticated_data("protected_endpoint")

            if user_data:
                print(f"User Profile: {user_data}")  # Debugging print
                self.user_label.text = f"Hello, {user_data.get('username', 'User')}!"
            else:
                print("❌ Failed to fetch user profile.")
        else:
            self.user_label.text = "Not logged in"
            print("❌ Not logged in")

    def logout(self, instance):
        """Calls the globally defined logout function in MyApp."""
        app = App.get_running_app()
        app.logout_user()  # Calls logout function

    def wrap_screen(self, screen, height=None):
        """
        Wrap a screen in a layout with a specific height.
        """
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=height if height else screen.height)
        layout.add_widget(screen)
        return layout

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