def verify_text(
    text: str
):

    cleaned = text.strip()

    return {
        "is_valid": len(cleaned) >= 3,
        "character_count": len(cleaned),
        "word_count": len(
            cleaned.split()
        )
    }   }
