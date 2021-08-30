# dir_name: dname
# number loops: nloops

result_file := IO_File(Concatenation(dname, "csorgo.res"), "w");

for i in [0..nloops-1] do
	loop_fname := Concatenation(dname, "loop/", String(i), ".loop"); 
	loop := LoopFromFile(loop_fname, " ");
	
	inn := InnerMappingGroup(loop);
	ord := Order(DerivedSubgroup(inn));
	ord_inn := Order(inn);
	nilp := NilpotencyClassOfLoop(loop);
	str := Concatenation(String(i), ",", String(nilp), ",", String(ord), ",", String(ord_inn), "\n");
	
	IO_Write(result_file, str);
	Print(i, "\n");
od;

IO_Close(result_file);
