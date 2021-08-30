# loop: loop
# dname: dname

res_fname := Concatenation(dname, "loop.prop");
res := IO_File(res_fname, "w");

group_descr := "fail";

if IsAssociative(loop) then
	group_descr := StringPrint(StructureDescription(AsGroup(loop)));
fi;

inn := InnerMappingGroup(loop);
Dinn := DerivedSubgroup(inn);

card_inn := String(Size(inn));
card_Dinn := String(Size(Dinn));

nilp := String(NilpotencyClassOfLoop(loop));
nilp_inn := String(NilpotencyClassOfGroup(inn));

str := Concatenation(
	"nilp_loop:    ", nilp, "\n",
	"nilp_inn:     ", nilp_inn, "\n",
	"card_inn:     ", card_inn, "\n",
	"card_Dinn:    ", card_Dinn, "\n",
	"group_descr:  ", group_descr);
		
IO_Write(res, str);
IO_Close(res);


