from django.test import TestCase
from django.utils.timezone import now

from apps.authentication.models import User
from apps.authentication.tests import SAMPLE_USER
from apps.scraper.models import Item, Interaction, Feed, Subscription
from apps.scraper.tests import SAMPLE_FEED


class ItemModelTestCase(TestCase):
    def test_is_seen_fail(self):
        item = Item()
        with self.assertRaises(AssertionError):
            _ = item.is_seen

    def test_is_seen_false(self):
        item = Item()
        item.user_interactions = []
        self.assertFalse(item.is_seen)

    def test_is_seen_true(self):
        item = Item()
        item.user_interactions = [Interaction(date_seen=now())]
        self.assertTrue(item.is_seen)

    def test_is_bookmarked_fail(self):
        item = Item()
        with self.assertRaises(AssertionError):
            _ = item.is_bookmarked

    def test_is_bookmarked_false(self):
        item = Item()
        item.user_interactions = []
        self.assertFalse(item.is_bookmarked)

    def test_is_bookmarked_true(self):
        item = Item()
        item.user_interactions = [Interaction(date_bookmarked=now())]
        self.assertTrue(item.is_bookmarked)

    def test_comment_fail(self):
        item = Item()
        with self.assertRaises(AssertionError):
            _ = item.comment

    def test_comment_correct(self):
        item = Item()
        item.user_interactions = [Interaction(comment="test")]
        self.assertEqual(item.comment, "test")

    def test_for_user_scope(self):
        user = User.objects.create(**SAMPLE_USER)
        allowed_feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        disallowed_feed = Feed.objects.create(url='https://test2.com', **SAMPLE_FEED)
        allowed_item = Item(
            feed=allowed_feed
        )
        disallowed_item = Item(
            feed=disallowed_feed
        )
        Item.objects.bulk_create([
            allowed_item,
            disallowed_item,
        ])
        allowed_feed.users.add(user)

        allowed_items = Item.objects.for_user(user).all()
        self.assertListEqual(list(allowed_items), [allowed_item])

    def test_bookmarks_scope(self):
        user = User.objects.create(**SAMPLE_USER)
        feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        allowed_item = Item(
            feed=feed
        )
        non_bookmarked_item = Item(
            feed=feed
        )
        unseen_item = Item(
            feed=feed
        )
        Item.objects.bulk_create([
            allowed_item,
            non_bookmarked_item,
            unseen_item
        ])
        Interaction.objects.create(
            user=user,
            item=allowed_item,
            date_bookmarked=now(),
        )
        Interaction.objects.create(
            user=user,
            item=non_bookmarked_item,
        )

        allowed_items = Item.objects.bookmarks(user).all()
        self.assertListEqual(list(allowed_items), [allowed_item])

    def test_unread_count(self):
        user = User.objects.create(**SAMPLE_USER)
        feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        seen_item = Item(
            feed=feed
        )
        unseen_item_1 = Item(
            feed=feed
        )
        unseen_item_2 = Item(
            feed=feed
        )
        Item.objects.bulk_create([
            seen_item,
            unseen_item_1,
            unseen_item_2,
        ])
        Interaction.objects.create(
            user=user,
            item=seen_item,
        )
        Subscription.objects.create(
            user=user,
            feed=feed,
        )

        self.assertEqual(Item.objects.unread_item_count(user), 2)

    def test_new_interact_with_user(self):
        user = User.objects.create(**SAMPLE_USER)
        feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        item = Item.objects.create(
            feed=feed
        )
        interaction = item.interact_with_user(user)
        self.assertEqual(interaction.user, user)
        self.assertEqual(interaction.item, item)
        self.assertIsNotNone(interaction.date_seen)

    def test_existing_interact_with_user(self):
        user = User.objects.create(**SAMPLE_USER)
        feed = Feed.objects.create(url='https://test.com', **SAMPLE_FEED)
        item = Item.objects.create(
            feed=feed
        )
        current_interaction = Interaction.objects.create(
            user=user,
            item=item,
        )
        new_interaction = item.interact_with_user(user)
        self.assertEqual(new_interaction, current_interaction)
