from django.templatetags.static import static

from .laundry_images import LAUNDRY_IMAGE_FILES


def laundry_media(request):
    return {
        "img": {key: static(path) for key, path in LAUNDRY_IMAGE_FILES.items()}
    }
