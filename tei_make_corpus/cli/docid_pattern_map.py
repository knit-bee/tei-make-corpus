"""
Mapping for regex patterns for extraction of document id from file name.
"""
PATTERN_MAP = {
    0: None,  # Default: use basename
    1: r".*/\w{2,3}_(\w+)\.xml$",
    2: r".*/(\w+)\.",
    3: r".*/\w{2,3}_(.+)\.xml$",
}
