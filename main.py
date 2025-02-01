from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton
from navigation_drawer import NavigationDrawer
from vendor_details import VendorDetailsScreen
from landing_page import LandingPage
from vendors import VendorsScreen
from vendors_by_service import VendorsByServiceScreen
from filtered_vendors import FilteredVendorsScreen
from search_results import SearchResultsScreen


class MyApp(MDApp):
    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Create a BoxLayout for main UI (including nav drawer)
        self.main_layout = BoxLayout(orientation='vertical')

        # Add a top navigation bar
        self.top_bar = BoxLayout(size_hint_y=0.1)
        self.menu_button = MDIconButton(icon="menu", on_release=self.open_nav_drawer)
        self.top_bar.add_widget(self.menu_button)

        # Add navigation drawer
        self.nav_drawer = NavigationDrawer()

        # Create and add the landing page screen
        landing_page_screen = Screen(name='landing_page')
        landing_page = LandingPage()
        landing_page_screen.add_widget(landing_page)
        screen_manager.add_widget(landing_page_screen)

        # Create the VendorDetailsScreen instance and add it to the ScreenManager
        vendor_details_screen = VendorDetailsScreen(name='vendor_details')
        screen_manager.add_widget(vendor_details_screen)

        # Create a screen for vendors listing
        vendors_screen = Screen(name='vendors_screen')
        vendors = VendorsScreen()
        vendors_screen.add_widget(vendors)
        screen_manager.add_widget(vendors_screen)

        # Create the VendorsByServiceScreen instance and add it to the ScreenManager
        vendors_by_service_screen = VendorsByServiceScreen(name='vendors_by_service')
        screen_manager.add_widget(vendors_by_service_screen)

        # Create the FilteredVendorsScreen instance and add it to the ScreenManager
        filtered_vendors = FilteredVendorsScreen(name='filtered_vendors')
        screen_manager.add_widget(filtered_vendors)

        # Create the SearchResultsScreen instance and add it to the ScreenManager
        search_results = SearchResultsScreen(name='search_results')
        screen_manager.add_widget(search_results)

        # Add screen manager to layout
        self.main_layout.add_widget(self.top_bar)
        self.main_layout.add_widget(screen_manager)

        # Add navigation drawer separately
        self.main_layout.add_widget(self.nav_drawer)

        return self.main_layout

    def open_nav_drawer(self, instance):
        """Opens the navigation drawer."""
        self.nav_drawer.set_state("open")


if __name__ == '__main__':
    MyApp().run()
