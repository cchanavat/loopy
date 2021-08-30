# Loop name : loop
# Folder name : fname
# index name : i


theta_fname := Concatenation(fname, "cocycle/", String(i), ".theta");
theta_file := IO_File(theta_fname, "w");

sigma_fname := Concatenation(fname, "cocycle/", String(i), ".sigma");
sigma_file := IO_File(sigma_fname, "w");

ABC_fname := Concatenation(fname, "ABC/", String(i), ".ABC");
ABC_file := IO_File(ABC_fname, "w");

A_fname := Concatenation(fname, "ABC/", String(i), ".A.group");
A_file := IO_File(A_fname, "w");

B_fname := Concatenation(fname, "ABC/", String(i), ".B.group");
B_file := IO_File(B_fname, "w");

C_fname := Concatenation(fname, "ABC/", String(i), ".C.group");
C_file := IO_File(C_fname, "w");

BC_fname := Concatenation(fname, "ABC/", String(i), ".BC.group");
BC_file := IO_File(BC_fname, "w");

cext1 := NuclearExtension(loop, Center(loop)); 
A := cext1[1];
BxC := cext1[2];
theta := cext1[4];

cext2 := NuclearExtension(BxC, Center(BxC));
B := cext2[1];
C := cext2[1];	 
sigma := cext2[4];

A_struct := StructureDescription(AsGroup(A));
B_struct := StructureDescription(AsGroup(B));
C_struct := StructureDescription(AsGroup(C));

str_struct := Concatenation(StringPrint(A_struct), " :_t (", StringPrint(B_struct), " :_s ", StringPrint(C_struct), ")");

IO_Write(theta_file, StringPrint(theta));
IO_Write(sigma_file, StringPrint(sigma));
IO_Write(ABC_file, str_struct);
IO_Write(A_file, StringPrint(MultiplicationTable(A)));
IO_Write(B_file, StringPrint(MultiplicationTable(B)));
IO_Write(C_file, StringPrint(MultiplicationTable(C)));
IO_Write(BC_file, StringPrint(MultiplicationTable(BxC)));


IO_Close(theta_file);
IO_Close(sigma_file);
IO_Close(ABC_file);
IO_Close(A_file);
IO_Close(B_file);
IO_Close(C_file);
IO_Close(BC_file);

