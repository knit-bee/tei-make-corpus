from tei_make_corpus.xmlid_handler import XmlIdHandlerImpl, create_xmlid_handler


def test_xmlidhandlerimpl_instance_constructed():
    handler = create_xmlid_handler()
    assert isinstance(handler, XmlIdHandlerImpl)


def test_create_default_xmlid_handler():
    handler = create_xmlid_handler()
    assert handler.action is None


def test_create_prefix_xmlid_handler():
    handler = create_xmlid_handler(prefix_xmlid=True)
    assert handler.action == "prefix"
