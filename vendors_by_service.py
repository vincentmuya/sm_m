from kivy.uix.screenmanager import Screen, SlideTransition
from navbar import Navbar
from kivy.lang import Builder

Builder.load_file('vendors_by_service.kv')


class VendorsByServiceScreen(Screen):
    """A blank screen for now, to be shown when 'View More' is clicked."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Navbar())
    pass