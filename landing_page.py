from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from filter_widget import Filter  # Import the Filter widget
from vendors import VendorsScreen
from header import Header
from navbar import Navbar


class LandingPage(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_type = ['bars']
        self.bar_width = 10
        self.do_scroll_x = False  # Disable horizontal scrolling
        self.do_scroll_y = True   # Enable vertical scrolling

        # Create a vertical BoxLayout to stack the screens
        self.layout = BoxLayout(orientation='vertical', spacing=0, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        # Create and add the Filter widget
        filter_widget = Filter(filter_callback=self.apply_filter)

        # Create other screens (Header, VendorsScreen, Navbar) and wrap them
        header = self.wrap_screen(Header(), height=50)
        vendors = self.wrap_screen(VendorsScreen(), height=400)
        nav_bar = self.wrap_screen(Navbar(), height=100)

        # Add the wrapped screens to the layout
        self.layout.add_widget(header)
        self.layout.add_widget(filter_widget)
        self.layout.add_widget(vendors)
        self.layout.add_widget(nav_bar)

        # Set the layout as the content of the ScrollView
        self.add_widget(self.layout)

    def wrap_screen(self, screen, height):
        """
        Wrap a screen in a layout with a specific height.
        """
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=height)
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
