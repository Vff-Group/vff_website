from django.templatetags.static import static

from .laundry_images import LAUNDRY_IMAGE_FILES

LOGO_PATH = "img/logos/logo_new.png"

VFF_VIDEOS = [
    "videos/vff_video_1.mp4",
    "videos/vff_video_2.mp4",
    "videos/vff_video_3.mp4",
    "videos/vff_video_4.mp4",
]


def laundry_media(request):
    return {
        "img": {key: static(path) for key, path in LAUNDRY_IMAGE_FILES.items()},
        "logo_url": static(LOGO_PATH),
        "vff_videos": [static(path) for path in VFF_VIDEOS],
    }
