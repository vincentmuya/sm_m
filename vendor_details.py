from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
import requests

Builder.load_file('vendor_details.kv')

class VendorDetailsScreen(Screen):
    institution_name = StringProperty()
    price = StringProperty()
    image_source = StringProperty()
    service = StringProperty()
    description = StringProperty()
    location = StringProperty()
    phone_number = StringProperty()
    email = StringProperty()
    website = StringProperty()
    social_media = StringProperty()
    slug = StringProperty()
    vendor_id = StringProperty()

    def load_details(self, vendor_details):
        print("Loading vendor_details...")
        print("Vendor Details:", vendor_details)

        self.institution_name = vendor_details['institution_name']
        self.price = str(vendor_details['price'])
        self.description = vendor_details['description']
        self.phone_number = str(vendor_details['phone_number'])
        self.location = str(vendor_details['location'])
        self.email = vendor_details['email']
        self.website = vendor_details['website']
        self.social_media = vendor_details['social_media']
        self.image_source = f"http://localhost:8000{vendor_details['profile_image']}"
        self.slug = vendor_details['slug']
        self.vendor_id = str(vendor_details['id'])

        # Fetch service details from the API using service ID
        service_id = vendor_details['service']
        service_name = 'Unknown Service'

        # Fetch all services from the services API
        services_response = requests.get('http://localhost:8000/api/services/')
        if services_response.status_code == 200:
            services = services_response.json()
            print("Services:", services)

            # Find the service name corresponding to the vendor's service_id
            for service in services:
                if service['id'] == service_id:
                    service_name = service['service']
                    break

        self.service = service_name

        # Fetch location details from the API using service ID
        location_id = vendor_details['location']
        location_name = 'Unknown Service'

        # Fetch all services from the services API
        locations_response = requests.get('http://localhost:8000/api/locations/')
        if locations_response.status_code == 200:
            locations = locations_response.json()
            print("Services:", locations)

            # Find the service name corresponding to the vendor's location_id
            for location in locations:
                if location['id'] == location_id:
                    location_name = location['location']
                    break

        self.location = location_name

        # Update UI elements with fetched data
        self.ids.institution_name_label.text = self.institution_name
        self.ids.price_label.text = self.price
        self.ids.description_label.text = self.description
        self.ids.service_label.text = self.service
        self.ids.phone_number_label.text = self.phone_number
        self.ids.email_label.text = self.email
        self.ids.website_label.text = self.website
        self.ids.social_media_label.text = self.social_media

        # Ensure all properties are updated
        self.property('institution_name').dispatch(self)
        self.property('price').dispatch(self)
        self.property('description').dispatch(self)
        self.property('location').dispatch(self)
        self.property('service').dispatch(self)
        self.property('phone_number').dispatch(self)
        self.property('email').dispatch(self)
        self.property('website').dispatch(self)
        self.property('social_media').dispatch(self)
