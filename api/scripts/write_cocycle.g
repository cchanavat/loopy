# dir name: dname
# array of loop: loop_arr


for i in [1..Size(loop_arr)] do
	file := IO_File(Concatenation(dname, String(i-1), ".theta"), "w");
	loop := loop_arr[i];
	ext := NuclearExtension(loop, Center(loop));
	IO_Write(file, StringPrint(ext[4]));
	IO_Close(file);
od;
