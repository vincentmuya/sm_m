from filter_widget import Filter
from filtered_vendors import FilteredVendorsScreen
from vendors import VendorsScreen
from header import Header
from navbar import Navbar
from search_widget import SearchWidget

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivymd.toast import toast
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

class LandingPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super(LandingPage, self).__init__(**kwargs)

        self.scroll_type = ['bars']
        self.bar_width = 10
        self.do_scroll_x = False
        self.do_scroll_y = True

        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        screen_height = Window.height

        self.vendors_grid = GridLayout(cols=3, spacing='10dp', size_hint_y=None, height=screen_height)
        self.vendors_grid.bind(minimum_height=self.vendors_grid.setter('height'))

        vendors_screen = VendorsScreen()
        vendors_screen.size_hint_y = None
        vendors_screen.height = screen_height
        self.vendors_grid.add_widget(vendors_screen)

        spacer = Widget(size_hint=(1, None), height=200)
        spacer_bottom = Widget(size_hint=(1, None), height=55)

        # ✅ Add widgets to scrollable content
        self.content_layout.add_widget(spacer)
        self.content_layout.add_widget(self.vendors_grid)
        self.content_layout.add_widget(spacer_bottom)

        scroll_view = ScrollView(size_hint=(1, 1), bar_width=20)
        scroll_view.add_widget(self.content_layout)

        self.add_widget(scroll_view)

        # Create and add the Header, fixed at the top of the screen
        header = Header(size_hint=(1, None), height=50)
        # Position header at the top using absolute coordinates
        header.pos_hint = {'top': 1}
        self.add_widget(header)

        # ✅ Fixed bottom navbar
        nav_bar = Navbar(size_hint=(1, None), height=50)
        nav_bar.pos_hint = {'x': 0, 'y': 0}
        self.add_widget(nav_bar)

    def on_pre_enter(self):
        """Update dropdown dynamically when entering the screen."""
        app = App.get_running_app()
        app.update_account_dropdown()
