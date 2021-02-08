# Usage

This program converts Orcad schematic libraries to KiCAD libraries (s-expression)
However, as Orcad libraries native format (*.olb) specification is not public, we first need to export Orcad libraries to XML.
To do that, we use Orcad:

	File->Export->Library XML

Then, once you get myLib.xml:

	pyorlib2ki -i myLib.xml

# TODO

- Understand Orcad native OLB format and convert directly from *.olb to KiCAD *.lib.
