from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from trucker.models import Carrier, Driver, Vehicle


class LogEntryAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdriver", password="password123")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.carrier = Carrier.objects.create(
            name="Test Carrier",
            main_office_address="123 Main St",
            home_terminal_address="456 Terminal Rd"
        )

        self.driver = Driver.objects.create(
            user=self.user,
            license_number="TEST123",
            carrier=self.carrier
        )

        self.vehicle = Vehicle.objects.create(truck_number="T123", trailer_number="TR456")

    def test_create_log_entry(self):
        self.client.force_login(self.user)

        url = "/api/logs/" 
        data = {
            "date": "2023-10-05",
            "vehicle": self.vehicle.id,
            "start_odometer": 1000.5,
            "end_odometer": 1200.75,
            "remarks": "Test log",
            "signature": "Test Driver",
            "duty_statuses": [],
        }
        response = self.client.post(url, data, format="json", follow=True)
        self.assertEqual(response.status_code, 200)
