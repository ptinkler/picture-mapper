import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import ExifTags, Image


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user("alice", password="pw-alice-123")


@pytest.fixture
def other(db):
    return get_user_model().objects.create_user("bob", password="pw-bob-123")


@pytest.fixture
def client_alice(client, user):
    client.force_login(user)
    return client


def make_image(name="photo.jpg", gps=None, size=(40, 30), fmt="JPEG"):
    """A small real image; ``gps`` is ``(lat_ref, (d, m, s), lon_ref, (d, m, s))`` to embed EXIF GPS."""
    image = Image.new("RGB", size, "red")
    buffer = io.BytesIO()
    kwargs = {}
    if gps:
        exif = Image.Exif()
        ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        ifd[1], ifd[2], ifd[3], ifd[4] = gps
        exif[ExifTags.Base.GPSInfo] = ifd
        kwargs["exif"] = exif
    image.save(buffer, fmt, **kwargs)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{fmt.lower()}")


@pytest.fixture
def image():
    return make_image


@pytest.fixture
def picture(user, image):
    from pictures.models import Picture  # noqa: PLC0415

    return Picture.objects.create(
        owner=user, title="Tower", description="up", image=image(), latitude="48.858370", longitude="2.294481"
    )
