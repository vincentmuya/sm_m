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
from functools import partial

Builder.load_file('messages.kv')


class MessagesScreen(Screen):
    """A screen to display Messages."""

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

        # Add other screens (MessagesScreen) to the content layout
        self.message_labels = GridLayout(cols=1, size_hint_y=None, spacing='10dp')

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=30)
        bottom_spacer = Widget(size_hint=(1, None), height=650)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.message_labels)
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
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(150, 40),
                                          pos=(650, 560))
        # ✅ Create a proxy button
        self.account_proxy_button = Button(text=app.account_button.text)
        # ✅ Open dropdown manually when proxy button is clicked
        self.account_proxy_button.bind(on_release=self.open_account_dropdown)
        # ✅ Add proxy button instead of the real one
        self.user_info_layout.add_widget(self.account_proxy_button)
        self.add_widget(self.user_info_layout)


    def load_user_messages(self, user_messages):
        """Load user Conversations into the screen with card-style layouts."""

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot display messages.")
            return

        current_user_id = user_data["id"]
        print(f"🔍 Current User ID: {current_user_id}")
        print(f"📜 User Conversations Count: {len(user_messages)}")

        # Clear previous messages
        self.message_labels.clear_widgets()

        if not user_messages:
            no_messages_label = Label(
                text="No messages found.",
                size_hint_y=None,
                height=40,
                color=(0, 0, 0, 1)  # Black text
            )
            self.message_labels.add_widget(no_messages_label)
            return

        for message in user_messages:
            institution_name = message["vendor"]["institution_name"]

            # Create a card layout
            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=170,
                padding=10,
                spacing=5
            )

            # Apply background color & rounded corners
            with card.canvas.before:
                Color(1, 1, 1, 1)  # White background
                card.bg_rect = RoundedRectangle(radius=[10], pos=card.pos, size=card.size)

            def update_bg(instance, value):
                card.bg_rect.pos = card.pos
                card.bg_rect.size = card.size

            card.bind(pos=update_bg, size=update_bg)

            # Vendor image (if available)
            if "profile_image" in message["vendor"]:
                profile_img = AsyncImage(
                    source=f"https://sherehemall.co.ke{message['vendor']['profile_image']}",
                    size_hint=(None, None),
                    size=(80, 80),
                    allow_stretch=True
                )
                card.add_widget(profile_img)

            # Message information
            message_label = Label(
                text=f"Message for {institution_name}",
                size_hint_y=None,
                height=30,
                color=(0, 0, 0, 1),  # Black text
                font_size='16sp',
                bold=True
            )
            card.add_widget(message_label)

            # ✅ Message the user made
            if message["sender_id"] == current_user_id:
                request_label = Label(
                    text=f"You sent a message to {institution_name}",
                    size_hint_y=None,
                    height=30,
                    color=(0, 0, 0, 1),
                    font_size='14sp'
                )
                card.add_widget(request_label)

            # ✅ Messages received for the user's vendor
            if message["recipient_id_display"] == current_user_id:
                request_label = Label(
                    text=f"You have a message for {institution_name}",
                    size_hint_y=None,
                    height=30,
                    color=(0, 0, 0, 1),
                    font_size='14sp'
                )
                card.add_widget(request_label)

            # if message["user_id"] == current_user_id:  # Check if the user sent the request
            view_button = Button(
                text="View Details",
                size_hint_y=None,
                height=30,
                background_color=(0.2, 0.6, 1, 1)  # Blue button
            )

            # Correctly bind button to pass the specific message object
            view_button.bind(on_release=partial(self.fetch_message_details, message))

            card.add_widget(view_button)

            self.message_labels.add_widget(card)

        # ✅ Update layout height dynamically
        self.message_labels.height = len(self.message_labels.children) * 130  # Adjust height per card
        print(f"✅ Total widgets in message_labels: {len(self.message_labels.children)}")  # Debugging

    def fetch_message_details(self, message, *args):
        """Handles displaying details for a selected message request sent by the user."""
        print(f"🔍 Viewing message details: {message}")

        app = App.get_running_app()

        # Extract conversation_id from the clicked message
        conversation_id = message.get("id")
        if not conversation_id:
            print("❌ Error: Conversation ID not found.")
            return

        # API Endpoint to fetch messages for this conversation
        url = f"https://sherehemall.co.ke/api/messages/?conversation_id={conversation_id}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                messages_data = response.json()
                # print(f"📩 Messages in Conversation {conversation_id}: {messages_data}")
            else:
                print(f"❌ Failed to fetch messages: {response.status_code} {response.text}")
                messages_data = []
        except Exception as e:
            print(f"❌ Error fetching messages: {e}")
            messages_data = []

        # Fetch the screen correctly
        try:
            messages_loaded_screen = app.root.get_screen("message_details")
        except Exception as e:
            print(f"❌ Error fetching message_details screen: {e}")
            return

        # Check if the screen has load_message_details method
        if hasattr(messages_loaded_screen, "load_message_details"):
            messages_loaded_screen.load_message_details(messages_data)
        else:
            print("❌ Error: message_details screen does not have load_message_details method.")

        # ✅ Transition to the message details screen
        app.root.current = "message_details"


    def open_account_dropdown(self, instance):
        """Manually opens the account dropdown."""
        app = App.get_running_app()
        # Ensure dropdown is updated before opening
        app.update_account_dropdown()
        # Open dropdown manually
        app.account_dropdown.open(instance)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()
        # Ensure the proxy button always has updated text
        self.account_proxy_button.text = app.account_button.text

    def apply_filter(self, location=None, service=None, price_range=None):
        # print(f"Applying filter with location={location}, service={service}, price_range={price_range}")

        # Fetch services to resolve the service name to ID
        services_response = requests.get('https://sherehemall.co.ke/api/services/')
        services = services_response.json() if services_response.status_code == 200 else []

        # Get the service ID from the service name (if the service exists)
        service_id = None
        if service:
            for s in services:
                if s['service'] == service:
                    service_id = s['id']
                    break

        # Construct the API URL with the service ID
        api_url = 'https://sherehemall.co.ke/api/vendor/'
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
