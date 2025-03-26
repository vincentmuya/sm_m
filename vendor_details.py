from header import Header
from navbar import Navbar
from filter_widget import Filter
from search_widget import SearchWidget

import requests
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import json
from kivy.metrics import dp
from kivy.utils import platform
from kivy.uix.filechooser import FileChooserListView
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

Builder.load_file('vendor_details.kv')

class ReviewFileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Select Menu Image"
        self.size_hint = (0.9, 0.9)

        layout = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView()
        layout.add_widget(self.filechooser)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.2)
        select_btn = Button(text="Select", on_press=self.select_file)
        cancel_btn = Button(text="Cancel", on_press=self.dismiss)
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        layout.add_widget(btn_layout)
        self.add_widget(layout)

    def select_file(self, instance):
        if self.filechooser.selection:
            self.callback(self.filechooser.selection)
        self.dismiss()

class VendorDetailsScreen(Screen):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    description = StringProperty()
    location = StringProperty()
    phone_number = StringProperty()
    email = StringProperty()
    website = StringProperty()
    social_media = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()
    gallery_images = ListProperty()
    vendor_user_id = StringProperty()
    average_rating = NumericProperty(0)
    menu_images = ListProperty([])
    user_id = NumericProperty()
    reviews = ListProperty([])

    def load_details(self, vendor_details):
        # print("Loading vendor_details...")
        # print("Vendor Details:", vendor_details)

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")

        self.institution_name = vendor_details['institution_name']
        self.price = str(vendor_details['price'])
        self.description = vendor_details['description']
        self.phone_number = str(vendor_details['phone_number'])
        self.location = str(vendor_details['location'])
        self.email = vendor_details['email']
        self.website = vendor_details['website']
        self.social_media = vendor_details['social_media']
        self.image_source = f"http://localhost:8000{vendor_details['profile_image']}"
        self.slug = vendor_details['slug']
        self.vendor_id = str(vendor_details['id'])
        self.vendor_user_id = str(vendor_details['user'])
        self.fetch_ratings()

        # Fetch reviews after loading vendor details
        self.fetch_reviews()

        # Fetch service details from the API using service ID
        service_id = vendor_details['service']
        service_name = 'Unknown Service'

        # Fetch all services from the services API
        services_response = requests.get('http://localhost:8000/api/services/')
        if services_response.status_code == 200:
            services = services_response.json()
            # print("Services:", services)

            # Find the service name corresponding to the vendor's service_id
            for service in services:
                if service['id'] == service_id:
                    service_name = service['service']
                    break

        self.service = service_name

        # Fetch location details from the API using service ID
        location_id = vendor_details['location']
        location_name = 'Unknown Service'

        # Fetch all services from the services API
        locations_response = requests.get('http://localhost:8000/api/locations/')
        if locations_response.status_code == 200:
            locations = locations_response.json()
            # print("Services:", locations)

            # Find the service name corresponding to the vendor's location_id
            for location in locations:
                if location['id'] == location_id:
                    location_name = location['location']
                    break

        self.location = location_name

        # Fetch gallery images URLs using gallery_images IDs
        gallery_images = []
        gallery_images_api_url = 'http://localhost:8000/api/gallery_images_vendor/'

        # Fetch the mapping of image_id to image filename from the API
        response = requests.get(gallery_images_api_url)
        if response.status_code == 200:
            image_mapping = response.json()
            # print("Image Mapping:", image_mapping)

            for image_id in vendor_details['gallery_images']:
                if str(image_id) in image_mapping:
                    image_url = image_mapping[str(image_id)]
                    # print("Image URL:", image_url)

                    gallery_images.append(image_url)

        # print("Gallery Images:", gallery_images)

        self.gallery_images = gallery_images

        # Fetch menu images for this vendor
        menu_images_api_url = f"http://localhost:8000/api/menu_images/?vendor_id={self.vendor_id}"

        menu_images = []
        response = requests.get(menu_images_api_url)
        if response.status_code == 200:
            image_mapping = response.json()
            for image_id, image_data in image_mapping.items():
                menu_images.append(image_data["image"])  # Append image URL

        self.menu_images = menu_images

        # Update UI elements with fetched data
        self.ids.institution_name_label.text = self.institution_name
        self.ids.price_label.text = self.price
        self.ids.description_label.text = self.description
        self.ids.service_label.text = self.service
        self.ids.phone_number_label.text = self.phone_number
        self.ids.email_label.text = self.email
        self.ids.website_label.text = self.website
        self.ids.social_media_label.text = self.social_media

        # Ensure all properties are updated
        self.property('institution_name').dispatch(self)
        self.property('price').dispatch(self)
        self.property('description').dispatch(self)
        self.property('location').dispatch(self)
        self.property('service').dispatch(self)
        self.property('phone_number').dispatch(self)
        self.property('email').dispatch(self)
        self.property('website').dispatch(self)
        self.property('social_media').dispatch(self)
        self.property('gallery_images').dispatch(self)
        self.property('menu_images').dispatch(self)

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot display Vendor Buttons.")
            authenticated = False
        else:
            authenticated = True
            current_user_id = user_data["id"]
            print(f"🔍 Current User ID: {current_user_id}")

        if not authenticated:
            # ✅ Create a box layout inside the card
            card_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # ✅ GridLayout to hold buttons
            vendor_details_buttons = GridLayout(cols=5, size_hint_y=None, height=40, spacing='10dp')

            # ✅ Show "Not Logged In" buttons if user is not authenticated
            login_rate_vendor_button = Button(text="Login To:Rate Vendor", markup=True, color=(1, 0, 0, 1))
            login_favorite_vendor_button = Button(text=":Favorite Vendor", markup=True, color=(1, 0, 0, 1))
            login_send_message_button = Button(text=":Message Vendor", markup=True, color=(1, 0, 0, 1))
            login_book_vendor_button = Button(text=":Book Vendor", markup=True, color=(1, 0, 0, 1))
            login_review_vendor_button = Button(text=":Review Vendor", markup=True, color=(1, 0, 0, 1))

            vendor_details_buttons.add_widget(login_rate_vendor_button)
            vendor_details_buttons.add_widget(login_favorite_vendor_button)
            vendor_details_buttons.add_widget(login_send_message_button)
            vendor_details_buttons.add_widget(login_book_vendor_button)
            vendor_details_buttons.add_widget(login_review_vendor_button)

            # ✅ Add buttons inside `card_layout`
            card_layout.add_widget(vendor_details_buttons)

        elif int(self.vendor_user_id) == current_user_id:

            # ✅ Create a box layout inside the card
            card_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # ✅ GridLayout to hold buttons
            vendor_details_buttons = GridLayout(cols=5, size_hint_y=None, height=40, spacing='10dp')

            # ✅ Show " Logged In user == vendor.user" buttons if user is not authenticated
            own_rate_vendor_button = Button(text="Can't:Rate Vendor", markup=True, color=(1, 0, 0, 1))
            own_favorite_vendor_button = Button(text=":Favorite Vendor", markup=True, color=(1, 0, 0, 1))
            own_send_message_button = Button(text=":Message Vendor", markup=True, color=(1, 0, 0, 1))
            own_book_vendor_button = Button(text=":Book Vendor", markup=True, color=(1, 0, 0, 1))
            own_review_vendor_button = Button(text=":Review Vendor", markup=True, color=(1, 0, 0, 1))

            vendor_details_buttons.add_widget(own_rate_vendor_button)
            vendor_details_buttons.add_widget(own_favorite_vendor_button)
            vendor_details_buttons.add_widget(own_send_message_button)
            vendor_details_buttons.add_widget(own_book_vendor_button)
            vendor_details_buttons.add_widget(own_review_vendor_button)

            # ✅ Add buttons inside `card_layout`
            card_layout.add_widget(vendor_details_buttons)

        else:
            # ✅ Create a box layout inside the card
            card_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # ✅ GridLayout to hold buttons
            vendor_details_buttons = GridLayout(cols=7, size_hint_y=None, height=40, spacing='10dp')

            # ✅ Label for rating
            self.rate_vendor_label = Label(text="Rate Vendor:", color=(0, 0, 0, 1))

            # ✅ Spinner for selecting rating
            self.rating_spinner = Spinner(text="Select Rating", values=['1', '2', '3', '4', '5'])

            # ✅ Button to submit rating
            self.rate_vendor_button = Button(text="Rate Vendor", markup=True, color=(0, 0, 0, 1))
            self.rate_vendor_button.bind(
                on_release=lambda instance: self.submit_rating(
                    self.vendor_id,
                    int(self.rating_spinner.text) if self.rating_spinner.text.isdigit() else 0
                )
            )

            favorite_vendor_button = Button(text="Favorite Vendor", markup=True, color=(0, 0, 0, 1))
            favorite_vendor_button.bind(on_release=self.favorite_vendor)

            send_message_button = Button(text="Send Message", markup=True, color=(0, 0, 0, 1))
            send_message_button.bind(on_release=self.show_message_vendor)

            book_vendor_button = Button(text="Book Vendor", markup=True, color=(0, 0, 0, 1))
            book_vendor_button.bind(
                on_release=lambda instance: app.show_book_popup(self.vendor_id, current_user_id)
            )

            review_vendor_button = Button(text="Review Vendor", markup=True, color=(0, 0, 0, 1))
            review_vendor_button.bind(on_release=self.show_review_vendor)

            # ✅ Add buttons if user is authenticated
            vendor_details_buttons.add_widget(self.rate_vendor_label)
            vendor_details_buttons.add_widget(self.rating_spinner)
            vendor_details_buttons.add_widget(self.rate_vendor_button)
            vendor_details_buttons.add_widget(favorite_vendor_button)
            vendor_details_buttons.add_widget(send_message_button)
            vendor_details_buttons.add_widget(book_vendor_button)
            vendor_details_buttons.add_widget(review_vendor_button)
            card_layout.add_widget(vendor_details_buttons)

        # ✅ Add final content to the card
        self.add_widget(card_layout)

        # self.add_widget(Navbar())

        # Create and add the Search, at the top of the screen
        search = SearchWidget(search_callback=self.display_search_results, size_hint=(1, None))
        search.pos_hint = {'x':0, 'y':0.849}
        self.add_widget(search)

        # Create and add the Filter Widget, at the top of the screen
        filter_widget = Filter(filter_callback=self.apply_filter)
        filter_widget.pos_hint = {'x': 0, 'y': 0.772}
        self.add_widget(filter_widget)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        header.pos_hint = {'x': 0, 'y': 0.95}
        self.add_widget(header)

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

    def fetch_ratings(self):
        """Fetch ratings from the API for the selected vendor and update UI"""
        api_url = f'http://localhost:8000/api/ratings/?vendor_id={self.vendor_id}'
        response = requests.get(api_url)

        if response.status_code == 200:
            ratings = response.json()
            if ratings:
                # Calculate the average rating
                total_rating = sum(rating['rating'] for rating in ratings)
                self.average_rating = total_rating / len(ratings)
            else:
                self.average_rating = 0  # No ratings available

        # Update the UI with the average rating
        self.ids.rating_label.text = f'Average Rating: {self.average_rating:.1f}/5'

    def submit_rating(self, vendor_id, rating_value):
        app = App.get_running_app()

        # Fetch authenticated user data
        user_data = app.get_authenticated_data("api/user")

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot submit rating.")
            return

        user_id = user_data["id"]  # Get the user ID

        url = "http://localhost:8000/api/ratings/"
        headers = {
            "Authorization": f"Token {app.user_data.get('token', '')}",
            "Content-Type": "application/json"
        }

        # ✅ Fix field names
        data = {"user_id": user_id, "vendor_id": vendor_id, "rating": rating_value}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                print("✅ Rating submitted successfully!")
                self.ids.rating_spinner.text = "Vendor Rated"
                self.ids.rating_spinner.disabled = True  # Disable after rating
            else:
                print(f"❌ Failed to submit rating. Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")

    def favorite_vendor(self):
        app = App.get_running_app()

        # Fetch authenticated user data
        user_data = app.get_authenticated_data("api/user")

        if not user_data or "id" not in user_data:
            print("❌ User not authenticated. Cannot favorite vendor.")
            return

        user_id = user_data["id"]  # Get the user ID
        vendor_id = int(self.vendor_id)  # Convert vendor_id to integer

        url = "http://localhost:8000/api/favorites/"
        headers = {
            "Authorization": f"Token {app.user_data.get('token', '')}",
            "Content-Type": "application/json"
        }

        data = {"user_id": user_id, "vendor_id": vendor_id}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                print("✅ Vendor favorited successfully!")
                self.ids.favorite_button.text = "Favorited "
                self.ids.favorite_button.disabled = True  # Disable after favoriting
            else:
                print("❌ Failed to favorite vendor:", response.json())
        except Exception as e:
            print("❌ Error favoriting vendor:", str(e))

    def show_message_vendor(self, *args):
        """Display popup for messaging the vendor."""

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        message = Label(text="Message Vendor", size_hint=(1, 0.5))
        textinput = TextInput(text='', multiline=True)

        send_message_button = Button(text="Send Message", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        popup = Popup(title="Message Vendor", content=layout, size_hint=(0.7, 0.4))

        send_message_button.bind(on_release=lambda instance: self.send_message(popup, textinput))
        cancel_button.bind(on_release=popup.dismiss)

        layout.add_widget(message)
        layout.add_widget(textinput)
        layout.add_widget(send_message_button)
        layout.add_widget(cancel_button)

        popup.open()

    def send_message(self, popup, textinput):
        """Handle message sending."""
        message_text = textinput.text.strip()
        if message_text:
            popup.dismiss()
            self.message_vendor(message_text)
        else:
            print("Message cannot be empty")

    def message_vendor(self, message_text):
        """Send a message to the vendor."""
        print("Message Vendor Called")
        app = App.get_running_app()

        # Fetch authenticated user data
        user_data = app.get_authenticated_data("api/user")
        current_user_id = user_data.get("id")  # Use `.get()` to avoid KeyError

        if not current_user_id:
            print("❌ Error: User ID is missing")
            return

        vendor_id = self.vendor_id  # Assuming you have this stored
        vendor_user_id = self.vendor_user_id  # Owner of the vendor

        if not vendor_id or not vendor_user_id:
            print("❌ Error: Vendor ID or Vendor User ID is missing")
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
        message_sent = self.send_message_to_api(conversation_id, current_user_id, message_text)
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

    def send_message_to_api(self, conversation_id, current_user_id, message_text):
        """Send the message to the API."""
        url = f"http://localhost:8000/api/messages/"
        payload = {
            "conversation_id": conversation_id,
            "sender_id": current_user_id,
            "recipient_id": self.vendor_user_id,  # Vendor owner is the recipient
            "vendor_id": self.vendor_id,  # Vendor item being discussed
            "content": message_text
        }
        print("📦 Message Payload:", payload)
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        return response.status_code == 201  # Return True if message was sent successfully

    def fetch_reviews(self):
        """Fetch reviews for the current vendor and match user IDs to usernames."""
        reviews_url = f"http://localhost:8000/api/reviews/vendor/{self.vendor_id}/"

        try:
            response = requests.get(reviews_url)
            if response.status_code == 200:
                reviews_data = response.json()  # List of reviews

                # Fetch user details for each review asynchronously
                for review in reviews_data:
                    user_id = review.get("user")
                    if user_id:
                        username = self.fetch_username(user_id)  # Get username
                        review["user_name"] = username  # Attach username to review

                    # ✅ Fetch usernames for review comments
                    for comment in review.get("reviewcomments", []):
                        comment_user_id = comment.get("user")
                        if comment_user_id:
                            comment["user_name"] = self.fetch_username(comment_user_id)  # Fetch and attach username

                self.reviews = reviews_data  # Store reviews in the list property
                self.display_reviews()
            else:
                print("❌ Failed to fetch reviews:", response.text)
        except Exception as e:
            print("❌ Error fetching reviews:", str(e))

    def fetch_username(self, user_id):
        """Fetch username based on user_id."""
        user_url = f"http://localhost:8000/api/user/{user_id}"
        try:
            response = requests.get(user_url)
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get("username", "Anonymous")
            else:
                print(f"❌ Failed to fetch username for user ID {user_id}: {response.text}")
                return "Anonymous"
        except Exception as e:
            print(f"❌ Error fetching username for user ID {user_id}: {str(e)}")
            return "Anonymous"

    def display_reviews(self):
        """Dynamically add reviews to the screen."""
        app = App.get_running_app()

        # Fetch authenticated user data
        user_data = app.get_authenticated_data("api/user")
        current_user_id = user_data.get("id")

        reviews_layout = self.ids.reviews_container  # Ensure you have a container in your .kv file
        reviews_layout.clear_widgets()  # Clear previous reviews

        print("Vendor ID", self.vendor_id)
        print("Vendor User ID", self.vendor_user_id)
        print("Current user ID", current_user_id)

        for review in self.reviews:
            image_source = review.get("vendor_review_image", "")

            if not image_source or image_source is None:  # Ensure image_source is always a valid string
                image_source = "No Image"

            # ✅ Pass comments list to ReviewCard
            review_card = ReviewCard(
                username=review.get("user_name", "Anonymous"),
                review_text=review["review"],
                timestamp=review["timestamp"],
                image_source=image_source,
                comments=review.get("reviewcomments", []),  # Pass comments
                vendor_user_id=self.vendor_user_id,
                current_user_id=current_user_id,
                review_id=review.get("id")
            )
            reviews_layout.add_widget(review_card)

    def show_review_vendor(self, *args):
        """Display popup for Reviewing the vendor."""

        layout = BoxLayout(orientation='vertical', spacing=20, padding=5)
        # Store reference to upload button
        self.upload_review_image = Button(text="Choose Review Image(Optional)")  # ✅ Define self.upload_review_image
        self.upload_review_image.bind(on_press=self.choose_file_review)

        textinput = TextInput(text='', multiline=True)

        post_review_button = Button(text="Post review", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        popup = Popup(title="Review Vendor", content=layout, size_hint=(0.7, 0.4))

        post_review_button.bind(on_release=lambda instance: self.post_review(popup, textinput))
        cancel_button.bind(on_release=popup.dismiss)

        layout.add_widget(self.upload_review_image)  # ✅ Ensure the button is added to the layout
        layout.add_widget(textinput)
        layout.add_widget(post_review_button)
        layout.add_widget(cancel_button)

        popup.open()

    def choose_file_review(self, instance):
        """Opens a file picker for menu image selection."""
        self.popup = ReviewFileChooserPopup(self.review_file_selected)
        self.popup.open()

    def review_file_selected(self, selection):
        """Handle file selection from file picker."""
        if selection:
            self.selected_review_file = selection[0]  # Ensure this is set
            if hasattr(self, 'upload_review_image'):  # ✅ Check if the button exists
                self.upload_review_image.text = "Review Image Selected"
            else:
                print("❌ Error: upload_review_image button not found.")

    def post_review(self, popup, textinput):
        """Handle posting a review along with an optional image."""
        review_text = textinput.text.strip()

        if not review_text:
            print("❌ Review cannot be empty")
            return

        popup.dismiss()

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")
        current_user_id = user_data.get("id")

        if not current_user_id:
            print("❌ Error: User ID is missing")
            return

        vendor_id = self.vendor_id

        if not vendor_id:
            print("❌ Error: Vendor ID is missing")
            return

        url = "http://localhost:8000/api/reviews/"

        # Prepare data
        data = {
            "review": review_text,
            "user_id": current_user_id,
            "vendor_id": vendor_id
        }

        # Prepare files (if an image was selected)
        files = {}
        if hasattr(self, "selected_review_file") and self.selected_review_file:
            files["vendor_review_image"] = open(self.selected_review_file, "rb")

        # Send request
        response = requests.post(url, data=data, files=files)

        # Close file after sending
        if files:
            files["vendor_review_image"].close()

        # Handle response
        if response.status_code == 201:
            print("✅ Review posted successfully:", response.json())
            toast("✅ Review posted successfully:")
        else:
            print("❌ Error posting review:", response.text)


    def open_account_dropdown(self, instance):
        """Manually opens the account dropdown."""
        app = App.get_running_app()

        # ✅ Ensure dropdown is updated before opening
        app.update_account_dropdown()

        # ✅ Open dropdown manually
        app.account_dropdown.open(instance)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()

        # ✅ Ensure the proxy button always has updated text
        self.account_proxy_button.text = app.account_button.text

    def display_search_results(self, vendors, search_query):
        print(f"Search results: {len(vendors)}")
        # print("Search results:", vendors)
        app = App.get_running_app()
        # Pass the service_id (parent category) to the search_results screen
        search_results_screen = app.root.get_screen('search_results')
        search_results_screen.load_search_results(vendors, search_query)
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'search_results'

    def apply_filter(self, location=None, service=None, price_range=None):
        print(f"Applying filter with location={location}, service={service}, price_range={price_range}")

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

class CarouselApp(App):
    def build(self):
        carousel = Carousel(direction='right')
        for i in range(10):
            src = "http://placehold.it/480x270.png&text=slide-%d&.png" % i
            image = AsyncImage(source=src, fit_mode="contain")
            carousel.add_widget(image)
        return carousel

class MyCard(MDCard):
    institution_name = StringProperty()
    price = StringProperty()
    location = StringProperty()
    description = StringProperty()
    phone_number = StringProperty()
    email = StringProperty()
    website = StringProperty()
    social_media = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(20)
        self.size_hint_y = None
        self.height = dp(350)  # Adjust height as needed
        self.pos_hint = {'center_x': 0.5}
        self.elevation = 5  # Add shadow for better visibility
        self.md_bg_color = (1, 1, 1, 1)  # White background
        self.radius = [10, 10, 10, 10]  # Rounded corners
        self.add_content()

    def add_content(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        labels_data = [
            ('Institution Name', self.institution_name),
            ('Price', self.price),
            ('Location', self.location),
            ('Description', self.description),
            ('Phone', self.phone_number),
            ('Email', self.email),
            ('Website', self.website),
            ('Social', self.social_media)
        ]

        for label_text, data_value in labels_data:
            if data_value:
                label = MDLabel(
                    text=f"[b]{label_text}:[/b] {data_value}",
                    markup=True,
                    theme_text_color="Primary",
                    halign="left",
                    size_hint_y=None,
                    height=dp(20)
                )
                content.add_widget(label)

        self.add_widget(content)

class ReviewCard(MDCard):
    username = StringProperty()
    review_text = StringProperty()
    timestamp = StringProperty()
    image_source = StringProperty()
    comments = ListProperty()  # Store comments
    vendor_user_id = NumericProperty()
    current_user_id = NumericProperty()
    review_id = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(8)
        self.size_hint = (None, None)
        self.size = (dp(300), dp(350))
        self.md_bg_color = (1, 1, 1, 1)
        self.radius = [10, 10, 10, 10]

        # ✅ Center the card in its parent layout
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # Adjust height dynamically based on comments
        base_height = dp(120) if not self.image_source else dp(200)
        self.height = base_height + (len(self.comments) * dp(80))

        self.add_content()

    def add_content(self):
        main_layout = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        title_label = MDLabel(
            text="Reviews",
            font_style="H6",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        main_layout.add_widget(title_label)

        # ScrollView for the reviews
        scroll_view = ScrollView(size_hint=(1, 1))
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        username_label = MDLabel(
            text=f"[b]{self.username}[/b]",
            markup=True,
            theme_text_color="Primary",
            halign="left"
        )
        content.add_widget(username_label)

        review_label = MDLabel(
            text=self.review_text,
            theme_text_color="Secondary",
            halign="left"
        )
        content.add_widget(review_label)

        timestamp_label = MDLabel(
            text=self.timestamp,
            theme_text_color="Hint",
            font_style="Caption",
            halign="left"
        )
        content.add_widget(timestamp_label)

        if self.image_source and self.image_source != "No Image":
            image = AsyncImage(
                source=f"http://localhost:8000{self.image_source}",
                size_hint_y=None,
                height=dp(100)
            )
            content.add_widget(image)

        # ✅ Conditionally Add Button
        if int(self.vendor_user_id) == self.current_user_id:
            post_comment_button = MDRaisedButton(
                text="Post Comment",
                size_hint=(None, None),
                size=(dp(150), dp(40)),
                pos_hint={"center_x": 0.5},
                on_release=lambda instance: self.on_post_comment_pressed()
            )
            content.add_widget(post_comment_button)

        # ✅ Add comments inside the review card
        if self.comments:
            comments_label = MDLabel(
                text="[b]Comments:[/b]",
                markup=True,
                theme_text_color="Primary",
                halign="left"
            )
            content.add_widget(comments_label)

            for comment in self.comments:
                comment_text = f"{comment.get('user_name', 'Anonymous')}: {comment['comment']}"
                comment_label = MDLabel(
                    text=comment_text,
                    theme_text_color="Secondary",
                    halign="left",
                    size_hint_y=None,
                    height=dp(20)
                )
                content.add_widget(comment_label)

        scroll_view.add_widget(content)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def on_post_comment_pressed(self):
        print(f"Post Comment button pressed")
        """Display popup for Review Comment."""

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        message = Label(text="Comment On Review", size_hint=(1, 0.5))
        textinput = TextInput(text='', multiline=True)

        send_review_comment_button = Button(text="Post Review Comment", size_hint=(1, 0.3))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))

        popup = Popup(title="Review Comment", content=layout, size_hint=(0.7, 0.4))

        send_review_comment_button.bind(on_release=lambda instance: self.send_comment_review(popup, textinput))
        cancel_button.bind(on_release=popup.dismiss)

        layout.add_widget(message)
        layout.add_widget(textinput)
        layout.add_widget(send_review_comment_button)
        layout.add_widget(cancel_button)

        popup.open()

    def send_comment_review(self, popup, textinput):
        print("Send Comment Review Called")
        review_comment_text = textinput.text.strip()

        if not review_comment_text:
            print("❌ Review Comment cannot be empty")
            return

        popup.dismiss()

        app = App.get_running_app()
        user_data = app.get_authenticated_data("api/user")
        current_user_id = user_data.get("id")

        if not current_user_id:
            print("❌ Error: User ID is missing")
            return

        if not self.review_id:
            print("❌ Error: Review ID is missing")
            return

        url = "http://localhost:8000/api/comment/"

        # Prepare data
        data = {
            "comment": review_comment_text,
            "user_id": current_user_id,
            "review_id": self.review_id
        }

        print("✅ Sending review comment:", data)
        # Send request
        response = requests.post(url, data=data)

        # Handle response
        if response.status_code == 201:
            print("✅ Review Comment Posted Successfully:", response.json())
            toast("✅ Review Comment Posted Successfully:")
        else:
            print("❌ Error Posting Review Comment:", response.text)
