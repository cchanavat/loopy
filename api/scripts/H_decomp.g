# Loop name : loop
# Folder name : fname
# index name : i

sigma_fname := Concatenation(fname, String(i), ".sigma");
sigma_file := IO_File(sigma_fname, "w");

AB_fname := Concatenation(fname, String(i),".struct");
AB_file := IO_File(AB_fname, "w");

cext1 := NuclearExtension(loop, Center(loop)); 
A := cext1[1];
B := cext1[2];
sigma := cext1[4];


A_struct := StructureDescription(AsGroup(A));
B_struct := StructureDescription(AsGroup(B));

str_struct := Concatenation(StringPrint(A_struct), " :_s ", StringPrint(B_struct));


IO_Write(sigma_file, StringPrint(sigma));
IO_Write(AB_file, str_struct);
# IO_Write(A_file, StringPrint(MultiplicationTable(A)));
# IO_Write(B_file, StringPrint(MultiplicationTable(B)));



IO_Close(sigma_file);
IO_Close(AB_file);
# IO_Close(A_file);
# IO_Close(B_file);
