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
from favorites import FavoritesScreen
from bookings import BookingsScreen

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
import requests
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivymd.toast import toast
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty
from datetime import date
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivymd.uix.pickers import MDDatePicker

class MyPopup(ModalView):
    menu_image = StringProperty('https://www.shutterstock.com/image-vector/image-icon-600nw-211642900.jpg') # Place holder

    def __init__(self, menu_image, **kwargs):
        super().__init__(**kwargs)
        self.menu_image = menu_image


class BookVendorPopup(ModalView):
    def __init__(self, vendor_id, user_id, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = False
        self.vendor_id = vendor_id
        self.user_id = user_id
        self.selected_date = None

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        layout.add_widget(Label(text="Book Vendor", bold=True, size_hint_y=None, height=30))

        # Date Picker
        self.date_label = Label(text="Select Date", size_hint_y=None, height=30)
        layout.add_widget(self.date_label)
        self.date_button = Button(text="Pick a Date", on_release=self.open_date_picker)
        layout.add_widget(self.date_button)

        # Comment Input
        self.comment_input = TextInput(hint_text="Enter your comment", multiline=True, size_hint_y=None, height=80)
        layout.add_widget(self.comment_input)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        submit_button = Button(text="Submit", on_release=self.submit_booking)
        cancel_button = Button(text="Cancel", on_release=self.dismiss)
        button_layout.add_widget(submit_button)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def open_date_picker(self, instance):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.on_date_selected)
        date_picker.open()

    def on_date_selected(self, instance, value, date_range):
        self.selected_date = value.strftime("%Y-%m-%d")
        self.date_label.text = f"Selected Date: {self.selected_date}"

    def submit_booking(self, instance):
        app = App.get_running_app()
        # 🔍 Get the authentication token
        token = app.user_data.get("token", "")
        # print(f"🔍 Token being used: {token}")

        if not token:
            # print("❌ User not authenticated.")
            toast("❌ User not authenticated.")

            return

        # ✅ Fetch user data to get user ID
        print("📡 Calling get_authenticated_data() to fetch user ID...")
        user_data = app.get_authenticated_data(f"api/user")

        if not user_data or "id" not in user_data:
            # print("❌ Failed to fetch user data.")
            toast("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]  # Extract the user ID
        # print(f"✅ Authenticated user ID: {user_id}")

        if not self.selected_date:
            self.date_label.text = "[color=ff0000]Please select a date![/color]"
            return

        booking_data = {
            "vendor_id": self.vendor_id,
            "user_id": user_id,
            "date": self.selected_date,
            "comment": self.comment_input.text,
        }
        print("Booking data:", booking_data)

        # API Endpoint for Booking
        api_url = "http://localhost:8000/api/bookings/"

        response = requests.post(api_url, json=booking_data)

        if response.status_code == 201:
            print("✅ Booking Successful!")
            toast("✅ Booking Successful!")
            self.dismiss()
        else:
            print("❌ Booking Failed:", response.text)
            toast("❌ Booking Failed:")


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

            # Favorite button
            favorite_btn = Button(text="Favorites", size_hint_y=None, height=40)
            favorite_btn.bind(on_release=self.user_favorites)
            self.account_dropdown.add_widget(favorite_btn)

            # Bookings button
            bookings_btn = Button(text="Bookings", size_hint_y=None, height=40)
            bookings_btn.bind(on_release=self.user_bookings)
            self.account_dropdown.add_widget(bookings_btn)

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

        # Create the FavoritesScreen instance and add it to the ScreenManager
        favorites_screen = FavoritesScreen(name='favorites_screen')
        screen_manager.add_widget(favorites_screen)

        # Create the BookingsScreen instance and add it to the ScreenManager
        bookings_screen = BookingsScreen(name='bookings_screen')
        screen_manager.add_widget(bookings_screen)

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
        """Fetch and print the user's profile details and vendor count."""
        app = App.get_running_app()

        # 🔍 Print token before making a request
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        print("📡 Calling get_authenticated_data()...")

        # ✅ Fetch the user profile data
        profile_data = app.get_authenticated_data("api_profile")

        if profile_data:
            user_id = profile_data.get("user")  # ✅ Ensure correct key usage
            print(f"✅ User ID: {user_id}, Profile ID: {profile_data['id']}")

            # ✅ Fetch the username using the user_id
            user_data = app.get_authenticated_data(f"api/user")

            if user_data and "username" in user_data:
                username = user_data["username"]
                print(f"👤 Username: {username}")
            else:
                print("❌ Failed to fetch username.")

            print("📡 Fetching vendor count...")

            # ✅ Fetch the vendor list using the correct endpoint
            vendors_data = app.get_authenticated_data("api/vendor")

            if vendors_data:
                # ✅ Ensure correct key usage (change "user_id" to "user")
                user_vendors = [vendor for vendor in vendors_data if vendor.get("user") == user_id]
                vendor_count = len(user_vendors)
                print(f"📊 Total Vendors Posted: {vendor_count}")
            else:
                print("❌ Failed to fetch vendors.")

            # Pass the vendor data to the profile screen
            profile_vendors_screen = app.root.get_screen('profile_screen')
            profile_vendors_screen.load_profile_vendors(user_vendors, username)
            app.root.current = "profile_screen"
        else:
            print("❌ Failed to fetch profile.")

    def user_favorites(self, instance):
        """Fetch and print the user's favorites."""
        app = App.get_running_app()
        # 🔍 Get the authentication token
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        # ✅ Fetch user data to get user ID
        # print("📡 Calling get_authenticated_data() to fetch user ID...")
        user_data = app.get_authenticated_data(f"api/user")

        if not user_data or "id" not in user_data:
            print("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]  # Extract the user ID
        # print(f"✅ Authenticated user ID: {user_id}")

        # 🔗 API URL for fetching favorites
        url = f"http://localhost:8000/api/favorites/"

        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }

        try:
            # print(f"📡 Sending request to: {url}")
            response = requests.get(url, headers=headers)

            # print(f"📡 Status Code: {response.status_code}")

            if response.status_code == 200:
                favorites = response.json()
                # print(f"📡 API Response: {favorites}")

                # Filter favorites for the current user
                user_favorites = [fav for fav in favorites if fav["user_id"] == user_id]

                if user_favorites:
                    print("✅ User's Favorited Vendors:")
                    for fav in user_favorites:
                        print(f"➡ Vendor ID: {fav['vendor_id']}")
                else:
                    print("ℹ No favorites found for this user.")

            else:
                print(f"❌ Error fetching favorites: {response.text}")

        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")

        # Pass the favorite Vendors to the favorite screen
        favorite_vendors_screen = app.root.get_screen('favorites_screen')
        favorite_vendors_screen.load_favorite_vendors(user_favorites)
        # Navigate to favorites screen
        app.root.current = "favorites_screen"

    def user_bookings(self, instance):
        """Redirect to the Bookings screen."""
        app = App.get_running_app()
        app.root.current = "bookings_screen"

    def show_menu_popup(self, menu_image):
        popup = MyPopup(menu_image=menu_image)
        popup.open()

    def show_book_popup(self, vendor_id, user_id):
        popup = BookVendorPopup(vendor_id, user_id)
        popup.open()

if __name__ == '__main__':
    MyApp().run()
