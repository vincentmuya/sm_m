from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from vendors import VendorsScreen
from vendor_details import VendorDetailsScreen
from landing_page import LandingPage


class MyApp(App):
    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Create and add the landing page screen
        landing_page_screen = Screen(name='landing_page')
        landing_page = LandingPage()
        landing_page_screen.add_widget(landing_page)
        screen_manager.add_widget(landing_page_screen)

        # Create the VendorDetailsScreen instance and add it to the ScreenManager
        vendor_details_screen = VendorDetailsScreen(name='vendor_details')
        screen_manager.add_widget(vendor_details_screen)

        return screen_manager


if __name__ == '__main__':
    MyApp().run()
