from django.db import transaction
from rest_framework import serializers
from BaseModules.models import Customer, Media
import stripe
from django.conf import settings
from rest_framework.exceptions import ValidationError


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CheckoutLinkRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class CustomerUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    progress = serializers.CharField(required=False)

    class Meta:
        model = Customer
        fields = ['progress', 'images', 'videos']

    def update(self, instance, validated_data):
        progress = validated_data.get('progress', instance.progress)
        instance.progress = progress

        if 'images' in validated_data:
            for image in validated_data.pop('images'):
                media_instance = Media.objects.create(file=image)
                instance.images.add(media_instance)

        if 'videos' in validated_data:
            for video in validated_data.pop('videos'):
                media_instance = Media.objects.create(file=video)
                instance.videos.add(media_instance)

        instance.save()
        return instance