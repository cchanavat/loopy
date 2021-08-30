file := IO_File(fname, "w");

for a in A do
	IO_Write(file, Concatenation(StringPrint(a), "\n"));
od;
IO_Close(file);
