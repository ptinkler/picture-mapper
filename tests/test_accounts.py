import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
class TestSignUp:
    data = {"username": "carol", "password1": "a-long-unusual-pw-9", "password2": "a-long-unusual-pw-9"}

    def test_creates_the_user_and_logs_them_in(self, client):
        response = client.post(reverse("signup"), self.data)
        assert response.status_code == 302
        assert response.url == reverse("profile")
        assert get_user_model().objects.filter(username="carol").exists()
        assert client.get(reverse("profile")).status_code == 200

    def test_password_mismatch(self, client):
        response = client.post(reverse("signup"), {**self.data, "password2": "different"})
        assert response.status_code == 200
        assert not get_user_model().objects.exists()

    def test_weak_password_rejected(self, client):
        response = client.post(reverse("signup"), {**self.data, "password1": "12345", "password2": "12345"})
        assert response.status_code == 200
        assert not get_user_model().objects.exists()

    def test_closed_registration(self, client, settings):
        settings.REGISTRATION_OPEN = False
        assert "closed" in client.get(reverse("signup")).content.decode()
        client.post(reverse("signup"), self.data)
        assert not get_user_model().objects.exists()


@pytest.mark.django_db
def test_login_and_logout(client, user):
    assert client.post(reverse("login"), {"username": "alice", "password": "pw-alice-123"}).status_code == 302
    assert client.get(reverse("profile")).status_code == 200
    assert client.post(reverse("logout")).status_code == 302
    assert client.get(reverse("profile")).status_code == 302


@pytest.mark.django_db
def test_logout_is_post_only(client_alice):
    assert client_alice.get(reverse("logout")).status_code == 405
