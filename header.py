from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the orientation of the Header to vertical
        self.orientation = 'vertical'

        # Apply the pink background
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black color (RGBA)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # Add a Label with the "What are you looking for?" text
        label = Label(text="Sherehe Mall.\nGet Services From The Best Vendors", size_hint_y=None, height=50)
        self.add_widget(label)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
