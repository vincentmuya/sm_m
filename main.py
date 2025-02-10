from vendor_details import VendorDetailsScreen
from landing_page import LandingPage
from vendors import VendorsScreen
from vendors_by_service import VendorsByServiceScreen
from filtered_vendors import FilteredVendorsScreen
from search_results import SearchResultsScreen
from location_vendors import LocationVendorsScreen
from service_vendors import ServiceVendorsScreen
from login_screen import LoginScreen

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
import requests


class MyApp(MDApp):

    def get_authenticated_data(self, endpoint):
        """Make an authenticated request with a stored token."""
        token = self.user_data.get("token", "")

        if not token:
            print("❌ No token found. User not logged in.")
            return None

        headers = {"Authorization": f"Bearer {token}"}
        url = f"http://localhost:8000/api/{endpoint}/"

        try:
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✅ Authenticated Request Successful!")
                return response.json()
            else:
                print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}  # Stores logged-in user info
        self.token = None

    def logout_user(self):
        """Clears user session and redirects to landing_page screen."""
        print("🔴 Logging out user...")

        # Clear user session data
        self.user_data = {}
        self.token = None

        # Redirect to login screen
        self.root.current = "login_screen"

        print("✅ Successfully logged out. Redirecting to login screen.")

    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Load stored user data
        store = JsonStore("user_session.json")
        if store.exists("user"):
            self.user_data = store.get("user")
            print(f"User session loaded: {self.user_data}")
        else:
            print("No user session found.")

        # LandingPage is added as a Screen
        landing_page = LandingPage(name="landing_page")
        screen_manager.add_widget(landing_page)

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

        # Create the LocationVendorsScreen instance and add it to the ScreenManager
        location_vendors = LocationVendorsScreen(name='location_vendors')
        screen_manager.add_widget(location_vendors)

        # Create the LocationVendorsScreen instance and add it to the ScreenManager
        service_vendors = ServiceVendorsScreen(name='service_vendors')
        screen_manager.add_widget(service_vendors)

        # Create the LoginScreen instance and add it to the ScreenManager
        login_screen = LoginScreen(name='login_screen')
        screen_manager.add_widget(login_screen)

        return screen_manager


if __name__ == '__main__':
    MyApp().run()
