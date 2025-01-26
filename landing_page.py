from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from filter_widget import Filter  # Import the Filter widget
from vendors import VendorsScreen
from header import Header
from navbar import Navbar
from kivy.uix.floatlayout import FloatLayout


class LandingPage(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set up the ScrollView
        self.scroll_type = ['bars']
        self.bar_width = 10
        self.do_scroll_x = False  # Disable horizontal scrolling
        self.do_scroll_y = True  # Enable vertical scrolling

        # Create a layout to contain the content and wrap it in a scrollview
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None)  # The main content area
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # Create and add the Filter widget
        filter_widget = Filter(filter_callback=self.apply_filter)

        # Create other screens (Header, VendorsScreen) and wrap them
        header = self.wrap_screen(Header(), height=50)
        vendors = self.wrap_screen(VendorsScreen(), height=450)

        # Add the wrapped screens to the content layout
        content_layout.add_widget(header)
        content_layout.add_widget(filter_widget)
        content_layout.add_widget(vendors)

        # Create the ScrollView and add the content_layout inside it
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=10)
        scroll_view.add_widget(content_layout)

        # Create and add the navbar, fix it at the bottom of the screen
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}  # Position at the bottom of the screen

        # Add ScrollView and navbar to the FloatLayout
        self.add_widget(scroll_view)  # Add ScrollView with content on top
        self.add_widget(nav_bar)  # Add navbar at the bottom

    def wrap_screen(self, screen, height=None):
        """
        Wrap a screen in a layout with a specific height.
        """
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=height if height else screen.height)
        layout.add_widget(screen)
        return layout

    def apply_filter(self, location=None, service=None, price_range=None):
        """
        Method to handle the filter callback.
        Update vendors or perform other actions based on the filter criteria.
        """
        # Implement your logic here to update vendors based on filter criteria
        print(f"Applying filter with location={location}, service={service}, price_range={price_range}")
        # For example, you can update the VendorsScreen with filtered results
        vendors_screen = self.layout.children[2]  # Assuming VendorsScreen is the third child
        vendors_screen.update_vendors(location=location, service=service, price_range=price_range)
