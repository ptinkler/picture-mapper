from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Picture(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pictures")
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1024, blank=True)
    image = models.ImageField(upload_to="pictures/%Y/%m/", height_field="height", width_field="width")
    height = models.PositiveIntegerField(editable=False)
    width = models.PositiveIntegerField(editable=False)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]

    def __str__(self) -> str:
        return self.title
