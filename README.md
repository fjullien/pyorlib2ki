# Usage

This program converts Orcad schematic libraries to KiCAD libraries (s-expression)
However, as Orcad libraries native format (*.olb) specification is not public, we first need to export Orcad libraries to XML.
To do that, we use Orcad:

	File->Export->Library XML

Then, once you get myLib.xml:

	pyorlib2ki -i myLib.xml

# Orcad TCL script

If you often convert libraries, you can include a command in orcad.
Modify convToKicad.tcl to match your configuration:

	proc get_olbLibPath {} { return "X:/your_lib_path/here" }
	proc get_pyorlib2ki {} { return "Y:/your_path_to_exe/pyorlib2ki.exe" }

Put convToKicad.tcl in your capAutoLoad directory (which is in general in SPB_XX/tools/capture/tclscripts/capAutoLoad) and restart orcad.

You should have two news commands under Accessories->Libs


# TODO

- Understand Orcad native OLB format and convert directly from *.olb to KiCAD *.lib.
