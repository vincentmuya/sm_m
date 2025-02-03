from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.toolbar import MDTopAppBar
from kivy.utils import get_color_from_hex  # For hex color support


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
            pos_hint={"x": -1, "top": -4},  # Moves the drawer up
            size_hint_y=0.8,  # Adjusts height
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

    def navigate_to(self, screen_name):
        """Handles navigation from the drawer."""
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = screen_name
        self.nav_drawer.set_state("close")  # Close the drawer after navigation
