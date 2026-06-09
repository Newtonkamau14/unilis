from sklearn.metrics.pairwise import cosine_similarity


def compute_score(
        student_embedding,
        reference_embedding
):

    score = cosine_similarity(
        [student_embedding],
        [reference_embedding]
    )[0][0]

    return round(score * 100, 2)
