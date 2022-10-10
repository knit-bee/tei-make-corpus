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
            ["tei-make-corpus", tempdir, "--cheader", temp_header],
            check=True,
            capture_output=True,
        )
    assert process.returncode == 0
