from decimal import Decimal

from pictures.exif import gps_position


def test_reads_gps(image):
    file = image(gps=("N", (48.0, 51.0, 30.12), "E", (2.0, 17.0, 40.12)))
    assert gps_position(file) == (Decimal("48.858367"), Decimal("2.294478"))


def test_southern_and_western_hemispheres_are_negative(image):
    file = image(gps=("S", (33.0, 52.0, 0.0), "W", (151.0, 12.0, 0.0)))
    lat, lon = gps_position(file)
    assert lat < 0 > lon
    assert (lat, lon) == (Decimal("-33.866667"), Decimal("-151.200000"))


def test_rewinds_the_file_so_it_can_still_be_saved(image):
    file = image(gps=("N", (1.0, 0.0, 0.0), "E", (1.0, 0.0, 0.0)))
    gps_position(file)
    assert file.tell() == 0


def test_photo_without_gps(image):
    assert gps_position(image()) is None


def test_not_an_image():
    import io  # noqa: PLC0415

    assert gps_position(io.BytesIO(b"not an image")) is None


def test_out_of_range_position_is_ignored(image):
    file = image(gps=("N", (95.0, 0.0, 0.0), "E", (10.0, 0.0, 0.0)))
    assert gps_position(file) is None


def test_garbage_gps_values_are_ignored(image):
    file = image(gps=("N", (0.0, 0.0, 0.0), "E", (0.0, 0.0, 0.0)))
    assert gps_position(file) == (Decimal("0.000000"), Decimal("0.000000"))
