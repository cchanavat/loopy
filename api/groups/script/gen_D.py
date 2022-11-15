for i in range(1, 5):
    gap.send(f"G:=DihedralGroup({2*i});")
    gap.send(f"MultiplicationTable(G);")
    res_ = gap.last_result()
    res = " ".join(res_)
    if i >= 6:
        print(res)
    table = literal_eval(res)
    D = Loop(np.array(table, dtype=int) - 1)
    np.savetxt(f"/home/clemence/stage/src/loopapy/groups/D{2*i}.group", D.tmul, fmt="%i")
