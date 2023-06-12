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
usage: tei-make-corpus [-h] --common-header COMMON_HEADER [--to-file FILENAME]
                       [--deduplicate-header]
                       [--split-documents [SPLIT_DOCUMENTS] | --split-size
                       [SPLIT_SIZE]]
                       corpus_dir

Create a *teiCorpus* from a collection of TEI documents. The output will be
printed to stdout as default.

positional arguments:
  corpus_dir            Directory containing the TEI files. Only file with the
                        extension '.xml' are processed.

optional arguments:
  -h, --help            show this help message and exit
  --common-header COMMON_HEADER, -c COMMON_HEADER
                        Xml file containing the common header for the whole
                        corpus.
  --to-file FILENAME, -f FILENAME
                        Name of output file to write to. If this option is
                        enabled, the output is written to the file instead of
                        stdout.
  --deduplicate-header, -d
                        Remove elements from header of individual TEI files
                        that are identical in the common header
                        (experimental).
  --split-documents [SPLIT_DOCUMENTS]
                        Use this option to split the teiCorpus into multiple
                        files. This option takes a NUMBER OF DOCUMENTS that are
                        written to one output file. This option requires the '
                        --to-file' argument, which will be used as template
                        for the names of all output files. The resulting files
                        will be numbered consecutively. For example, if '--
                        split-documents 10' is used, ten files are written to
                        each output file. Each output file will be a valid,
                        stand-alone teiCorpus and the same common header is
                        used for all parts. If the last part would contain
                        less than 30% of the intended number of TEI documents,
                        all files will be distributed evenly (i.e. a part may
                        then contain more than the indicated number of files).
                        This option can also be used without passing a value,
                        the default is 100 000 (documents per output file).
  --split-size [SPLIT_SIZE]
                        Use this option to split the teiCorpus into multiple
                        files. This option takes an intended FILE SIZE IN
                        BYTES for one output file. This option requires the '
                        --to-file' argument, which will be used as template
                        for the file names of all output files. The resulting
                        files will be numbered consecutively. For example, if
                        '--split-size 15000' is used, when the limit of 15
                        kilobytes is reached, (after completing the current
                        TEI document) a new output file will be used. This
                        option can also be used without passing a value, the
                        default is 150 000 000 (bytes per file, 150 MB).
  --prefix-xmlid        
                        Add a prefix to @xml:id attributes instead of removing
                        them. The prefix is generated from the the document's
                        file path and concatenated with the original value of
                        the @xml:id attribute (separated by '-'). For each
                        @xml:id attribute, the prefix is also added to attributes
                        referencing the @xml:id, i.e. attributes with the same
                        value as @xml:id but with a prepended '#'.

```

`tei-make-corpus` requires the path to a directory containing the TEI file and a file containing the information for the common header of the corpus.  
All files in the corpus directory that don't end in `.xml` are ignored as well as files that don't contain a `TEI` element as root element.  
The common header should be a formatted `teiHeader`. If the option `--deduplicate-header` is used, the individual header of each file is compared with the common header during the generation of the corpus, and elements that appear in the common header are removed from the individual header (experimental).  
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
