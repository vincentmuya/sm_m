from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerItem
from kivy.app import App

class NavigationDrawer(MDNavigationDrawer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_ui()

    def init_ui(self):
        """Initialize the drawer UI with menu options."""
        self.box = BoxLayout(orientation='vertical', padding="10dp", spacing="10dp")

        # Example menu items
        self.add_menu_item("Home", "home", "landing_page")
        self.add_menu_item("Vendors", "store", "vendors_screen")
        self.add_menu_item("Filtered Vendors", "filter", "filtered_vendors")
        self.add_menu_item("Search Results", "magnify", "search_results")

        self.add_widget(self.box)

    def add_menu_item(self, text, icon, screen_name):
        """Helper function to add menu items to the drawer."""
        menu_item = MDNavigationDrawerItem(
            text=text,
            icon=icon,
            on_release=lambda _: self.navigate_to(screen_name)
        )
        self.box.add_widget(menu_item)

    def navigate_to(self, screen_name):
        """Switch to the selected screen and close drawer."""
        app = App.get_running_app()
        self.set_state("close")  # Close the drawer
