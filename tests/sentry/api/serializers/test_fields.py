from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from sentry.api.serializers.rest_framework import ActorField, ListField
from sentry.models import Team, User
from sentry.testutils import TestCase


class ChildSerializer(serializers.Serializer):
    b_field = serializers.CharField(max_length=64)
    d_field = serializers.CharField(max_length=64)


class DummySerializer(serializers.Serializer):
    a_field = ListField(child=ChildSerializer(), required=False, allow_null=False)
    actor_field = ActorField(required=False)


class TestListField(TestCase):
    def test_simple(self):
        data = {"a_field": [{"b_field": "abcdefg", "d_field": "gfedcba"}]}

        serializer = DummySerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == {
            "a_field": [{"b_field": "abcdefg", "d_field": "gfedcba"}]
        }

    def test_allow_null(self):
        data = {"a_field": [None]}

        serializer = DummySerializer(data=data)
        assert not serializer.is_valid()
        assert serializer.errors == {
            "a_field": [ErrorDetail(string="This field may not be null.", code="null")]
        }

    def test_child_validates(self):
        data = {"a_field": [{"b_field": "abcdefg"}]}

        serializer = DummySerializer(data=data)
        assert not serializer.is_valid()
        assert serializer.errors == {
            "a_field": {
                {"d_field": [ErrorDetail(string="This field is required.", code="required")]}
            }
        }


class TestActorField(TestCase):
    def test_simple(self):
        data = {"actor_field": "user:1"}

        serializer = DummySerializer(data=data)
        assert serializer.is_valid()

        assert serializer.validated_data["actor_field"].type == User
        assert serializer.validated_data["actor_field"].id == 1

    def test_legacy_user_fallback(self):
        data = {"actor_field": "1"}

        serializer = DummySerializer(data=data)
        assert serializer.is_valid()

        assert serializer.validated_data["actor_field"].type == User
        assert serializer.validated_data["actor_field"].id == 1

    def test_team(self):
        data = {"actor_field": "team:1"}

        serializer = DummySerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["actor_field"].type == Team
        assert serializer.validated_data["actor_field"].id == 1

    def test_validates(self):
        data = {"actor_field": "foo:1"}

        serializer = DummySerializer(data=data)
        assert not serializer.is_valid()
        assert serializer.errors == {"actor_field": ["Unknown actor input"]}
