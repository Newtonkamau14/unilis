REQUIRED_RUBRIC_FIELDS = {

    "completeness",

    "structural_accuracy",

    "label_correctness",

    "spatial_correctness",

    "diagram_quality"
}


def validate_rubric(
    rubric: dict
) -> bool:

    return REQUIRED_RUBRIC_FIELDS.issubset(
        rubric.keys()
    )