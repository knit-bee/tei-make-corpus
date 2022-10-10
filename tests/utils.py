from lxml import etree


def create_validator(scheme_path: str) -> etree.RelaxNG:
    return etree.RelaxNG(etree.parse(scheme_path))
