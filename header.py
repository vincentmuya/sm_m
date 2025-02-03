from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.toolbar import MDTopAppBar
from kivy.utils import get_color_from_hex  # For hex color support
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
import requests
from functools import partial


class Header(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a top bar with a hamburger menu button
        self.top_bar = MDTopAppBar(
            title="Sherehe Mall.\nCelebrations Made Easy",
            left_action_items=[["menu", lambda x: self.toggle_drawer()]],
            elevation=5,
            pos_hint={"top": 1}  # Keep it at the top
        )
        self.add_widget(self.top_bar)

        # Create Navigation Drawer with a background color and move it up
        self.nav_drawer = MDNavigationDrawer(
            pos_hint={"x": -1, "top": -5},  # Moves the drawer up
            size_hint_y=1,  # Adjusts height
            md_bg_color=get_color_from_hex("#FFFFFF")  # White background
        )

        self.nav_list = MDList()
        self.nav_list.md_bg_color = get_color_from_hex("#F0F0F0")  # Light gray background for contrast

        # Add menu items
        self.nav_list.add_widget(OneLineListItem(text="Home", on_release=lambda x: self.navigate_to("landing_page")))
        self.nav_list.add_widget(
            OneLineListItem(text="Vendors", on_release=lambda x: self.navigate_to("vendors_screen")))
        self.nav_list.add_widget(OneLineListItem(text="My Bookings", on_release=lambda x: self.navigate_to("bookings")))
        self.nav_list.add_widget(OneLineListItem(text="Profile", on_release=lambda x: self.navigate_to("profile")))

        # Location Dropdown Container
        self.location_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=40)
        self.location_button = MDRaisedButton(
            text='Location', on_release=self.ensure_location_menu_open
        )
        self.location_layout.add_widget(self.location_button)
        self.nav_list.add_widget(self.location_layout)

        # Service Dropdown Container
        self.service_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=40)
        self.service_button = MDRaisedButton(
            text='Service', on_release=self.ensure_service_menu_open
        )
        self.service_layout.add_widget(self.service_button)
        self.nav_list.add_widget(self.service_layout)

        # Now create the dropdown menus after buttons are defined
        self.location_menu = MDDropdownMenu(
            caller=self.location_button,
            items=[],
            width_mult=4
        )
        self.service_menu = MDDropdownMenu(
            caller=self.service_button,
            items=[],
            width_mult=4
        )

        self.populate_location_dropdown()
        self.populate_service_dropdown()

        self.nav_drawer.add_widget(self.nav_list)

        # Ensure drawer overlays everything
        self.nav_drawer.elevation = 10  # Ensures it's above other widgets
        self.add_widget(self.nav_drawer)

    def toggle_drawer(self):
        """Opens or closes the drawer when the menu button is clicked."""
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")
            self.nav_drawer.pos_hint = {"x": -0.02}  # Move into view

    def ensure_location_menu_open(self, *args):
        if not self.location_menu.items:
            self.populate_location_dropdown()
        self.location_menu.open()

    def ensure_service_menu_open(self, *args):
        if not self.service_menu.items:
            self.populate_service_dropdown()
        self.service_menu.open()

    def populate_location_dropdown(self):
        api_url = 'http://localhost:8000/api/locations/'
        response = requests.get(api_url)

        if response.status_code == 200:
            locations = response.json()
            self.location_menu.items = [
                {
                    "text": location['location'],
                    "viewclass": "OneLineListItem",
                    "on_release": partial(self.set_location, location['location'])
                }
                for location in locations
            ]
        else:
            print(f"Failed to retrieve locations. Status code: {response.status_code}")

    def populate_service_dropdown(self):
        api_url = 'http://localhost:8000/api/services/'
        response = requests.get(api_url)

        if response.status_code == 200:
            services = response.json()
            self.service_menu.items = [
                {
                    "text": service['service'],
                    "viewclass": "OneLineListItem",
                    "on_release": partial(self.set_service, service['service'])
                }
                for service in services
            ]
        else:
            print(f"Failed to retrieve services. Status code: {response.status_code}")

    def set_location(self, location):
        """Sets selected location from dropdown."""
        self.location_button.text = location
        self.location_menu.dismiss()

    def set_service(self, service):
        """Sets selected service from dropdown."""
        self.service_button.text = service
        self.service_menu.dismiss()

    def navigate_to(self, screen_name):
        """Handles navigation from the drawer."""
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = screen_name
        self.nav_drawer.set_state("close")  # Close the drawer after navigation
