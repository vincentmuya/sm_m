from navbar import Navbar
from header import Header
from vendors import VendorsCard
from kivy.uix.widget import Widget
from filter_widget import Filter
from search_widget import SearchWidget

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import AsyncImage
from kivymd.uix.card import MDCard
from kivy.uix.popup import Popup
from kivymd.toast import toast
from kivy.uix.textinput import TextInput
import json

Builder.load_file('booking_details.kv')

class BookingDetailsScreen(Screen):
    """A screen to display BookingDetails."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        # Add other screens (VendorsScreen) to the content layout
        self.booking_details_labels = GridLayout(cols=1, size_hint_y=None, spacing='10dp')

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=30)
        bottom_spacer = Widget(size_hint=(1, None), height=650)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.booking_details_labels)
        self.content_layout.add_widget(bottom_spacer)

        # Create the ScrollView and add the content_layout inside it
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=20)
        scroll_view.add_widget(self.content_layout)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        header.pos_hint = {'x': 0, 'y': 0.95}
        # Add ScrollView and navbar to the FloatLayout
        self.add_widget(scroll_view)  # Add ScrollView with content on top
        self.add_widget(header)

        # Create and add the navbar, fixed at the bottom of the screen
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}
        # Add ScrollView and navbar to the FloatLayout
        self.add_widget(nav_bar)

        # ✅ Use a proxy button instead of moving the original button
        app = App.get_running_app()
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(150, 40),pos=(650, 560))
        # ✅ Create a proxy button
        self.account_proxy_button = Button(text=app.account_button.text)
        # ✅ Open dropdown manually when proxy button is clicked
        self.account_proxy_button.bind(on_release=self.open_account_dropdown)
        # ✅ Add proxy button instead of the real one
        self.user_info_layout.add_widget(self.account_proxy_button)
        self.add_widget(self.user_info_layout)

    def open_account_dropdown(self, instance):
        """Manually opens the account dropdown."""
        app = App.get_running_app()
        #Ensure dropdown is updated before opening
        app.update_account_dropdown()
        #Open dropdown manually
        app.account_dropdown.open(instance)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()
        #Ensure the proxy button always has updated text
        self.account_proxy_button.text = app.account_button.text

    def load_booking_details(self, booking):
        """Loads and displays the booking details inside a Card widget."""
        print(f"📜 Booking Details Loaded: {booking}")

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot display bookings.")
            return

        current_user_id = user_data["id"]
        print(f"🔍 Current User ID: {current_user_id}")

        # Clear previous details before adding new ones
        self.booking_details_labels.clear_widgets()

        # Create a card layout to hold booking details
        booking_details_card = MDCard(size_hint_y=None, height=200)  # Assuming CardView or a similar widget exists

        # Create a box layout inside the card
        card_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Add booking details inside the card
        booking_vendor = Button(text=f"[b]Vendor Being Booked:[/b] {booking['vendor']['institution_name']}", markup=True, color=(0, 0, 0, 1))
        booking_vendor.bind(on_release=lambda instance: self.booking_vendor_details(booking["vendor"]["id"], booking["vendor"]["slug"]))
        card_layout.add_widget(booking_vendor)

        card_layout.add_widget(Label(text=f"[b]Booking Date:[/b] {booking['date']}", markup=True, color=(0, 0, 0, 1)))
        card_layout.add_widget(Label(text=f"[b]Booking Comment:[/b] {booking['comment']}", markup=True, color=(0, 0, 0, 1)))
        card_layout.add_widget(Label(text=f"[b]Booking Status:[/b] {booking['booking_status']}", markup=True, color=(0, 0, 0, 1)))

        if booking["user_id"] == current_user_id:
            # Add other screens (Booking Details buttons) to the content layout
            booking_details_info = GridLayout(cols=3, size_hint_y=None, height=40, spacing='10dp')

            update_booking = Button(text="Update Booking", markup=True, color=(0, 0, 0, 1))
            app = App.get_running_app()
            update_booking.bind(on_release=lambda instance: app.show_update_popup(booking))

            delete_booking_button = Button(text="Delete Booking", markup=True, color=(0, 0, 0, 1))
            delete_booking_button.bind(on_release=lambda instance: self.show_delete_confirmation(booking.get("id")))

            send_message = Button(text="Send Message", markup=True, color=(0, 0, 0, 1))
            send_message.bind(
                on_release=lambda instance: self.show_message_vendor(booking.get("id"), booking.get("user_id"),
                                                                     booking.get("vendor_id"),
                                                                     booking.get("vendor", {}).get("user")))

            booking_details_info.add_widget(update_booking)
            booking_details_info.add_widget(delete_booking_button)
            booking_details_info.add_widget(send_message)

            card_layout.add_widget(booking_details_info)

        if booking["vendor"]["user"] == current_user_id:

            # Add other screens (Booking Details buttons) to the content layout
            booking_details_info = GridLayout(cols=3, size_hint_y=None, height=40, spacing='10dp')

            approve_booking_button = Button(text="Approve Booking", markup=True, color=(0, 0, 0, 1))
            approve_booking_button.bind(on_release=lambda instance: self.show_approve_confirmation(booking.get("id")))

            reject_booking_button = Button(text="Reject Booking", markup=True, color=(0, 0, 0, 1))
            reject_booking_button.bind(on_release=lambda instance: self.show_reject_booking(booking.get("id")))

            send_message = Button(text="Send Message", markup=True, color=(0, 0, 0, 1))
            send_message.bind(
                on_release=lambda instance: self.show_message_vendor(booking.get("id"), booking.get("user_id"),
                                                                     booking.get("vendor_id"),
                                                                     booking.get("vendor", {}).get("user")))

            booking_details_info.add_widget(approve_booking_button)
            booking_details_info.add_widget(reject_booking_button)
            booking_details_info.add_widget(send_message)

            card_layout.add_widget(booking_details_info)


        # Add the layout to the card
        booking_details_card.add_widget(card_layout)

        # Add the card to the GridLayout
        self.booking_details_labels.add_widget(booking_details_card)

    def booking_vendor_details(self, vendor_id, slug, *args):
        print(f"Fetching details for Vendor ID: {vendor_id}, Slug: {slug}")

        api_url = f"http://localhost:8000/api/vendor/{vendor_id}/{slug}/"
        response = requests.get(api_url)

        if response.status_code == 200:
            vendor_details = response.json()

            app = App.get_running_app()
            vendor_details_screen = app.root.get_screen('vendor_details')
            vendor_details_screen.load_details(vendor_details)

            app.root.transition = SlideTransition(direction='left')
            app.root.current = 'vendor_details'
        else:
            print("❌ Failed to fetch vendor details.")

    def show_delete_confirmation(self, booking_id):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        # Popup Layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Message
        message = Label(text="Are you sure you want to delete this booking?", size_hint=(1, 0.5))

        # Buttons
        confirm_button = Button(text="Yes, Delete", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        # Create popup
        popup = Popup(title="Confirm Deletion", content=layout, size_hint=(0.7, 0.4))

        # Bind buttons
        confirm_button.bind(on_release=lambda instance: self.confirm_delete(booking_id, popup))
        cancel_button.bind(on_release=popup.dismiss)

        # Add widgets to layout
        layout.add_widget(message)
        layout.add_widget(confirm_button)
        layout.add_widget(cancel_button)

        # Open popup
        popup.open()

    def confirm_delete(self, booking_id, popup):
        popup.dismiss()  # Close the popup before deleting
        self.delete_booking(booking_id)

    def delete_booking(self, booking_id):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        api_url = f"http://localhost:8000/api/bookings/{booking_id}/"
        print(f"📡 Sending DELETE request to: {api_url}")

        try:
            response = requests.delete(api_url)
            if response.status_code == 204:
                print("✅ Booking deleted successfully.")
                # Optionally refresh UI or remove the booking from the list
            else:
                print(f"❌ Failed to delete booking. Status Code: {response.status_code}")
                print("Response:", response.text)
        except requests.exceptions.RequestException as e:
            print("❌ Request failed:", e)

    def show_approve_confirmation(self, booking_id):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        # Popup Layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Message
        message = Label(text="Are you sure you want to book this booking?", size_hint=(1, 0.5))

        # Buttons
        approve_button = Button(text="Yes, Approve", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        # Create popup
        popup = Popup(title="Confirm Booking", content=layout, size_hint=(0.7, 0.4))

        # Bind buttons
        approve_button.bind(on_release=lambda instance: self.confirm_approve(booking_id, popup))
        cancel_button.bind(on_release=popup.dismiss)

        # Add widgets to layout
        layout.add_widget(message)
        layout.add_widget(approve_button)
        layout.add_widget(cancel_button)

        # Open popup
        popup.open()

    def confirm_approve(self, booking_id, popup):
        popup.dismiss()  # Close the popup before deleting
        self.approve_booking(booking_id)

    def approve_booking(self, booking_id):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        api_url = f"http://localhost:8000/api/bookings/{booking_id}/"
        data = {"booking_status": "approved"}  # ✅ Update the status

        print(f"📡 Sending PUT request to: {api_url} with data: {data}")

        try:
            response = requests.put(api_url, json=data)  # Send PUT request
            if response.status_code == 200:
                print("Booking approved successfully.")
                toast("Booking approved successfully.")
                app = App.get_running_app()
                app.root.transition = SlideTransition(direction='left')
                app.root.current = 'bookings_screen'
            else:
                print(f"❌ Failed to approve booking. Status Code: {response.status_code}")
                print("Response:", response.text)
        except requests.exceptions.RequestException as e:
            print("❌ Request failed:", e)

    def show_reject_booking(self, booking_id):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        # Popup Layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Message
        message = Label(text="Enter Rejection Comment", size_hint=(1, 0.5))
        textinput = TextInput(text='', multiline=True)  # Input field for comment

        # Buttons
        reject_button = Button(text="Yes, Reject", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        # Create popup
        popup = Popup(title="Confirm Booking Rejection", content=layout, size_hint=(0.7, 0.4))

        # Bind buttons (Pass rejection comment when rejecting)
        reject_button.bind(on_release=lambda instance: self.confirm_reject(booking_id, textinput.text, popup))
        cancel_button.bind(on_release=popup.dismiss)

        # Add widgets to layout
        layout.add_widget(message)
        layout.add_widget(textinput)
        layout.add_widget(reject_button)
        layout.add_widget(cancel_button)

        # Open popup
        popup.open()

    def confirm_reject(self, booking_id, rejection_comment, popup):
        popup.dismiss()  # Close the popup before rejecting
        self.booking_reject(booking_id, rejection_comment)

    def booking_reject(self, booking_id, rejection_comment):
        if not booking_id:
            print("❌ Booking ID is missing!")
            return

        api_url = f"http://localhost:8000/api/bookings/{booking_id}/"
        print(f"📡 Sending PUT request to: {api_url}")

        data = {
            "booking_status": "rejected",
            "rejection_booking_comment": rejection_comment  # Pass rejection comment
        }

        try:
            response = requests.put(api_url, json=data)
            if response.status_code == 200:
                print("Booking rejected successfully.")
                toast("Booking rejected successfully.")

                app = App.get_running_app()
                app.root.transition = SlideTransition(direction='left')
                app.root.current = 'bookings_screen'

            else:
                print(f"❌ Failed to reject booking. Status Code: {response.status_code}")
                print("Response:", response.text)
        except requests.exceptions.RequestException as e:
            print("❌ Request failed:", e)

    def show_message_vendor(self, booking_id, user_id, vendor_id, vendor_user_id):
        """Display popup for messaging the vendor."""

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        message = Label(text="Message Vendor", size_hint=(1, 0.5))
        textinput = TextInput(text='', multiline=True)

        send_message_button = Button(text="Send Message", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        popup = Popup(title="Message Vendor", content=layout, size_hint=(0.7, 0.4))

        # Pass the booking details when binding the send message button
        send_message_button.bind(
            on_release=lambda instance: self.send_message(
                popup, textinput, booking_id, user_id, vendor_id, vendor_user_id
            )
        )
        cancel_button.bind(on_release=popup.dismiss)

        layout.add_widget(message)
        layout.add_widget(textinput)
        layout.add_widget(send_message_button)
        layout.add_widget(cancel_button)

        popup.open()

    def send_message(self, popup, textinput, booking_id, user_id, vendor_id, vendor_user_id):
        """Handle message sending."""
        message_text = textinput.text.strip()

        if message_text:
            popup.dismiss()
            self.message_vendor(message_text, booking_id, user_id, vendor_id, vendor_user_id)
        else:
            print("Message cannot be empty")

    def message_vendor(self, message_text, booking_id, user_id, vendor_id, vendor_user_id):
        """Send a message to the vendor."""
        print("Message Vendor Called")
        app = App.get_running_app()

        # Fetch authenticated user data
        user_data = app.get_authenticated_data("api/user")
        current_user_id = user_data.get("id")  # Use `.get()` to avoid KeyError

        if not current_user_id:
            print("❌ Error: User ID is missing")
            return

        # Step 1: Check if a conversation already exists
        conversation_id = self.get_conversation(current_user_id, vendor_id, vendor_user_id)

        if not conversation_id:
            # Step 2: Create a new conversation
            conversation_id = self.create_conversation(current_user_id, vendor_id, vendor_user_id)
            if not conversation_id:
                print("❌ Failed to create conversation")
                return

        # Step 3: Send the message
        message_sent = self.send_message_to_api(conversation_id, current_user_id, message_text, vendor_id, vendor_user_id)
        if message_sent:
            print("✅ Message sent successfully")
        else:
            print("❌ Failed to send message")

    def get_conversation(self, current_user_id, vendor_id, vendor_user_id):
        """Check if a conversation already exists between the user and vendor."""
        app = App.get_running_app()
        token = app.user_data.get("token", None)  # Get auth token

        if not token:
            print("❌ No auth token found. Cannot fetch conversations.")
            return None

        url = "http://localhost:8000/api/conversations/"
        headers = {"Authorization": f"Token {token}"}  # Use auth token

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                conversations = response.json()
                for convo in conversations:
                    if (
                            (convo["sender_id"] == current_user_id and convo["recipient_id_display"] == vendor_user_id and
                             convo["vendor_id_display"] == vendor_id) or
                            (convo["sender_id"] == vendor_user_id and convo["recipient_id_display"] == current_user_id and
                             convo["vendor_id_display"] == vendor_id)
                    ):
                        print(f"✅ Existing conversation found: {convo['id']}")
                        return convo["id"]  # ✅ Return existing conversation ID
            else:
                print(f"❌ Failed to fetch conversations. Response: {response.text}")

        except requests.RequestException as e:
            print(f"🚨 Error fetching conversations: {e}")

        return None  # No conversation found

    def create_conversation(self, user_id, vendor_id, vendor_user_id):
        """Create a new conversation with the vendor owner."""
        app = App.get_running_app()
        token = app.user_data.get("token", None)  # Get auth token

        if not token:
            print("❌ No auth token found. Cannot create conversation.")
            return None

        url = "http://localhost:8000/api/conversations/"
        payload = {
            "user_id": user_id,  # Ensure this matches your API field
            "recipient_id": vendor_user_id,  # Vendor owner
            "vendor_id": vendor_id  # Vendor being messaged
        }
        headers = {
            "Authorization": f"Token {token}",  # Use authentication
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response_json = response.json()  # Store response JSON

            print("📡 Response Status:", response.status_code)
            print("🔍 Response JSON:", response_json)  # Show server response

            if response.status_code == 201:
                return response_json.get("id")  # ✅ Return new conversation ID
            else:
                print(f"❌ Failed to create conversation. Response: {response.text}")

        except requests.RequestException as e:
            print(f"🚨 Error creating conversation: {e}")

        return None

    def send_message_to_api(self, conversation_id, current_user_id, message_text, vendor_id, vendor_user_id):
        """Send the message to the API."""
        url = f"http://localhost:8000/api/messages/"
        payload = {
            "conversation_id": conversation_id,
            "sender_id": current_user_id,
            "recipient_id": vendor_user_id,  # Vendor owner is the recipient
            "vendor_id": vendor_id,  # Vendor item being discussed
            "content": message_text
        }
        print("📦 Message Payload:", payload)
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        return response.status_code == 201  # Return True if message was sent successfully


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