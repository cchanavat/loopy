file := IO_File(fname, "w");

for phi in homBtoAutA do
	for b in B do
		for a in A do
			phiB := Image(phi, b);
			phiBA := Image(phiB, a);
			IO_Write(file, Concatenation(StringPrint(phiBA), "\n"));
		od;
	od;
od;
IO_Close(file);
