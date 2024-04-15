from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from vendors import VendorsScreen
from vendor_details import VendorDetailsScreen
from navbar import Navbar


class MyApp(App):
    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Create and add VendorScreen instance to ScreenManager
        vendors_screen = VendorsScreen(name='vendors')
        screen_manager.add_widget(vendors_screen)

        # Create the VendorDetailsScreen instance and add it to the ScreenManager
        vendor_details_screen = VendorDetailsScreen(name='vendor_details')
        screen_manager.add_widget(vendor_details_screen)

        # Create the Navbar screen
        navbar_screen = Screen(name='navbar')
        navbar_screen.add_widget(Navbar())  # Add Navbar widget to the screen

        # Add the Navbar screen to the ScreenManager
        screen_manager.add_widget(navbar_screen)

        return screen_manager


if __name__ == '__main__':
    MyApp().run()
