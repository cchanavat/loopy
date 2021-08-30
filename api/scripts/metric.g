
metric_file := IO_File(fname, "w");
for i in [0..nloops] do
	fname := Concatenation(BDIR, "loop/", String(i), ".loop");
	Print(fname); Print("\n");
	Q := LoopFromFile(fname, " ");
	Inn := InnerMappingGroup(Q);
	D := DerivedSubgroup(Inn);
	
	Inn_ord := String(Order(Inn));
	D_ord := String(Order(D));
	
	nilp := NilpotencyClassOfLoop(Q);
	
	data := Concatenation(String(i), ",", Inn_ord, ",", D_ord, ",", String(nilp) ,"\n");
	IO_Write(metric_file, data);
od;
IO_Close(metric_file);
