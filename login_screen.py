from header import Header
from navbar import Navbar
from search_widget import SearchWidget
from filter_widget import Filter

import requests
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.widget import Widget
from kivy.utils import rgba
from kivy.clock import mainthread

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()

        card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(300, 300),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=10,
            elevation=4,
        )

        title = MDLabel(
            text="Log In",
            theme_text_color="Primary",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=40
        )

        self.username = MDTextField(
            hint_text='Username',
            size_hint=(None, None),
            size=(280, 40),
            pos_hint={'center_x': 0.5}
        )

        self.password = MDTextField(
            hint_text='Password',
            password=True,
            size_hint=(None, None),
            size=(280, 40),
            pos_hint={'center_x': 0.5}
        )

        self.login_button = MDRaisedButton(
            text='Login',
            size_hint=(None, None),
            size=(280, 40),
            pos_hint={'center_x': 0.5}
        )
        self.login_button.bind(on_release=self.login_user)

        self.dont_button = MDRaisedButton(
            text="Don't have an account? Register here.",
            size_hint=(None, None),
            size=(280, 40),
            pos_hint={'center_x': 0.5},
            md_bg_color = rgba("#FFA500")
        )

        # Spacer widget to add space after the login button
        spacer = Widget(size_hint=(1, None), height=15)

        card.add_widget(title)
        card.add_widget(self.username)
        card.add_widget(self.password)
        card.add_widget(self.login_button)
        card.add_widget(spacer)
        card.add_widget(self.dont_button)

        self.layout.add_widget(card)

        self.add_widget(self.layout)


        # Create and add the Search, at the top of the screen
        search = SearchWidget(search_callback=self.display_search_results, size_hint=(1, None))
        search.pos_hint = {'x': 0, 'y': 0.849}
        self.add_widget(search)

        # Create and add the Filter Widget, at the top of the screen
        filter_widget = Filter(filter_callback=self.apply_filter)
        filter_widget.pos_hint = {'x': 0, 'y': 0.772}
        self.add_widget(filter_widget)

        # Create and add the navbar, fixed at the bottom of the screen
        self.nav_bar = Navbar(size_hint=(1, None), height=50)
        self.nav_bar.pos_hint = {'x': 0, 'y': 0}

        self.add_widget(self.nav_bar)

        # Create and add the Header, fixed at the top of the screen
        self.header = Header(size_hint=(1, None), height=50)
        self.header.pos_hint = {'x': 0, 'y': 0.95}

        self.add_widget(self.header)

    def login_user(self, instance):
        username = self.username.text
        password = self.password.text

        print(f"Attempting login with Username: {username}, Password: {password}")

        url = "http://localhost:8000/api/kivy_login/"
        data = {"username": username, "password": password}

        try:
            response = requests.post(url, json=data)
            print(f"Status Code: {response.status_code}")

            if "application/json" in response.headers.get("Content-Type", ""):
                response_data = response.json()
                print(f"Response: {response_data}")

                if response.status_code == 200:
                    user_id = response_data.get("user_id", "N/A")
                    print(f"Login Successful! User ID: {user_id}")

                    # Store user session
                    app = App.get_running_app()
                    app.user_data = {"user_id": user_id, "username": username}

                    # Find the header instance in your app and update it
                    for screen in self.manager.screens:
                        if hasattr(screen, "header"):  # Check if the screen has a header
                            screen.header.update_logged_in_user(username)

                    # Redirect to the landing page
                    self.manager.current = "landing_page"

                else:
                    print("Login Failed! Please check your credentials.")
            else:
                print("Error: Received unexpected HTML content instead of JSON.")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

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
