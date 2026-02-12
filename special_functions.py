def split_at_first(n, find):
    for i in n:
        if i == find:
            position = n.find(i)
    first_section = n[:position]
    second_section = n[position+1:]
    n = [first_section, second_section]
    return n

