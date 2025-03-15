import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user(username="john", password="pass1234")

    assert User.objects.count() == 1
    user = User.objects.first()
    assert user.username == "john"
    assert user.is_active is True
    assert user.is_staff is False