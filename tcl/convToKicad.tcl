package provide capMenuUtil 1.0
namespace eval ::capMenuUtil {
}

proc get_olbLibPath {} { return "X:/your_lib_path/here" }
proc get_pyorlib2ki {} { return "Y:/your_path_to_exe/pyorlib2ki.exe" }

proc ::capMenuUtil::addLibXMLMenu { } {
	AddAccessoryMenu "Libs" "Update XML libraries" "::capMenuUtil::update"
	AddAccessoryMenu "Libs" "Convert XML libraries to KiCAD" "::capMenuUtil::convert"
}

proc ::capMenuUtil::update { pLib } {
	set olbLibPath [get_olbLibPath]
	set allLibs [glob -directory $olbLibPath -- "*.olb"]
	puts $allLibs
	foreach f $allLibs {
		set fbasename [file rootname $f]
		puts $f
		XMATIC_OLB2XML $f ${fbasename}.xml
	}
}

proc ::capMenuUtil::convert { pLib } {
	set olbLibPath [get_olbLibPath]
	set pyorlib2ki [get_pyorlib2ki]
	set allLibs [glob -directory $olbLibPath -- "*.xml"]
	foreach f $allLibs {
		puts $f
		set cmd [list ${pyorlib2ki} -i $f]
		puts $cmd
		eval exec $cmd
	}
}

proc ::capMenuUtil::capTrue { } {
	return 1
}

RegisterAction "_cdnCapTclAddDesignCustomMenu" "::capMenuUtil::capTrue" "" "::capMenuUtil::addLibXMLMenu" ""
