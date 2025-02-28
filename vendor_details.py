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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner

Builder.load_file('vendor_details.kv')

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
    vendor_id = StringProperty()
    average_rating = NumericProperty(0)
    menu_images = ListProperty([])
    user_id = NumericProperty()

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
        self.fetch_ratings()

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
            print("❌ User not authenticated. Cannot display bookings.")
            authenticated = False
        else:
            authenticated = True
            current_user_id = user_data["id"]
            print(f"🔍 Current User ID: {current_user_id}")

        # ✅ Create a box layout inside the card
        card_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # ✅ GridLayout to hold buttons
        vendor_details_buttons = GridLayout(cols=7, size_hint_y=None, height=40, spacing='10dp')

        if authenticated:
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
            send_message_button.bind(on_release=self.message_vendor)

            book_vendor_button = Button(text="Book Vendor", markup=True, color=(0, 0, 0, 1))
            book_vendor_button.bind(
                on_release=lambda instance: app.show_book_popup(self.vendor_id, current_user_id)
            )

            review_vendor_button = Button(text="Review Vendor", markup=True, color=(0, 0, 0, 1))

            # ✅ Add buttons if user is authenticated
            vendor_details_buttons.add_widget(self.rate_vendor_label)
            vendor_details_buttons.add_widget(self.rating_spinner)
            vendor_details_buttons.add_widget(self.rate_vendor_button)
            vendor_details_buttons.add_widget(favorite_vendor_button)
            vendor_details_buttons.add_widget(send_message_button)
            vendor_details_buttons.add_widget(book_vendor_button)
            vendor_details_buttons.add_widget(review_vendor_button)
            card_layout.add_widget(vendor_details_buttons)

        else:
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

    def message_vendor(self, *args):
        print("Message Vendor Called")

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