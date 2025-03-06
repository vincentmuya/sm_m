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

Builder.load_file('message_details.kv')

class MessageDetailsScreen(Screen):
    """A screen to display MessageDetails."""

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

        # Add other screens (MessageScreen) to the content layout
        self.message_details_labels = GridLayout(cols=1, size_hint_y=None, spacing='10dp', height=1000)

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=30)
        bottom_spacer = Widget(size_hint=(1, None), height=650)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.message_details_labels)

        # Add the reply section (TextInput + Button)
        self.add_reply_section()

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
        # self.add_widget(nav_bar)

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

    def load_message_details(self, messages_data):
        """Loads and displays the message details inside a Card widget."""
        print(f"📜 Message Details Loaded: {messages_data}")

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot display messages.")
            return

        self.current_user_id = user_data["id"]  # Save sender ID
        print(f"🔍 Current User ID: {self.current_user_id}")

        # Clear previous message details
        self.message_details_labels.clear_widgets()

        if messages_data:
            first_message = messages_data[0]
            self.conversation_id = first_message.get("conversation", {}).get("id", None)
            self.recipient_id = first_message.get("conversation", {}).get("recipient_id_display", None)
            self.sender_id = first_message.get("conversation", {}).get("sender_id", None)
            self.vendor_id = first_message.get("vendor", {}).get("id", None)

            print(
                f"💾 Saved Data: Conversation ID={self.conversation_id}, Recipient ID={self.recipient_id}, Sender ID={self.sender_id}, Vendor ID={self.vendor_id}")

        # Display vendor information at the top (only once)
        if messages_data:
            vendor_info = messages_data[0].get("vendor", {})  # Get vendor details from the first message
            if vendor_info:
                messaging_vendor = Button(
                    text=f"[b]Vendor Being Messaged:[/b] {vendor_info['institution_name']}",
                    markup=True,
                    color=(0, 0, 0, 1),
                    height=40
                )
                messaging_vendor.bind(
                    on_release=lambda instance: self.message_vendor_details(vendor_info["id"], vendor_info["slug"])
                )
                spacer = Widget(size_hint=(1, None), height=30)
                self.message_details_labels.add_widget(messaging_vendor)  # Add button only once
                self.message_details_labels.add_widget(spacer)

        # Loop through each message and create a card
        for message in messages_data:
            sender_id = message.get("conversation", {}).get("sender_id", "Unknown")
            recipient_id = message.get("conversation", {}).get("recipient_id_display", "Unknown")
            content = message.get("content", "No content")
            timestamp = message.get("timestamp", "Unknown time")

            # Determine if the current user is the sender
            is_sender = sender_id == self.current_user_id

            # Message styling
            sender_text = "You" if is_sender else f"User {sender_id}"
            align = "right" if is_sender else "left"

            # Create a card layout to hold message details
            message_details_card = MDCard(size_hint_y=None, height=150, padding=10, elevation=4)

            # Create a box layout inside the card
            card_layout = BoxLayout(orientation="vertical", padding=10, spacing=5)

            # Create message labels
            sender_label = Label(
                text=f"[b]Sender ID: {sender_text}[/b]", markup=True, halign=align, size_hint_y=None, height=20,
                color=(0, 0, 0, 1)
            )
            recipient_label = Label(
                text=f"[b]Recipient ID: {recipient_id}[/b]", markup=True, halign=align, size_hint_y=None, height=20,
                color=(0, 0, 0, 1)
            )
            content_label = Label(
                text=content, halign=align, size_hint_y=None, height=40, color=(0, 0, 0, 1)
            )
            timestamp_label = Label(
                text=timestamp, font_size=12, color=(0.5, 0.5, 0.5, 1), halign=align, size_hint_y=None, height=20
            )

            # Add labels to the card layout
            card_layout.add_widget(sender_label)
            card_layout.add_widget(recipient_label)
            card_layout.add_widget(content_label)
            card_layout.add_widget(timestamp_label)

            # Add the layout to the card
            message_details_card.add_widget(card_layout)

            # Add the card to the message list
            self.message_details_labels.add_widget(message_details_card)

    def add_reply_section(self):
        """Adds a reply input area and send button."""
        reply_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10, padding=10)

        # Create TextInput for reply
        self.reply_input = TextInput(
            hint_text="Type your message...",
            size_hint_x=0.8,
            multiline=True,
        )

        # Create "Send" button
        send_button = Button(
            text="Send",
            size_hint_x=0.2,
            color=(0, 0, 0, 1),
            on_release=self.send_reply
        )

        # Add input and button to layout
        reply_layout.add_widget(self.reply_input)
        reply_layout.add_widget(send_button)

        # Add reply section to the content layout
        self.content_layout.add_widget(reply_layout)

    def send_reply(self, instance):
        """Handles sending a reply message to the Django API."""
        reply_text = self.reply_input.text.strip()

        if not reply_text:
            print("⚠️ Cannot send an empty message.")
            return

        print(f"📩 Sending Message: {reply_text}")

        if not hasattr(self, "current_user_id") or not hasattr(self, "recipient_id") or not hasattr(self, "sender_id"):
            print("❌ Missing required IDs. Cannot send message.")
            return

        # Use stored data
        sender_id = self.current_user_id
        recipient_id = self.recipient_id
        conversation_id = self.conversation_id
        vendor_id = self.vendor_id

        # Ensure the recipient is the actual other user in the conversation
        if sender_id == recipient_id:
            recipient_id = self.sender_id  # Swap recipient with stored sender_id

        print(f"💬 Sending message from {sender_id} to {recipient_id} in conversation {conversation_id} for {vendor_id}")

        # Django API endpoint
        api_url = f"http://localhost:8000/api/messages/"

        # Data payload
        payload = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "conversation_id": conversation_id,  # Include conversation ID
            "vendor_id": vendor_id,  # Include vendor ID if needed
            "content": reply_text
        }
        print("📦 Message Payload:", payload)
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, data=json.dumps(payload), headers=headers)

            if response.status_code == 201:
                print("✅ Message sent successfully!")
                self.reply_input.text = ""  # Clear input after sending

                # Refresh messages
                self.load_message_details(self.fetch_messages())

            else:
                print(f"❌ Failed to send message: {response.text}")

        except requests.RequestException as e:
            print(f"🚨 Network Error: {e}")

    def fetch_messages(self):
        """Fetch the latest messages from the API after sending a reply."""
        app = App.get_running_app()

        # Get the authentication token from user_data
        token = app.user_data.get("token", None)

        if not token:
            print("❌ No auth token found. Cannot fetch messages.")
            return []

        api_url = "http://localhost:8000/api/messages/"
        headers = {"Authorization": f"Token {token}"}  # Ensure correct token format

        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch messages. Response: {response.text}")
        except requests.RequestException as e:
            print(f"🚨 Error fetching messages: {e}")

        return []

    def message_vendor_details(self, vendor_id, slug, *args):
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