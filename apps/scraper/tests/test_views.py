from unittest import mock
from unittest.mock import Mock

from django.test import TestCase
from rest_framework.serializers import Serializer

from apps.scraper.serializers import SubscriptionSerializer, SubscriptionCreationSerializer, FeedSerializer, \
    CommentSerializer, ItemSerializer
from apps.scraper.views import SubscriptionViewSet, FeedViewSet, ItemViewSet


class ViewsTestCase(TestCase):

    def test_subscription_list_using_correct_serializer(self):
        viewset = SubscriptionViewSet()
        viewset.action = 'list'
        self.assertEqual(viewset.get_serializer_class(), SubscriptionSerializer)

    def test_subscription_create_using_correct_serializer(self):
        viewset = SubscriptionViewSet()
        viewset.action = 'create'
        self.assertEqual(viewset.get_serializer_class(), SubscriptionCreationSerializer)

    @mock.patch('apps.scraper.models.Subscription.objects.for_user')
    def test_subscription_viewset_using_correct_queryset(self, mock_for_user: Mock):
        viewset = SubscriptionViewSet()
        viewset.request = Mock()

        viewset.get_queryset()
        mock_for_user.assert_called_once()

    def test_feed_viewset_using_correct_serializer(self):
        self.assertEqual(FeedViewSet().get_serializer_class(), FeedSerializer)

    @mock.patch('apps.scraper.models.Feed.objects.for_user')
    def test_feed_viewset_using_correct_queryset(self, mock_for_user: Mock):
        viewset = FeedViewSet()
        viewset.request = Mock()

        viewset.get_queryset()
        mock_for_user.assert_called_once()

    def test_item_comment_using_correct_serializer(self):
        viewset = ItemViewSet()
        viewset.action = 'comment'
        self.assertEqual(viewset.get_serializer_class(), CommentSerializer)

    def test_item_bookmark_using_empty_serializer(self):
        viewset = ItemViewSet()
        viewset.action = 'bookmark'
        self.assertEqual(viewset.get_serializer_class(), Serializer)

    def test_item_remove_bookmark_using_empty_serializer(self):
        viewset = ItemViewSet()
        viewset.action = 'remove_bookmark'
        self.assertEqual(viewset.get_serializer_class(), Serializer)

    def test_item_viewset_using_correct_serializer(self):
        viewset = ItemViewSet()
        viewset.action = 'list'
        self.assertEqual(viewset.get_serializer_class(), ItemSerializer)

    @mock.patch('apps.scraper.models.Item.objects')
    def test_item_viewset_using_correct_queryset(self, mock_objects: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.action = 'list'

        mock_objects.for_user.return_value = mock_objects
        mock_objects.order_by.return_value = mock_objects

        viewset.get_queryset()
        mock_objects.for_user.assert_called_once()
        mock_objects.order_by.assert_called_once_with('-pubDate')

    @mock.patch('apps.scraper.models.Item.objects')
    def test_item_bookmarks_using_correct_queryset(self, mock_objects: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.action = 'bookmarks'

        mock_objects.for_user.return_value = mock_objects
        mock_objects.order_by.return_value = mock_objects
        mock_objects.bookmarks.return_value = mock_objects

        viewset.get_queryset()
        mock_objects.for_user.assert_called_once()
        mock_objects.order_by.assert_called_once_with('-pubDate')
        mock_objects.bookmarks.assert_called_once()

    @mock.patch('apps.scraper.views.viewsets.GenericViewSet.get_object')
    def test_item_actions_using_correct_object(self, mock_get_object: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        actions = ['comment', 'bookmark', 'remove_bookmark']
        for action in actions:
            viewset.action = action
            viewset.get_object()
            mock_get_object().interact_with_user.assert_called_once()
            mock_get_object().interact_with_user.reset_mock()

    @mock.patch('apps.scraper.views.viewsets.GenericViewSet.get_object')
    def test_item_viewset_using_correct_object(self, mock_get_object: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.action = 'list'

        viewset.get_object()
        mock_get_object().interact_with_user.assert_not_called()

    @mock.patch('apps.scraper.views.mixins.RetrieveModelMixin.retrieve')
    @mock.patch('apps.scraper.views.ItemViewSet.get_object')
    def test_item_retrieve_interacts_with_user(self, mock_get_object: Mock, mock_retrieve: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.retrieve(viewset.request)

        mock_get_object().interact_with_user.assert_called_once()
        mock_retrieve.assert_called_once()

    @mock.patch('apps.scraper.models.Item.objects.unread_item_count')
    def test_item_unread_count_reads_correctly(self, mock_unread_item_count: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.unread_count(viewset.request)

        mock_unread_item_count.assert_called_once()

    @mock.patch('apps.scraper.views.ItemViewSet.get_object')
    def test_item_add_bookmark_works(self, mock_get_object: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.bookmark(viewset.request)

        mock_get_object().add_bookmark.assert_called_once()

    @mock.patch('apps.scraper.views.ItemViewSet.get_object')
    def test_item_remove_bookmark_works(self, mock_get_object: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.remove_bookmark(viewset.request)

        mock_get_object().remove_bookmark.assert_called_once()

    @mock.patch('apps.scraper.views.mixins.ListModelMixin.list')
    def test_item_bookmark_list_calls_super(self, mock_list: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.bookmarks(viewset.request)

        mock_list.assert_called_once()

    @mock.patch('apps.scraper.views.ItemViewSet.get_object')
    @mock.patch('apps.scraper.views.ItemViewSet.get_serializer')
    def test_item_comment_calls_serializer(self, mock_get_serializer: Mock, mock_get_object: Mock):
        viewset = ItemViewSet()
        viewset.request = Mock()
        viewset.comment(viewset.request)

        mock_get_serializer.assert_called_once()
        mock_get_object.assert_called_once()
        mock_get_serializer().is_valid.assert_called_once()
        mock_get_serializer().save.assert_called_once()
