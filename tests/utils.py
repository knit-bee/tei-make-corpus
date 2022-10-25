from lxml import etree


def create_validator(scheme_path: str) -> etree.RelaxNG:
    return etree.RelaxNG(etree.parse(scheme_path))


class MockHeaderHandler:
    def common_header(self):
        return None

    def declutter_individual_header(self, iheader):
        pass
