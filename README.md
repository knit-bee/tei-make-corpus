# tei-make-corpus
Create a teiCorpus-file from a collection of TEI documents



## Installation
Install from github repository:

```sh
$ pip install git+https://github.com/knit-bee/tei-make-corpus.git
```
### Requirements
* Python >= 3.8
* lxml >= 4.0

## Usage
`tei-make-corpus` assumes that the TEI files you want to merge to a `teiCorpus` are valid TEI files (according to [TEI P5](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/index.html)). Otherwise, it is not guaranteed that the output is valid according the same standard.

`tei-make-corpus` can be used from the command line:

```
$ tei-make-corpus --help
usage: tei-make-corpus [-h] --cheader CHEADER corpus_dir

Create a *teiCorpus* from a collection of TEI documents. The output will be printed to stdout.

positional arguments:
  corpus_dir            Directory containing the TEI files.

optional arguments:
  -h, --help            show this help message and exit
  --common-header COMMON_HEADER, -c COMMON_HEADER
                        Xml file containing the common header for the whole corpus.
  --to-file FILENAME, -f FILENAME
                        Name of output file to write to. If this option is
                        enabled, the output is written to the file instead of
                        stdout.

```

`tei-make-corpus` requires the path to a directory containing the TEI file and a file containing the information for the common header of the corpus.
All files in the corpus directory that don't end in `.xml` are ignored as well as files that don't contain a `TEI` element as root element.
The common header should be a formatted `teiHeader`. During the generation of the corpus, the individual header of each file is compared with the common header
and elements that appear in the common header are removed from the individual header.

### Example usage
```xml
$ tei-make-corpus my_corpus --cheader common_header.xml
<?xml version='1.0' encoding='utf-8'?>
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0"><teiHeader>
    <fileDesc>
        <titleStmt>
            <title/>
        </titleStmt>
        <publicationStmt>
          <p/>
        </publicationStmt>
        <sourceDesc>
          <p/>
        </sourceDesc>
    </fileDesc>
</teiHeader>
<TEI>
<!-- ... -->
</TEI>
</teiCorpus>
```

The output can then be piped to other programs, e.g. to format it or to compress it.

```sh
$ tei-make-corpus my_corpus --cheader common_header.xml | xmllint --format - | gzip > my_corpus.xml.gz
```

## License
Copyright © 2022 Berlin-Brandenburgische Akademie der Wissenschaften.

This project is licensed under the GNU General Public License v3.0.
