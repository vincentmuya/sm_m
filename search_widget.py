import requests
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class SearchWidget(BoxLayout):
    def __init__(self, search_callback, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=50, padding=[10, 5], spacing=10, **kwargs)

        # Search input field
        self.search_input = TextInput(hint_text="Search vendors...", size_hint=(0.8, 1))

        # Search button
        self.search_button = Button(text="Search", size_hint=(0.2, 1))
        self.search_button.bind(on_press=lambda instance: self.search_vendors(search_callback))

        # Add input and button to layout
        self.add_widget(self.search_input)
        self.add_widget(self.search_button)

    def search_vendors(self, search_callback):
        search_query = self.search_input.text.strip()
        if search_query:
            print(f"Searching for: {search_query}")

            response = requests.get(f"http://localhost:8000/api/vendor/?search={search_query}")

            # print("API Response:", response.text)  # Debugging

            if response.status_code == 200:
                try:
                    vendors = response.json()
                    print(f"Found {len(vendors)} vendors")
                    search_callback(vendors, search_query)  # Pass vendors and Query to callback function
                except requests.exceptions.JSONDecodeError:
                    print("Error: Response is not valid JSON")
            else:
                print(f"Error fetching vendor data: {response.status_code}")