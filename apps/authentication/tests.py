from django.http import HttpResponse
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from apps.authentication.models import User
from apps.authentication.serializers import RegisterSerializer
from apps.authentication.views import RegisterView


class UserRegistrationIntegrationTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.dummy_user = {
            'username': 'john',
            'password': 'abc123@!@cba',
            'email': 'john@john.com',
            'name': 'John Doe',
        }

    def test_correct_register(self):
        request = self.factory.post(reverse('auth_register'), self.dummy_user)
        response: HttpResponse = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.dummy_user.pop('password')  # Password gets hashed in the db so no need to check that
        self.assertTrue(User.objects.filter(**self.dummy_user).exists())

    def test_using_correct_serializer(self):
        self.assertEqual(RegisterView.serializer_class, RegisterSerializer)


class RegisterSerializerTestCase(APITestCase):
    def setUp(self):
        self.serializer = RegisterSerializer()
        self.dummy_user = {
            'username': 'john',
            'password': 'abc123@!@cba',
            'email': 'john@john.com',
            'name': 'John Doe',
        }

    def test_correct_validation(self):
        serializer = RegisterSerializer(data=self.dummy_user)
        self.assertTrue(serializer.is_valid())

    def test_fail_on_duplicate_username(self):
        User.objects.create_user(**self.dummy_user)
        # Change the email to make it not duplicate, only the username should be tested
        self.dummy_user['email'] = 'another@john.com'

        serializer = RegisterSerializer(data=self.dummy_user)
        self.assertFalse(serializer.is_valid())

    def test_fail_on_duplicate_email(self):
        User.objects.create_user(**self.dummy_user)
        # Change the username to make it not duplicate, only the email should be tested
        self.dummy_user['username'] = 'another_john'

        serializer = RegisterSerializer(data=self.dummy_user)
        self.assertFalse(serializer.is_valid())

    def _test_fail_on_blank_field(self, field_name):
        self.dummy_user[field_name] = ''
        serializer = RegisterSerializer(data=self.dummy_user)
        self.assertFalse(serializer.is_valid())

    def test_fail_on_blank_name(self):
        self._test_fail_on_blank_field('name')

    def test_fail_on_blank_username(self):
        self._test_fail_on_blank_field('username')

    def test_fail_on_blank_email(self):
        self._test_fail_on_blank_field('email')

    def test_fail_on_blank_password(self):
        self._test_fail_on_blank_field('password')
