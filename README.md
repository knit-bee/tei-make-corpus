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
`tei-make-corpus` assumes that the TEI files you want to merge to a `teiCorpus` are valid TEI files (according to [TEI P5](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/index.html)). Otherwise, it is not guaranteed that the output is valid according to the same standard.

`tei-make-corpus` can be used from the command line:

```
$ tei-make-corpus --help
usage: tei-make-corpus [-h] [--config CONFIG] --common-header COMMON_HEADER
                       [--to-file FILENAME] [--deduplicate-header]
                       [--split-documents [SPLIT_DOCUMENTS] | --split-size
                       [SPLIT_SIZE]] [--prefix-xmlid]
                       [--processing-instructions PROCESSING_INSTRUCTIONS]
                       corpus_dir

Create a *teiCorpus* from a collection of TEI documents. The output will be
printed to stdout as default.

positional arguments:
  corpus_dir            Directory containing the TEI files. Only files with the
                        extension '.xml' are processed.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -k CONFIG
                        Path to config file in TOML format for settings of
                        optional arguments (i.e. corpus_dir and --common-header
                        should always be passed as command line arguments). Use
                        [tei-make-corpus] as header or no header. Keys/
                        argument names should match CL argument names but with
                        underscore instead of dash.
  --common-header COMMON_HEADER, -c COMMON_HEADER
                        Xml file containing the common header for the whole
                        corpus. This argument is required.
  --to-file FILENAME, -f FILENAME
                        Name of output file to write to. If this option is
                        enabled, the output is written to the file instead of
                        stdout.
  --deduplicate-header, -d
                        Remove elements from header of individual TEI files
                        that are identical in the common header (experimental).
  --split-documents [SPLIT_DOCUMENTS]
                        Use this option to split the teiCorpus into multiple
                        files. This option takes a NUMBER OF DOCUMENTS that are
                        written to one output file. This option requires the '
                        --to-file' argument, which will be used as template for
                        the names of all output files. The resulting files will
                        be numbered consecutively. For example, if '--split-
                        documents 10' is used, ten files are written to each
                        output file. Each output file will be a valid, stand-
                        alone teiCorpus and the same common header is used for
                        all parts. If the last part would contain less than 30%
                        of the intended number of TEI documents, all files will
                        be distributed evenly (i.e. a part may then contain
                        more than the indicated number of files). This option
                        can also be used without passing a value, the default
                        is 100 000 (documents per output file).
  --split-size [SPLIT_SIZE]
                        Use this option to split the teiCorpus into multiple
                        files. This option takes an intended FILE SIZE IN BYTES
                        for one output file. This option requires the '--to-
                        file' argument, which will be used as template for the
                        file names of all output files. The resulting files
                        will be numbered consecutively. For example, if '--
                        split-size 15000' is used, when the limit of 15
                        kilobytes is reached, (after completing the current TEI
                        document) a new output file will be used. This option
                        can also be used without passing a value, the default
                        is 150 000 000 (bytes per file, 150 MB).
  --prefix-xmlid        Add a prefix to @xml:id attributes instead of removing
                        them. The prefix is generated from the the document's
                        file path and concatenated with the original value of
                        the @xml:id attribute (separated by '-'). For each
                        @xml:id attribute, the prefix is also added to
                        attributes referencing the @xml:id, i.e. attributes
                        with the same value as @xml:id but with a prepended
                        '#'.
  --processing-instructions PROCESSING_INSTRUCTIONS
                        Add xml processing instructions to the teiCorpus file.
                        If passed as command line argument, the processing
                        instructions should be formatted as a json-parsable
                        string representing a dictionary, e.g. '{"a":"b"}'
                        (with double quotes). If a toml file is used, use an
                        inline table or, in multi-line format and used with
                        global table header, prefix the sub-table with 'tei-
                        make-corpus'.
  --add-docid [{0,1,2,3}]
                        Add an <idno/> element with @type='docId' attribute to
                        teiHeader/fileDesc/publicationStmt to each TEI
                        document in the teiCorpus containing a document
                        identifier. The doc id is derived from the original
                        filename. If used without value, it defaults to 0,
                        i.e. the basename of the file is added as doc id.
                        Otherwise, a predefined regex is used to search the
                        filename and extract a capturing group that should be
                        added as identifier. If the filename can't be matched,
                        the basename is used instead and a warning is logged.
                        Possible regular expressions are: {0: None, 1:
                        '.*/\\w{2,3}_(\\w+)\\.xml$', 2: '.*/(\\w+)\\.', 3:
                        '.*/\\w{2,3}_(.+)\\.xml$'}
```

`tei-make-corpus` requires the path to a directory containing the TEI files and a file containing the information for the common header of the corpus.  
All files in the corpus directory that don't end in `.xml` are ignored as well as files that don't contain a `TEI` element as root element.  
The common header should be a formatted `teiHeader`. If the option *--deduplicate-header* is used, the individual header of each file is compared with the common header during the generation of the corpus, and elements that appear in the common header are removed from the individual header (experimental).  
The split options (*--split-size* and *--split-documents*) can also be used with unit prefixes (K, M, G, T), e.g. "2K" = 2000 Bytes.  
As default, all `@xml:id ` attributes are removed from the individual TEI documents to avoid a clash of ids. With the option *--prefix-xmlid*, a prefix individual to each document can be added to `@xml:id` attributes and attributes referencing them (see example below).


<table width="100%">
<tr>
 <th>Original document</th>
 <th>With prefix added</th>
 </tr>

 <tr>
 <td>

```xml
<TEI>
  <name xml:id="author"/>
  <!-- ... -->
  <name corresp="#author"/>
</TEI>
```
</td>

<td>

```xml
<TEI>
  <name xml:id="p7dff7b-author"/>
  <!-- ... -->
  <name corresp="#p7dff7b-author"/>
</TEI>
```
</td>

</tr>

</table>

To add XML processing instructions to the corpus file, use the *--processing-instructions*  option. From the command line, pass a dictionary as a json-parsable string (i.e. keys and values should be enclosed with double quotes).

```xml
$ tei-make-corpus my_corpus -c header.xml --processing-instructions \
'{"xml-model":"href=\"path/to/sth\" type=\"application/xml\""}' | head -n 5
<?xml version='1.0' encoding='UTF-8'?>
<?xml-model href="path/to/sth" type="application/xml"?>
<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">
<teiHeader>
    <fileDesc>
        <titleStmt>
```

If a config file is used, the processing instructions can be formatted as an inline table or multi-line table. In mutli-line format, the table header should be prefixed with 'tei-make-corpus' if a global table header is used.
```sh
# inline table format
$ cat config.toml
processing_instructions = {a="b", a2="c"}
prefix_xmlid = true

# multi-line format

# without global table header
$ cat config3.toml
prefix_xmlid = true
[processing_instructions]
a = "b"
a2 = "c"

# with global table header
$ cat config3.toml
[tei-make-corpus]
prefix_xmlid = true

[tei-make-corpus.processing_instructions]
a = "b"
a2 = "c"
```

The option *--add-docid* can be used to add a document identifier to each TEI document. The doc id is derived from the original file path and as default the basename of the path is used. A set of predefined regular expressions is available to extract only part of the file path as document identifier, e.g.:

```xml
$ ls my_corpus
PRE_Ahfb5ls.xml
$ tei-make-corpus my_corpus -c header.xml --add-docid 1 | grep '<idno type="docId">'
<idno type="docId">Ahfb5ls</idno>
```
If the chosen regular expressions that is used to search the file path does not produce a match, the basename is used as fallback doc id and a warning will be logged.

The extracted doc id is added as text content of a `<idno/>` element with `@type='docId'`. This `<idno/>` element is inserted in `teiHeader/fileDesc/publicationStmt`:
  - after the last `<idno/>` child, if present
  - else: before `<availability/>`, if present
  - else: as last child of `<publicationStmt/>`

If the `<publicationStmt/>` is empty or contains only `<p/>` children, `<p/>` is used as tag for the new element and no `@type` attribute is added.


### Example usage
```xml
$ tei-make-corpus my_corpus --common-header common_header.xml
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
$ tei-make-corpus my_corpus --common-header common_header.xml | xmllint --format - | gzip > my_corpus.xml.gz
```
To remove redundant namespace declarations from the output, e.g. use `xmllint` with the option `--nsclean`.

## License
Copyright © 2022 Berlin-Brandenburgische Akademie der Wissenschaften.

This project is licensed under the GNU General Public License v3.0.
