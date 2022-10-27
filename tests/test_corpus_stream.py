import sys
import unittest

from tei_make_corpus.corpus_stream import CorpusStreamImpl


class CorpusStreamTest(unittest.TestCase):
    def setUp(self):
        self.corpus_stream = CorpusStreamImpl()

    def test_returns_stdout_buffer(self):
        result = self.corpus_stream.path()
        self.assertEqual(result, sys.stdout.buffer)

    def test_file_handle_returned_when_set_as_output(self):
        file = "text.xml"
        self.corpus_stream.set_output_file(file)
        self.assertEqual(self.corpus_stream.path(), file)

    def test_update_output_file_name_enumeration(self):
        template_name = "file.xml"
        self.corpus_stream.set_output_file(template_name)
        result = []
        for _ in range(20):
            self.corpus_stream.update_output_file_name()
            result.append(self.corpus_stream.path())
        expected = [f"file{i:04}.xml" for i in range(1, 21)]
        self.assertEqual(result, expected)

    def test_update_file_name_when_no_file_name_was_set(self):
        result = []
        for _ in range(20):
            self.corpus_stream.update_output_file_name()
            result.append(self.corpus_stream.path())
        expected = [f"part{i:04}.xml" for i in range(1, 21)]
        self.assertEqual(result, expected)
