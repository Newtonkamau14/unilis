from functools import lru_cache

from shared.config import settings


@lru_cache
def get_settings():
    return settings


def get_model_paths():

    return {
        "yolo": settings.YOLO_MODEL_PATH,
        "unet": settings.UNET_MODEL_PATH
    }