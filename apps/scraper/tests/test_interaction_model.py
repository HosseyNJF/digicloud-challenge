from unittest import mock
from unittest.mock import Mock

from django.test import TestCase
from django.utils.timezone import now

from apps.scraper.models import Interaction


class InteractionModelTestCase(TestCase):

    @mock.patch('apps.scraper.models.Interaction.save')
    def test_add_bookmark(self, mock_save: Mock):
        interaction = Interaction()
        interaction.add_bookmark()

        self.assertIsNotNone(interaction.date_bookmarked)
        mock_save.assert_called_once()

    @mock.patch('apps.scraper.models.Interaction.save')
    def test_remove_bookmark(self, mock_save: Mock):
        interaction = Interaction(date_bookmarked=now())
        interaction.remove_bookmark()

        self.assertIsNone(interaction.date_bookmarked)
        mock_save.assert_called_once()
