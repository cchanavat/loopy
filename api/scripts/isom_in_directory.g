# parent directory name: fname
# number of loops: nloops

file_name := Concatenation(fname, "isom.res");
file := IO_File(file_name, "w");

for i in [0..nloops-2] do
	I_fname := Concatenation(fname, "loop/", String(i), ".loop"); 
	I := LoopFromFile(I_fname, " ");
	for j in [i + 1..nloops-1] do
		J_fname := Concatenation(fname, "loop/", String(j), ".loop");
		J := LoopFromFile(J_fname, " ");
		isom := IsomorphismLoops(I, J);
		str := Concatenation(String(i), " - ", String(j), " : ", StringPrint(isom), "\n");
		IO_Write(file, str);
		Print(i);Print(j);Print("\n");
	od;
od;


IO_Close(file);
