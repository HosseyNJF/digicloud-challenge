from django.http import HttpResponse
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from apps.authentication.models import User
from apps.authentication.serializers import RegisterSerializer
from apps.authentication.views import RegisterView

SAMPLE_USER = {
    'username': 'john',
    'password': 'abc123@!@cba',
    'email': 'john@john.com',
    'name': 'John Doe',
}


class UserRegistrationIntegrationTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_correct_register(self):
        request = self.factory.post(reverse('auth_register'), SAMPLE_USER)
        response: HttpResponse = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        new_user_data = SAMPLE_USER.copy()
        new_user_data.pop('password')  # Password gets hashed in the db so no need to check that
        self.assertTrue(User.objects.filter(**new_user_data).exists())

    def test_using_correct_serializer(self):
        self.assertEqual(RegisterView.serializer_class, RegisterSerializer)


class RegisterSerializerTestCase(APITestCase):
    def setUp(self):
        self.serializer = RegisterSerializer()

    def test_correct_validation(self):
        serializer = RegisterSerializer(data=SAMPLE_USER)
        self.assertTrue(serializer.is_valid())

    def test_fail_on_duplicate_username(self):
        User.objects.create_user(**SAMPLE_USER)
        # Change the email to make it not duplicate, only the username should be tested
        other_user_data = SAMPLE_USER.copy()
        other_user_data['email'] = 'another@john.com'

        serializer = RegisterSerializer(data=other_user_data)
        self.assertFalse(serializer.is_valid())

    def test_fail_on_duplicate_email(self):
        User.objects.create_user(**SAMPLE_USER)
        # Change the username to make it not duplicate, only the email should be tested
        other_user_data = SAMPLE_USER.copy()
        other_user_data['username'] = 'another_john'

        serializer = RegisterSerializer(data=other_user_data)
        self.assertFalse(serializer.is_valid())

    def _test_fail_on_blank_field(self, field_name):
        data = SAMPLE_USER.copy()
        data[field_name] = ''
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_fail_on_blank_name(self):
        self._test_fail_on_blank_field('name')

    def test_fail_on_blank_username(self):
        self._test_fail_on_blank_field('username')

    def test_fail_on_blank_email(self):
        self._test_fail_on_blank_field('email')

    def test_fail_on_blank_password(self):
        self._test_fail_on_blank_field('password')
