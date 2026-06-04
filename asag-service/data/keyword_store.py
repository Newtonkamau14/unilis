"""
keyword_store.py
-----------------
Loads domain-specific keyword lists.

In production this could query a database keyed by subject/course.
For now it uses a static dictionary with subject detection heuristics.

The keyword list supplements POS-tagged term extraction in term_extractor.py
to ensure critical domain terms are never missed even if POS tagging drops them.
"""

from __future__ import annotations

# Keyword lists organized by domain — extend as needed
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "biology": [
        "photosynthesis", "chlorophyll", "mitosis", "meiosis", "osmosis",
        "diffusion", "respiration", "enzyme", "catalyst", "chromosome",
        "nucleus", "ribosome", "mitochondria", "ATP", "DNA", "RNA",
    ],
    "chemistry": [
        "oxidation", "reduction", "covalent", "ionic", "bond", "molecule",
        "atom", "electron", "proton", "neutron", "valence", "equilibrium",
        "catalyst", "reaction", "enthalpy", "entropy",
    ],
    "computer_science": [
        "algorithm", "complexity", "recursion", "iteration", "stack",
        "queue", "array", "linked list", "binary", "hash", "sorting",
        "searching", "inheritance", "polymorphism", "encapsulation",
        "abstraction", "class", "object", "method",
    ],
    "physics": [
        "velocity", "acceleration", "momentum", "force", "gravity",
        "energy", "work", "power", "frequency", "wavelength", "amplitude",
        "resistance", "voltage", "current", "electromagnetic",
    ],
    "default": [],
}

# Simple domain detection by keyword presence in question context
DOMAIN_HINTS: dict[str, list[str]] = {
    "biology": ["cell", "organism", "plant", "animal", "gene", "species", "protein"],
    "chemistry": ["element", "compound", "reaction", "acid", "base", "solution", "mole"],
    "computer_science": ["program", "code", "function", "data structure", "software", "algorithm"],
    "physics": ["force", "motion", "energy", "wave", "electric", "magnetic", "light"],
}


def load_keywords(context: str) -> list[str]:
    """
    Detect subject domain from question context and return relevant keywords.

    Args:
        context: The question text.

    Returns:
        List of domain-specific keywords to prioritize during term extraction.
    """
    context_lower = context.lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(hint in context_lower for hint in hints):
            return DOMAIN_KEYWORDS.get(domain, [])
    return DOMAIN_KEYWORDS["default"]