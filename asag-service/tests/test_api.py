import requests

BASE = "http://127.0.0.1:8000"

tests = [
    {
        "label": "Correct short answer",
        "payload": {
            "question_context": "What is photosynthesis?",
            "reference_answer": "Photosynthesis is the process by which plants use sunlight, water and CO2 to produce glucose and oxygen.",
            "student_answer": "Plants use sunlight and carbon dioxide to make glucose and release oxygen through photosynthesis.",
            "question_type": "short_answer"
        }
    },
    {
        "label": "Partial short answer",
        "payload": {
            "question_context": "What is photosynthesis?",
            "reference_answer": "Photosynthesis is the process by which plants use sunlight, water and CO2 to produce glucose and oxygen.",
            "student_answer": "Plants make food using sunlight.",
            "question_type": "short_answer"
        }
    },
    {
        "label": "Wrong short answer",
        "payload": {
            "question_context": "What is photosynthesis?",
            "reference_answer": "Photosynthesis is the process by which plants use sunlight, water and CO2 to produce glucose and oxygen.",
            "student_answer": "Plants absorb nutrients from the soil to grow.",
            "question_type": "short_answer"
        }
    },
    {
        "label": "MCQ correct",
        "payload": {
            "question_context": "Which gas do plants release during photosynthesis?",
            "reference_answer": "C",
            "student_answer": "C",
            "question_type": "multiple_choice",
            "mcq_options": ["A. Carbon dioxide", "B. Nitrogen", "C. Oxygen", "D. Hydrogen"]
        }
    },
    {
        "label": "MCQ wrong",
        "payload": {
            "question_context": "Which gas do plants release during photosynthesis?",
            "reference_answer": "C",
            "student_answer": "A",
            "question_type": "multiple_choice",
            "mcq_options": ["A. Carbon dioxide", "B. Nitrogen", "C. Oxygen", "D. Hydrogen"]
        }
    },
]

for test in tests:
    print(f"\n{'='*55}")
    print(f"TEST: {test['label']}")
    print('='*55)
    r = requests.post(f"{BASE}/grade", json=test["payload"])
    data = r.json()
    print(f"  Final score:       {data['final_weighted_score']}")
    print(f"  Question type:     {data['question_type']}")
    if data.get("semantic_score"):
        print(f"  Semantic score:    {data['semantic_score']['score']}")
        print(f"  Terminology score: {data['terminology_score']['score']}")
        if data['terminology_score']['missing_terms']:
            print(f"  Missing terms:     {data['terminology_score']['missing_terms']}")
    if data.get("mcq_result"):
        print(f"  Correct:           {data['mcq_result']['is_correct']}")
    print(f"\n  Feedback:\n  {data['feedback_report']}")