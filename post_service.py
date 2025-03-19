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
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.uix.dropdown import DropDown

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class FileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Select Profile Image"
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

class MenuFileChooserPopup(Popup):
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

class PostServiceScreen(Screen):
    """A screen to display Post A service."""

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

        # The form container
        self.post_vendor_form = GridLayout(cols=2, size_hint_y=None, spacing='10dp')
        self.post_vendor_form.bind(minimum_height=self.post_vendor_form.setter('height'))
        # Call the method to display the form
        self.show_post_vendor_form()

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=30)
        bottom_spacer = Widget(size_hint=(1, None), height=50)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.post_vendor_form)
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

    def show_post_vendor_form(self):
        """Creates and adds the vendor posting form to the UI."""

        # Create a scrollable form layout
        layout = GridLayout(cols=2, spacing=15, size_hint_y=None, row_default_height=50)
        layout.bind(minimum_height=layout.setter('height'))

        # Dictionary to store form fields
        self.fields = {}

        field_data = [
            ("Institution Name", "institution_name"),
            ("Description", "description"),
            ("Price", "price"),
            ("Phone Number", "phone_number"),
            ("Email", "email"),
            ("Website", "website"),
            ("Social Media", "social_media"),
            ("Business Registration Number(Optional)", "business_registration_number"),
        ]

        for label_text, field_name in field_data:
            layout.add_widget(Label(text=label_text, size_hint_x=0.4, font_size='16sp', color=(0, 0, 0, 1)))
            text_input = TextInput(multiline=False, size_hint_x=0.6, font_size='16sp')
            layout.add_widget(text_input)
            self.fields[field_name] = text_input

        # Location Dropdown
        layout.add_widget(Label(text="Location", size_hint_x=0.5, color=(0, 0, 0, 1)))

        self.location_dropdown = DropDown()
        self.location_button = Button(text='Select Location', size_hint_x=0.8)
        self.location_button.bind(on_release=self.location_dropdown.open)
        self.location_dropdown.bind(on_select=lambda instance, x: setattr(self.location_button, 'text', x))

        layout.add_widget(self.location_button)
        self.populate_location_dropdown()  # Fetch and populate location options

        # Service Dropdown
        layout.add_widget(Label(text="Service", size_hint_x=0.5, color=(0, 0, 0, 1)))

        self.service_dropdown = DropDown()
        self.service_button = Button(text='Select Service', size_hint_x=0.8)
        self.service_button.bind(on_release=self.service_dropdown.open)
        self.service_dropdown.bind(on_select=lambda instance, x: setattr(self.service_button, 'text', x))

        layout.add_widget(self.service_button)
        self.populate_service_dropdown()  # Fetch and populate service options

        # Profile Image Upload
        layout.add_widget(Label(text="Profile Image", font_size='16sp', color=(0, 0, 0, 1)))
        self.upload_btn = Button(text="Choose File")
        self.upload_btn.bind(on_press=self.choose_file)
        layout.add_widget(self.upload_btn)

        # Menu Image Upload
        layout.add_widget(Label(text="Menu Image", font_size='16sp', color=(0, 0, 0, 1)))
        self.upload_menu = Button(text="Choose File")
        self.upload_menu.bind(on_press=self.choose_file_menu)  # Fixed method name
        layout.add_widget(self.upload_menu)

        # Submit Button
        submit_btn = Button(text="Submit", size_hint=(1, None), height=50)
        submit_btn.bind(on_press=self.submit_form)

        layout.add_widget(Label())  # Spacer
        layout.add_widget(submit_btn)

        # Wrap form inside a ScrollView for better UX
        scroll_view = ScrollView(size_hint=(1, None), height=500)
        scroll_view.add_widget(layout)

        # Add form to the post vendor form container
        self.post_vendor_form.add_widget(scroll_view)

    def choose_file(self, instance):
        """Opens a file picker for profile image selection."""
        self.popup = FileChooserPopup(self.file_selected)
        self.popup.open()

    def file_selected(self, selection):
        if selection:
            self.selected_file = selection[0]
            self.upload_btn.text = "Profile Image Selected"

    def choose_file_menu(self, instance):
        """Opens a file picker for menu image selection."""
        self.popup = MenuFileChooserPopup(self.menu_file_selected)
        self.popup.open()

    def menu_file_selected(self, selection):
        if selection:
            self.selected_menu_file = selection[0]  # Store menu image separately
            self.upload_menu.text = "Menu Image Selected"  # Corrected button update

    def submit_form(self, instance):
        """Collect form data and send a POST request."""
        app = App.get_running_app()
        token = app.user_data.get("token", "")
        if not token:
            print("❌ User not authenticated.")
            return

        # Get user ID
        user_data = app.get_authenticated_data(f"api/user")
        if not user_data or "id" not in user_data:
            print("❌ Failed to fetch user data.")
            return

        user_id = user_data["id"]

        # Collect form data
        vendor_data = {key: field.text for key, field in self.fields.items()}
        vendor_data["user"] = user_id
        vendor_data["service"] = self.service_spinner.text
        vendor_data["location"] = self.location_spinner.text

        # Upload Profile Image (if selected)
        files = {}
        if self.file_chooser.selection:
            file_path = self.file_chooser.selection[0]
            files["profile_image"] = open(file_path, "rb")

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            "http://your-django-api.com/api/vendor/",
            data=vendor_data,
            files=files,
            headers=headers
        )

        if response.status_code == 201:
            print("✅ Vendor posted successfully!")
        else:
            print(f"❌ Error: {response.json()}")

    def populate_location_dropdown(self):
        """Fetch locations from the API and populate the dropdown."""
        api_url = 'http://localhost:8000/api/locations/'
        response = requests.get(api_url)

        if response.status_code == 200:
            locations = response.json()
            for location in locations:
                btn = Button(text=location['location'], size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn=btn: self.location_dropdown.select(btn.text))  # Fix late binding issue
                self.location_dropdown.add_widget(btn)
        else:
            print(f"Failed to retrieve locations. Status code: {response.status_code}")

    def populate_service_dropdown(self):
        """Fetch services from the API and populate the dropdown with only child categories."""
        api_url = 'http://localhost:8000/api/services/'
        response = requests.get(api_url)

        if response.status_code == 200:
            services = response.json()

            # Extract only child categories (where "parent" is not null)
            child_services = [service for service in services if service["parent"] is not None]

            for service in child_services:
                btn = Button(text=service['service'], size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn=btn: self.service_dropdown.select(btn.text))  # Fix late binding issue
                self.service_dropdown.add_widget(btn)
        else:
            print(f"Failed to retrieve services. Status code: {response.status_code}")

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