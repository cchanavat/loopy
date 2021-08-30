# dir name: dname
# array of loop: loop_arr


for i in [1..Size(loop_arr)] do
	Afile := IO_File(Concatenation(dname, "loop/", String(i-1), ".A.loop"), "w");
	Bfile := IO_File(Concatenation(dname, "loop/", String(i-1), ".B.loop"), "w");
	Cfile := IO_File(Concatenation(dname, "loop/", String(i-1), ".C.loop"), "w");
	thetafile := IO_File(Concatenation(dname, "cocycle/", String(i-1), ".theta"), "w");
	sigmafile := IO_File(Concatenation(dname, "cocycle/", String(i-1), ".sigma"), "w");
	
	loop := loop_arr[i];
	ext := NuclearExtension(loop, Center(loop));
	A := ext[1];
	BC := ext[2];
	theta := ext[4];
	ext2 := NuclearExtension(BC, Center(BC));
	B := ext2[1];
	C := ext2[2];
	sigma := ext2[4];
	
	IO_Write(Afile, StringPrint(MultiplicationTable(A)));
	IO_Write(Bfile, StringPrint(MultiplicationTable(B)));
	IO_Write(Cfile, StringPrint(MultiplicationTable(C)));
	IO_Write(thetafile, StringPrint(theta));
	IO_Write(sigmafile, StringPrint(sigma));
	
	
	IO_Close(Afile);
	IO_Close(Bfile);
	IO_Close(Cfile);
	IO_Close(thetafile);
	IO_Close(sigmafile);
od;
