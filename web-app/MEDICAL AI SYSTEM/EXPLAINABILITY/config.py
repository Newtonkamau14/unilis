import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =====================================================
    # SERVICE
    # =====================================================

    SERVICE_NAME: str = "explainability-service"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8011

    # =====================================================
    # STORAGE
    # =====================================================

    OUTPUT_DIR: str = "outputs/explainability"

    HEATMAP_DIR: str = "outputs/explainability/heatmaps"
    OVERLAY_DIR: str = "outputs/explainability/overlays"
    REPORT_DIR: str = "outputs/explainability/reports"
    ATTENTION_DIR: str = "outputs/explainability/attention"

    # =====================================================
    # MODEL SETTINGS
    # =====================================================

    DEVICE: str = "cpu"

    DEFAULT_IMAGE_SIZE: int = 512

    NORMALIZE_MEAN: tuple = (
        0.485,
        0.456,
        0.406
    )

    NORMALIZE_STD: tuple = (
        0.229,
        0.224,
        0.225
    )

    # =====================================================
    # EXPLAINABILITY
    # =====================================================

    ENABLE_GRADCAM: bool = True
    ENABLE_GRADCAM_PLUS_PLUS: bool = True
    ENABLE_INTEGRATED_GRADIENTS: bool = True
    ENABLE_SHAP: bool = True
    ENABLE_LRP: bool = True

    MAX_EXPLANATION_CLASSES: int = 5

    # =====================================================
    # REPORTS
    # =====================================================

    PDF_AUTHOR: str = "Medical AI Explainability Engine"

    PDF_TITLE: str = (
        "Medical AI Explanation Report"
    )

    # =====================================================
    # LOGGING
    # =====================================================

    LOG_LEVEL: str = "INFO"

    LOG_FORMAT: str = (
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    # =====================================================
    # Pydantic Settings
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

# =====================================================
# DIRECTORY CREATION
# =====================================================

directories = [
    settings.OUTPUT_DIR,
    settings.HEATMAP_DIR,
    settings.OVERLAY_DIR,
    settings.REPORT_DIR,
    settings.ATTENTION_DIR,
]

for directory in directories:
    Path(directory).mkdir(
        parents=True,
        exist_ok=True
    )