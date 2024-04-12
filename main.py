from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from vendors import VendorsScreen


class MyApp(App):
    def build(self):
        # Create a ScreenManager
        screen_manager = ScreenManager()

        # Create and add VendorScreen instance to ScreenManager
        vendors_screen = VendorsScreen(name='vendors')
        screen_manager.add_widget(vendors_screen)

        return screen_manager

if __name__ == '__main__':
    MyApp().run()
