from pydantic import ValidationError


def validate_schema(
    schema,
    payload: dict
):

    try:

        return schema.model_validate(
            payload
        )

    except ValidationError as error:

        raise error