import re


_CITATION_CHAIN_RE = re.compile(
    r"""
    (?:
        \[\s*\d+(?:\s*[-,\u2010-\u2015?]\s*\d+)*\s*\]
        (?:\s*[,;\u2010-\u2015?-]\s*)?
    )+
    """,
    re.VERBOSE,
)


def clean_text(text: str) -> str:
    """
    Normalize PDF-extracted text before chunking.

    Removes bracketed numeric citation chains such as [30], [30]-[32],
    [30]–[32], [30], [31], and [31,32][30-31].
    """
    if not text:
        return ""

    text = _CITATION_CHAIN_RE.sub("", text)
    text = re.sub(r":::+", "", text)

    # Rejoin words split by PDF line wrapping while keeping normal newlines as spaces.
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

    # Clean up punctuation left behind after citation removal.
    text = re.sub(r"\s+([,;:.])", r"\1", text)
    text = re.sub(r"([([{])\s+|\s+([)\]}])", lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"\(\s*\)|\[\s*\]|\{\s*\}", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()
