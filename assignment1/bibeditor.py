def bibeditor():
    listorequires =     ["title","author","journal","volume","pages","year","keyword","pathname of a .bib file"]
    inputdict = {}
    for elem in listorequires:
        x = input(elem+"?")
        inputdict[elem] = x

    writtenfile = open(inputdict["pathname of a .bib file"],"a")
    writtenfile.write("@article{"+inputdict["keyword"]+ ",\n")
    
    for elem in listorequires:
        if elem != "pathname of a .bib file" and elem != "keyword":
            writtenfile.write(elem+"="+'"'+inputdict[elem]+'",\n')
    writtenfile.write("}\n")
    
bibeditor()