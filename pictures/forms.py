from django import forms
from django.conf import settings

from .exif import gps_position
from .models import Picture


class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ("title", "description", "image", "latitude", "longitude")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Not required in the form: a photo with GPS data can supply them (see clean).
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False

    def clean_image(self):
        image = self.cleaned_data.get("image")
        limit = settings.MAX_UPLOAD_MB * 1024 * 1024
        if image and image.size > limit:
            msg = f"The picture is larger than {settings.MAX_UPLOAD_MB} MB."
            raise forms.ValidationError(msg)
        return image

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("latitude") is not None and cleaned.get("longitude") is not None:
            return cleaned
        image = cleaned.get("image")
        position = gps_position(image) if image and hasattr(image, "seek") else None
        if position is None:
            if "image" not in self.errors:
                msg = "Click the map to say where it was taken, or upload a photo that has GPS data."
                self.add_error("latitude", msg)
            return cleaned
        cleaned["latitude"], cleaned["longitude"] = position
        return cleaned
