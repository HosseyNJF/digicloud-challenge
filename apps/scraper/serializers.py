from rest_framework import serializers

from apps.scraper.models import Subscription, Feed, Item, Interaction


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    is_seen = serializers.ReadOnlyField()
    is_bookmarked = serializers.ReadOnlyField()
    comment = serializers.ReadOnlyField()

    class Meta:
        model = Item
        exclude = ('viewers',)


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    # Defining this relation manually because it's a reverse relation and should be explicitly
    # declared in the `fields` attribute of the `Meta` class, and it's impossible (because we
    # already use the `excluded` attribute).
    items = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='item-detail',
        read_only=True
    )

    class Meta:
        model = Feed
        exclude = ('users', 'periodic_task',)


class SubscriptionCreationSerializer(serializers.Serializer):
    feed_url = serializers.URLField(write_only=True)
    feed = FeedSerializer(read_only=True)

    def create(self, validated_data):
        try:
            feed = Feed.objects.get(url=validated_data['feed_url'])
        except Feed.DoesNotExist:
            feed = Feed.objects.create_from_url(validated_data['feed_url'])
            # TODO: possible race condition when two people try to create the same feed at the same time!

        return Subscription.objects.create(
            user=self.context['request'].user,
            feed=feed,
        )

    def update(self, instance, validated_data):
        raise NotImplementedError  # We have to have this because of the parent's ABC constrains


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Subscription
        fields = ('url', 'feed', 'date_created')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction
        fields = ('comment',)
