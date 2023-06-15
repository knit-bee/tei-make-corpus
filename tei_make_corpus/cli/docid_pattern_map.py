class PatternMap(dict):
    def __init__(self):
        self[0] = None  # Default: use basename
        self[1] = r".*/\w{2,3}_(\w+)\.xml$"
        self[2] = r".*/(\w+)\."
        self[3] = r".*/\w{2,3}_(.+)\.xml$"
