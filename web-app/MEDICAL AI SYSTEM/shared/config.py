from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "Medical AI Diagram Assessment"

    API_VERSION: str = "v1"

    YOLO_MODEL_PATH: str = (
        "DETECTION/weights/yolo11m_medical.pt"
    )

    UNET_MODEL_PATH: str = (
        "DETECTION/weights/attention_unet.pth"
    )

    OCR_LANGUAGES: list[str] = ["en"]

    DEVICE: str = "cpu"

    class Config:
        env_file = ".env"


settings = Settings()