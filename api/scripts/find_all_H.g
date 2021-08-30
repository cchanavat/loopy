# directory name : dname

for i in [1..267] do
	H := SmallGroup(64, i);
	DH := DerivedSubgroup(H);
	q := FactorGroup(H, DH);
	if Size(DH) = 8 and Length(GeneratorsOfGroup(DH)) = 3 and IdGroup(q)[2] = 5 and IsPGroup(DH) and DH = Center(H) then
		fname := Concatenation(dname, String(i), ".group");
		file := IO_File(fname, "w");
		IO_Write(file, String(MultiplicationTable(H)));
		IO_Close(file);
	fi;
	
od;
