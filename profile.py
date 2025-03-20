from navbar import Navbar
from header import Header
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
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivymd.toast import toast

Builder.load_file('profile.kv')

class ProfileVendorCard(BoxLayout):
    def __init__(self, institution_name, price, image_source, vendor_id, slug, service, location, update_callback, delete_callback, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=320, spacing=0, padding=10)

        self.vendor_id = vendor_id
        self.slug = slug
        self.delete_callback = delete_callback

        # Vendor Image (lowered)
        self.image = AsyncImage(source=image_source, size_hint_y=None, height=130)
        self.image.bind(on_touch_down=self.on_touch)
        self.add_widget(self.image)

        # Vendor Details
        self.add_widget(Label(text=f"[b]{institution_name}[/b]", markup=True, size_hint_y=None, height=30, color=(0, 0, 0, 1), on_touch_down=self.on_touch))
        self.add_widget(Label(text=f"Service: {service}", size_hint_y=None, height=20, color=(0, 0, 0, 1), on_touch_down=self.on_touch))
        self.add_widget(Label(text=f"Location: {location}", size_hint_y=None, height=20, color=(0, 0, 0, 1), on_touch_down=self.on_touch))
        self.add_widget(Label(text=f"Price: {price}", size_hint_y=None, height=20, color=(0, 0, 0, 1), on_touch_down=self.on_touch))

        # Update and Delete Buttons
        self.update_button = Button(text="Update", size_hint_y=None, height=40, background_color=(0, 0.5, 1, 1))
        self.update_button.bind(on_press=lambda instance: update_callback(self.vendor_id))
        self.add_widget(self.update_button)

        # Delete Button (calls confirmation popup)
        self.delete_button = Button(text="Delete", size_hint_y=None, height=40, background_color=(1, 0, 0, 1))
        self.delete_button.bind(on_press=self.confirm_delete_popup)
        self.add_widget(self.delete_button)

    def confirm_delete_popup(self, instance):
        """Show confirmation popup before deleting vendor."""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        popup_label = Label(text=f"Are you sure you want to delete this vendor?")
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        # Confirm Button
        confirm_button = Button(text="Yes", background_color=(1, 0, 0, 1))
        confirm_button.bind(on_press=lambda x: self.confirm_delete(self.vendor_id, popup))  # ✅ Calls delete on confirm

        # Cancel Button
        cancel_button = Button(text="No", background_color=(0, 1, 0, 1))
        cancel_button.bind(on_press=lambda x: popup.dismiss())

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(button_layout)

        popup = Popup(title="Confirm Deletion", content=popup_layout, size_hint=(None, None), size=(300, 200))
        popup.open()

    def confirm_delete(self, vendor_id, popup):
        """Closes popup and calls delete_vendor."""
        popup.dismiss()
        if self.delete_callback:  # ✅ Ensure delete_callback exists before calling
            self.delete_callback(vendor_id)
        else:
            print("Error: delete_callback not found")

    def on_touch(self, instance, touch):
        """Detect touch and call view_vendor only when the image is clicked."""
        if instance.collide_point(*touch.pos):  # Ensure touch is inside the image
            self.view_vendor()
            return True  # Consume touch event
        return False  # Allow other interactions

    def view_vendor(self):
        """Fetch vendor details and navigate to vendor details screen."""
        vendor_id = self.vendor_id
        api_url = f"http://localhost:8000/api/vendor/{vendor_id}/{self.slug}/"
        response = requests.get(api_url)

        if response.status_code == 200:
            vendor_details = response.json()
            app = App.get_running_app()
            vendor_details_screen = app.root.get_screen('vendor_details')
            vendor_details_screen.load_details(vendor_details)

            app.root.transition = SlideTransition(direction='left')
            app.root.current = 'vendor_details'
        else:
            print("Failed to fetch vendor details.")

class ProfileScreen(Screen):
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
        self.vendor_grid = GridLayout(cols=3, size_hint_y=None, spacing='10dp')

        # Spacer widget to add space after the header
        top_spacer = Widget(size_hint=(1, None), height=45)
        spacer = Widget(size_hint=(1, None), height=15)
        bottom_spacer = Widget(size_hint=(1, None), height=650)

        self.content_layout.add_widget(top_spacer)
        self.content_layout.add_widget(self.search_widget)
        self.content_layout.add_widget(self.filter_widget)
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.vendor_grid)
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

        #Use a proxy button instead of moving the original button
        app = App.get_running_app()
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(150, 40), pos=(650, 560))
        #Create a proxy button
        self.account_proxy_button = Button(text=app.account_button.text)

        #Open dropdown manually when proxy button is clicked
        self.account_proxy_button.bind(on_release=self.open_account_dropdown)

        #Add proxy button instead of the real one
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

    def load_profile_vendors(self, user_vendors, username):
        # print(f"Loading {len(user_vendors)} User Vendors ...")
        self.vendor_grid.clear_widgets()

        profile_label = Label(
            text=f"{username}'s Profile ",
            size_hint_y=None,
            height=5,
            font_size="15sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        location_label2 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        location_label3 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )

        self.vendor_grid.add_widget(location_label2)
        self.vendor_grid.add_widget(profile_label)
        self.vendor_grid.add_widget(location_label3)

        vendors_label = Label(
            text=f"Vendors Posted By {username}",
            size_hint_y=None,
            height=5,
            font_size="15sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        vendors_label2 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )
        vendors_label3 = Label(
            text="",
            size_hint_y=None,
            height=5,
            font_size="2sp",
            color=(0, 0, 0, 1),
            bold=True
        )

        self.vendor_grid.add_widget(vendors_label2)
        self.vendor_grid.add_widget(vendors_label)
        self.vendor_grid.add_widget(vendors_label3)

        # Fetch all services and locations to map their IDs to names
        services_response = requests.get('http://localhost:8000/api/services/')
        locations_response = requests.get('http://localhost:8000/api/locations/')

        if services_response.status_code == 200:
            services = {service['id']: service['service'] for service in services_response.json()}
        else:
            services = {}

        if locations_response.status_code == 200:
            locations = {location['id']: location['location'] for location in locations_response.json()}
        else:
            locations = {}

        for vendor in user_vendors:
            full_image_url = f"http://localhost:8000{vendor['profile_image']}"

            # Get the location name
            location_id = vendor.get('location')
            location_name = locations.get(location_id, "Unknown Location")

            # Get the service name
            service_id = vendor.get('service')
            service_name = services.get(service_id, "Unknown Service")

            # Use ProfileVendorCard
            vendor_card = ProfileVendorCard(
                institution_name=vendor['institution_name'],
                price=str(vendor['price']),
                image_source=full_image_url,
                vendor_id=str(vendor['id']),
                slug=vendor['slug'],
                service=service_name,
                location=location_name,
                update_callback=self.update_vendor,
                delete_callback=self.delete_vendor
            )
            self.vendor_grid.add_widget(vendor_card)

    def update_vendor(self, vendor_id):
        print(f"Update vendor {vendor_id}")
        # Here you can open a form popup to edit vendor details
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Update feature coming soon!"))

        close_button = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_button)

        popup = Popup(title="Update Vendor", content=content, size_hint=(None, None), size=(400, 200))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def delete_vendor(self, vendor_id):
        """Deletes vendor and refreshes the list."""
        print(f"Deleting vendor {vendor_id}...")

        url = f"http://localhost:8000/api/vendor/delete/{vendor_id}/"
        response = requests.delete(url)

        if response.status_code == 204:
            print(f"Vendor {vendor_id} deleted successfully.")
            app = App.get_running_app()
            app.root.current = "landing_page"
            toast("Vendor Deleted successfully!")
        else:
            print(f"Failed to delete vendor {vendor_id}. Status code: {response.status_code}")

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
