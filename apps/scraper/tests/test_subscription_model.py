from django.test import TestCase

from django.test import TestCase

from apps.authentication.models import User
from apps.authentication.tests import SAMPLE_USER
from apps.scraper.models import Feed, Subscription
from apps.scraper.tests import SAMPLE_FEED


class SubscriptionModelTestCase(TestCase):

    def test_for_user_scope(self):
        user = User.objects.create_user(**SAMPLE_USER)
        user2_data = SAMPLE_USER.copy()
        user2_data['username'] = 'another'
        user2_data['email'] = 'another@john.com'
        user2 = User.objects.create_user(**user2_data)
        feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)

        allowed_subscription = Subscription.objects.create(
            user=user,
            feed=feed,
        )
        disallowed_subscription = Subscription.objects.create(
            user=user2,
            feed=feed,
        )

        allowed_subscriptions = Subscription.objects.for_user(user).all()
        self.assertListEqual(list(allowed_subscriptions), [allowed_subscription])
