from decimal import Decimal

import pytest
from django.urls import reverse

from pictures.models import Picture

GPS = ("N", (48.0, 51.0, 30.0), "E", (2.0, 17.0, 40.0))


def upload(client, make_image, **fields):
    data = {"title": "Paris", "description": "", **fields}
    if "image" not in data:
        data["image"] = make_image()
    return client.post(reverse("upload_picture"), data)


@pytest.mark.django_db
class TestUpload:
    def test_with_a_clicked_location(self, client_alice, image, user):
        response = upload(client_alice, image, latitude="51.5", longitude="-0.12")
        assert response.status_code == 302
        picture = Picture.objects.get()
        assert picture.owner == user
        assert (picture.latitude, picture.longitude) == (Decimal("51.5"), Decimal("-0.12"))
        assert (picture.width, picture.height) == (40, 30)

    def test_location_from_exif_when_blank(self, client_alice, image):
        upload(client_alice, image, image=image(gps=GPS))
        picture = Picture.objects.get()
        assert picture.latitude == Decimal("48.858333")
        assert picture.longitude == Decimal("2.294444")

    def test_clicked_location_wins_over_exif(self, client_alice, image):
        upload(client_alice, image, image=image(gps=GPS), latitude="10", longitude="20")
        assert Picture.objects.get().latitude == Decimal("10")

    def test_no_location_anywhere_is_an_error(self, client_alice, image):
        response = upload(client_alice, image)
        assert response.status_code == 200
        assert "Click the map" in response.content.decode()
        assert not Picture.objects.exists()

    @pytest.mark.parametrize(("lat", "lon"), [("91", "0"), ("-91", "0"), ("0", "181"), ("0", "-181")])
    def test_out_of_range_location(self, client_alice, image, lat, lon):
        response = upload(client_alice, image, latitude=lat, longitude=lon)
        assert response.status_code == 200
        assert not Picture.objects.exists()

    def test_not_an_image(self, client_alice):
        from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: PLC0415

        bad = SimpleUploadedFile("x.jpg", b"definitely not a jpeg", content_type="image/jpeg")
        response = client_alice.post(
            reverse("upload_picture"), {"title": "x", "image": bad, "latitude": "1", "longitude": "1"}
        )
        assert response.status_code == 200
        assert not Picture.objects.exists()

    def test_too_large(self, client_alice, image, settings):
        settings.MAX_UPLOAD_MB = 0
        response = upload(client_alice, image, latitude="1", longitude="1")
        assert "larger than" in response.content.decode()
        assert not Picture.objects.exists()

    def test_needs_login(self, client, image):
        response = upload(client, image, latitude="1", longitude="1")
        assert response.status_code == 302
        assert response.url.startswith(reverse("login"))
        assert not Picture.objects.exists()


@pytest.mark.django_db
class TestOwnership:
    def test_edit_own(self, client_alice, picture):
        response = client_alice.post(
            reverse("edit_picture", args=[picture.pk]), {"title": "New", "latitude": "1", "longitude": "2"}
        )
        assert response.status_code == 302
        picture.refresh_from_db()
        assert (picture.title, picture.latitude) == ("New", Decimal("1"))

    def test_edit_keeps_the_image_and_location_when_not_changed(self, client_alice, picture):
        old_name = picture.image.name
        client_alice.post(
            reverse("edit_picture", args=[picture.pk]),
            {"title": "New", "latitude": picture.latitude, "longitude": picture.longitude},
        )
        picture.refresh_from_db()
        assert picture.image.name == old_name

    def test_cannot_edit_someone_elses(self, client, other, picture):
        client.force_login(other)
        url = reverse("edit_picture", args=[picture.pk])
        assert client.get(url).status_code == 404
        assert client.post(url, {"title": "Hijack", "latitude": "1", "longitude": "1"}).status_code == 404
        picture.refresh_from_db()
        assert picture.title == "Tower"

    def test_cannot_delete_someone_elses(self, client, other, picture):
        client.force_login(other)
        assert client.post(reverse("delete_picture", args=[picture.pk])).status_code == 404
        assert Picture.objects.exists()

    def test_delete_needs_post(self, client_alice, picture):
        url = reverse("delete_picture", args=[picture.pk])
        assert client_alice.get(url).status_code == 200  # the confirmation page
        assert Picture.objects.exists()
        assert client_alice.post(url).status_code == 302
        assert not Picture.objects.exists()

    def test_profile_lists_only_own(self, client_alice, picture, other, image):
        Picture.objects.create(owner=other, title="Bobs", image=image(), latitude="1", longitude="1")
        body = client_alice.get(reverse("profile")).content.decode()
        assert "Tower" in body
        assert "Bobs" not in body

    @pytest.mark.parametrize("name", ["profile", "upload_picture", "map", "picture_data"])
    def test_pages_need_login(self, client, name):
        response = client.get(reverse(name))
        assert response.status_code == 302
        assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
class TestMapData:
    def test_json(self, client_alice, picture):
        data = client_alice.get(reverse("picture_data")).json()["pictures"]
        assert len(data) == 1
        assert data[0]["title"] == "Tower"
        assert data[0]["owner"] == "alice"
        assert data[0]["latitude"] == pytest.approx(48.85837)
        assert data[0]["image"].endswith(".jpg")

    def test_filter_by_user(self, client_alice, picture, other, image):
        Picture.objects.create(owner=other, title="Bobs", image=image(), latitude="1", longitude="1")
        everyone = client_alice.get(reverse("picture_data")).json()["pictures"]
        only_bob = client_alice.get(reverse("picture_data"), {"user": other.pk}).json()["pictures"]
        assert {p["title"] for p in everyone} == {"Tower", "Bobs"}
        assert [p["title"] for p in only_bob] == ["Bobs"]

    @pytest.mark.parametrize("bad", ["abc", "1; DROP TABLE", "-1", "1.5"])
    def test_bad_user_filter(self, client_alice, bad):
        assert client_alice.get(reverse("picture_data"), {"user": bad}).status_code == 400

    def test_page_lists_only_users_with_pictures(self, client_alice, picture, other):
        body = client_alice.get(reverse("map")).content.decode()
        assert "alice" in body
        assert "bob" not in body

    def test_titles_are_escaped_in_html(self, client_alice, user, image):
        Picture.objects.create(
            owner=user, title="<script>alert(1)</script>", image=image(), latitude="1", longitude="1"
        )
        body = client_alice.get(reverse("profile")).content.decode()
        assert "<script>alert(1)</script>" not in body
        assert "&lt;script&gt;" in body
