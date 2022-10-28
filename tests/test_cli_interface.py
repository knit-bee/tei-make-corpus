import os
import subprocess
import tempfile


def test_package_callable_without_error():
    process = subprocess.run(
        ["tei-make-corpus", "--help"], check=True, capture_output=True
    )
    assert process.returncode == 0


def test_package_callable_with_arguments():
    with tempfile.TemporaryDirectory() as tempdir:
        _, temp_header = tempfile.mkstemp(".xml", dir=tempdir, text=True)
        with open(temp_header, "w") as ptr:
            ptr.write("<teiHeader/>")
        process = subprocess.run(
            ["tei-make-corpus", tempdir, "--common-header", temp_header],
            check=True,
            capture_output=True,
        )
    assert process.returncode == 0


def test_package_callable_with_output():
    with tempfile.TemporaryDirectory() as tempdir:
        _, temp_header = tempfile.mkstemp(".xml", dir=tempdir, text=True)
        with open(temp_header, "w") as ptr:
            ptr.write("<teiHeader/>")
        out_file = os.path.join(tempdir, "out.xml")
        corpus_dir = os.path.join(tempdir, "corpus")
        os.mkdir(corpus_dir)
        _, temp_tei = tempfile.mkstemp(".xml", dir=corpus_dir, text=True)
        with open(temp_tei, "w") as ptr:
            ptr.write("<TEI/>")
        process = subprocess.run(
            [
                "tei-make-corpus",
                corpus_dir,
                "-c",
                temp_header,
                "--to-file",
                out_file,
            ],
            check=True,
            capture_output=True,
        )
        assert os.path.exists(out_file) is True
    assert process.returncode == 0
