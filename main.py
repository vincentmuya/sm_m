from vendor_details import VendorDetailsScreen
from landing_page import LandingPage
from vendors import VendorsScreen
from vendors_by_service import VendorsByServiceScreen
from filtered_vendors import FilteredVendorsScreen
from search_results import SearchResultsScreen
from location_vendors import LocationVendorsScreen
from service_vendors import ServiceVendorsScreen
from login_screen import LoginScreen
from register_screen import RegisterScreen
from profile import ProfileScreen

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
import requests
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivymd.toast import toast


class MyApp(MDApp):

    def get_authenticated_data(self, endpoint):
        token = self.user_data.get("token", "")

        if not token:
            print("❌ No token found. User not logged in.")
            return None

        headers = {"Authorization": f"Token {token}"}
        url = f"http://localhost:8000/{endpoint}/"

        print(f"📡 Sending request to: {url}")

        try:
            response = requests.get(url, headers=headers)
            print(f"📡 Status Code: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch data. Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            return None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}  # Stores logged-in user info
        self.token = None
        self.account_dropdown = DropDown()
        self.account_button = Button(text="Account", size_hint=(None, None), size=(150, 40))
        self.account_button.bind(on_release=self.account_dropdown.open)

    def logout_user(self, instance=None):
        """Clears user session and redirects to landing_page screen."""
        # print("🔴 Logging out user...")

        # Clear user session data
        self.user_data = {}
        self.token = None
        toast("Logged Out Successful.")
        # Redirect to login screen
        self.root.current = "login_screen"

        self.user_data.pop("username", None)  # Remove user session
        self.update_account_dropdown()
        # print("✅ Successfully logged out. Redirecting to login screen.")

    def update_account_dropdown(self):
        """Update dropdown contents based on user login state."""
        self.account_dropdown.clear_widgets()

        if "username" in self.user_data:
            username = self.user_data["username"]
            self.account_button.text = "Account"

            # Logged-in user label
            user_label = Button(text=f"Logged in as {username}", size_hint_y=None, height=40)
            self.account_dropdown.add_widget(user_label)

            # Profile button
            profile_btn = Button(text="Profile", size_hint_y=None, height=40)
            profile_btn.bind(on_release=self.user_profile)
            self.account_dropdown.add_widget(profile_btn)

            # Logout button
            logout_btn = Button(text="Logout", size_hint_y=None, height=40)
            logout_btn.bind(on_release=self.logout_user)
            self.account_dropdown.add_widget(logout_btn)

        else:
            self.account_button.text = "Account"

            # Login button
            login_btn = Button(text="Login", size_hint_y=None, height=40)
            login_btn.bind(on_release=self.go_to_login)
            self.account_dropdown.add_widget(login_btn)

            # Register button
            register_btn = Button(text="Register", size_hint_y=None, height=40)
            register_btn.bind(on_release=self.go_to_register)
            self.account_dropdown.add_widget(register_btn)

    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Load stored user data
        store = JsonStore("user_session.json")
        if store.exists("user"):
            self.user_data = store.get("user")
            # print(f"User session loaded: {self.user_data}")
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

        # Create the RegisterScreen instance and add it to the ScreenManager
        register_screen = RegisterScreen(name='register_screen')
        screen_manager.add_widget(register_screen)

        # Create the ProfileScreen instance and add it to the ScreenManager
        profile_screen = ProfileScreen(name='profile_screen')
        screen_manager.add_widget(profile_screen)

        return screen_manager

    def go_to_login(self, instance):
        """Redirect to the Login screen."""
        app = App.get_running_app()
        app.root.current = "login_screen"

    def go_to_register(self, instance):
        """Redirect to the Register screen."""
        app = App.get_running_app()
        app.root.current = "register_screen"

    def user_profile(self, instance):
        """Fetch and print the user's profile details."""
        app = App.get_running_app()

        # 🔍 Print token before making a request
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        # 🔍 Debugging: Ensure function is being called
        print("📡 Calling get_authenticated_data()...")

        # ✅ Use the reusable function to fetch profile data
        profile_data = app.get_authenticated_data("api_profile")

        if profile_data:
            print(f"✅ User ID: {profile_data['user']}, Profile ID: {profile_data['id']}")

            app.root.current = "profile_screen"
        else:
            print("❌ Failed to fetch profile.")


if __name__ == '__main__':
    MyApp().run()
