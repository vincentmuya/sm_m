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
from booking_details import BookingDetailsScreen
from messages import MessagesScreen
from message_details import MessageDetailsScreen
from post_service import PostServiceScreen
from update_vendor import UpdateServiceScreen

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
    def __init__(self, vendor_id, user_id, booking_id=None, booking_date=None, booking_comment=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = False
        self.vendor_id = vendor_id
        self.user_id = user_id
        self.booking_id = booking_id  # Store booking ID (None if new)
        self.selected_date = booking_date  # Pre-fill date if updating

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        layout.add_widget(Label(text="Update Booking" if self.booking_id else "Book Vendor", bold=True, size_hint_y=None, height=30))

        # Date Picker
        self.date_label = Label(text=f"Selected Date: {self.selected_date}" if self.selected_date else "Select Date", size_hint_y=None, height=30)
        layout.add_widget(self.date_label)
        self.date_button = Button(text="Pick a Date", on_release=self.open_date_picker)
        layout.add_widget(self.date_button)

        # Comment Input (Pre-filled if updating)
        self.comment_input = TextInput(
            hint_text="Enter your comment",
            multiline=True,
            size_hint_y=None,
            height=80,
            text=booking_comment if booking_comment else ""  # Pre-fill if updating
        )
        layout.add_widget(self.comment_input)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        submit_button = Button(text="Update" if self.booking_id else "Submit", on_release=self.submit_booking)
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
        token = app.user_data.get("token", "")

        if not token:
            toast("❌ User not authenticated.")
            return

        user_data = app.get_authenticated_data("api/user")
        if not user_data or "id" not in user_data:
            toast("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]

        if not self.selected_date:
            self.date_label.text = "Please select a date!"
            return

        booking_data = {
            "vendor_id": self.vendor_id,
            "user_id": user_id,
            "date": self.selected_date,
            "comment": self.comment_input.text,
        }

        if self.booking_id:
            # If booking_id exists, send PUT request (Update)
            api_url = f"https://sherehemall.co.ke/api/bookings/{self.booking_id}/"
            response = requests.put(api_url, json=booking_data)
        else:
            # Otherwise, send POST request (Create)
            api_url = "https://sherehemall.co.ke/api/bookings/"
            response = requests.post(api_url, json=booking_data)

        if response.status_code in [200, 201]:
            toast("✅ Booking Updated!" if self.booking_id else "✅ Booking Successful!")
            self.dismiss()
        else:
            toast(f"❌ Booking Failed: {response.status_code}")


class MyApp(MDApp):

    def get_authenticated_data(self, endpoint):
        token = self.user_data.get("token", "")

        if not token:
            print("❌ No token found. User not logged in.")
            return None

        headers = {"Authorization": f"Token {token}"}
        url = f"https://sherehemall.co.ke/{endpoint}/"

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

            # Messages button
            messages_btn = Button(text="Messages", size_hint_y=None, height=40)
            messages_btn.bind(on_release=lambda instance: self.user_messages(instance))
            self.account_dropdown.add_widget(messages_btn)

            # Bookings button
            bookings_btn = Button(text="Bookings", size_hint_y=None, height=40)
            bookings_btn.bind(on_release=lambda instance: self.user_bookings(instance))
            self.account_dropdown.add_widget(bookings_btn)

            # Profile button
            profile_btn = Button(text="Profile", size_hint_y=None, height=40)
            profile_btn.bind(on_release=self.user_profile)
            self.account_dropdown.add_widget(profile_btn)

            # Post service button
            post_btn = Button(text="Post Service", size_hint_y=None, height=40)
            post_btn.bind(on_release=self.post_service)
            self.account_dropdown.add_widget(post_btn)

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

        # Create the BookingDetailsScreen instance and add it to the ScreenManager
        booking_details_screen = BookingDetailsScreen(name='booking_details')
        screen_manager.add_widget(booking_details_screen)

        # Create the MessagesScreen instance and add it to the ScreenManager
        messages_screen = MessagesScreen(name='messages_screen')
        screen_manager.add_widget(messages_screen)

        # Create the MessageDetailsScreen instance and add it to the ScreenManager
        message_details_screen = MessageDetailsScreen(name='message_details')
        screen_manager.add_widget(message_details_screen)

        # Create the PostServiceScreen instance and add it to the ScreenManager
        post_service_screen = PostServiceScreen(name='post_service_screen')
        screen_manager.add_widget(post_service_screen)

        # Create the UpdateServiceScreen instance and add it to the ScreenManager
        update_service_screen = UpdateServiceScreen(name='update_service_screen')
        screen_manager.add_widget(update_service_screen)

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
        url = f"https://sherehemall.co.ke/api/favorites/"

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
        """Fetch user bookings and pass them to the bookings screen."""
        app = App.get_running_app()

        # 🔍 Get the authentication token
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        # ✅ Fetch user data to get user ID
        user_data = app.get_authenticated_data(f"api/user")

        if not user_data or "id" not in user_data:
            print("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]  # Extract the user ID
        print(f"✅ Authenticated user ID: {user_id}")

        # API endpoint to fetch bookings
        api_url = f"https://sherehemall.co.ke/api/bookings/?user_id={user_id}"
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Raise an error for non-2xx responses

            # Store response in self.user_bookings
            self.user_bookings = response.json()

            # Print the stored bookings
            if self.user_bookings:
                print("📜 Stored User Bookings:")
                for booking in self.user_bookings:
                    print(
                        f"- Booking ID: {booking['id']}, Date: {booking['date']}, Vendor: {booking['vendor_id']}, Status: {booking['booking_status']}")
            else:
                print("🛑 No bookings found.")
                self.user_bookings = []  # Ensure it's an empty list if no bookings are found

            # ✅ Pass the bookings data to the bookings screen
            user_bookings_screen = app.root.get_screen('bookings_screen')
            user_bookings_screen.load_user_bookings(self.user_bookings)

            # 🚀 Switch to the bookings screen
            app.root.current = "bookings_screen"

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch bookings: {e}")
            self.user_bookings = []  # Reset to empty list in case of error

    def show_menu_popup(self, menu_image):
        popup = MyPopup(menu_image=menu_image)
        popup.open()

    def show_book_popup(self, vendor_id, user_id):
        popup = BookVendorPopup(vendor_id, user_id)
        popup.open()

    def show_update_popup(self, booking):
        vendor_id = booking["vendor"]["id"]
        user_id = booking["user_id"]
        booking_id = booking["id"]
        booking_date = booking["date"]
        booking_comment = booking["comment"]

        update_popup = BookVendorPopup(
            vendor_id=vendor_id,
            user_id=user_id,
            booking_id=booking_id,
            booking_date=booking_date,
            booking_comment=booking_comment
        )
        update_popup.open()

    def user_messages(self, *args):
        """Fetch user Messages and pass them to the messages screen."""
        app = App.get_running_app()

        # 🔍 Get the authentication token
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        # ✅ Fetch user data to get user ID
        user_data = app.get_authenticated_data(f"api/user")

        if not user_data or "id" not in user_data:
            print("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]  # Extract the user ID
        print(f"✅ Authenticated user ID: {user_id}")

        # API endpoint to fetch conversations
        api_url = f"https://sherehemall.co.ke/api/conversations/?user_id={user_id}"
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Raise an error for non-2xx responses

            # Store response in self.user_conversations
            self.user_conversations = response.json()

            # Print the stored messages
            if self.user_conversations:
                print("📜 Stored User Conversations:")
                for convo in self.user_conversations:
                    print(
                        f"- Conversation ID: {convo['id']}, Vendor: {convo['vendor_id_display']}")
            else:
                print("🛑 No Conversations found.")
                self.user_conversations = []  # Ensure it's an empty list if no conversations are found

            # ✅ Pass the conversation data to the conversation screen
            user_messages_screen = app.root.get_screen('messages_screen')
            user_messages_screen.load_user_messages(self.user_conversations)

            # 🚀 Switch to the bookings screen
            app.root.current = "messages_screen"

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch bookings: {e}")
            self.user_conversations = []  # Reset to empty list in case of error

    def post_service(self, *args):
        app = App.get_running_app()

        # 🔍 Get the authentication token
        token = app.user_data.get("token", "")
        print(f"🔍 Token being used: {token}")

        if not token:
            print("❌ User not authenticated.")
            return

        # ✅ Fetch user data to get user ID
        user_data = app.get_authenticated_data(f"api/user")

        if not user_data or "id" not in user_data:
            print("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]  # Extract the user ID
        print(f"✅ Authenticated user ID: {user_id}")

        app.root.current = "post_service_screen"
        pass

if __name__ == '__main__':
    MyApp().run()
