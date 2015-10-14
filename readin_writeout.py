#!/usr/bin/python3
import re
import os
import csv

def readin(typer):

    if typer == "optitype":
        regexp = re.compile(r'.*result.tsv$')
    if typer == "bwakit":
        regexp = re.compile(r'.*hla.top$')
    if typer == "hlassign":
        regexp = re.compile(r'.*calls.tsv$')
    if typer == "phlat":
        regexp = re.compile(r'.*sum$')

    d = {}

    for root, dirs, files in os.walk('work'):
        for name in files:
            if regexp.search(name):
                name = (os.path.join(name))
                f = open(os.path.join(root,name))
                newnameregex = re.compile(r'work\/hla\.(?:bwakit|optitype|phlat|hlassign)\..{6}-(BIH|C|I|[ES]RR.*[0-9])\/out')
                name = newnameregex.sub(r'\1', root)
                # print(typer + ": " + name)
                
                if typer == "optitype":
                    try:
                        reader = csv.reader(f, delimiter='\t')
                        for row in reader:
                            if row[0]=="0":
                                val = row[1:7]
                                val.sort()
                                c = {}
                                c.update({name:val})
                                d.update({name:val})
                    finally:
                        f.close()
                
                    fsingle = re.sub("work", "output", root)
                    fsingle = "{}/calls.txt".format(fsingle)
                    os.makedirs(os.path.dirname(fsingle), exist_ok=True)
                    with open(fsingle, 'w') as f:
                        for key, value in sorted( c.items() ):
                            f.write(str("\n".join(value)) + '\n' )
                
                if typer == "bwakit":
                    l = []
                    try:
                        reader = csv.reader(f, delimiter='\t')
                        
                        rownum = 0
                        genes = ["A","B","C"]
                        for row in reader:
                            for cell in row:
                                if re.match("HLA-[ABC]", cell):
                                    if cell[4] == genes[rownum]: #First line must be A, second line B ,...
                                        l.append(re.sub("HLA-", "", cell))
                                    else:
                                        l.append("*".join((genes[rownum], "none")))
                            rownum = rownum + 1
                    finally:
                        f.close()
                    
                    # Fill list with none predictions in case the file is empty or does not contain enough lines!
                    if len(l) == 4:
                        l.extend(["C*none","C*none"])
                    elif len(l) == 2:
                        l.extend(["B*none","B*none", "C*none","C*none"])
                    elif len(l) == 0:
                        l.extend(["A*none","A*none", "B*none","B*none", "C*none","C*none"])

                    d.update({name:l})

                if typer == "hlassign":
                    l = []
                    try:
                        reader = csv.reader(f, delimiter=' ')
                        for row in reader:
                            colnum = 0
                            for cell in row:
                                if colnum in [2,3]:
                                    l.append(cell)
                                colnum = colnum + 1
                    finally:
                        f.close()
                        l.sort()

                    d.update({name:l})

                if typer == "phlat":
                    l = []
                    try:
                        reader = csv.reader(f, delimiter='\t')
                        
                        rownum = -1
                        genes = ["A","B","C"]
                        for row in reader:
                            for cell in row:
                                if re.match("[ABC]\*", cell):
                                    if cell[0] == genes[rownum]:
                                        l.append(cell)
                                    else:
                                        l.append("*".join((genes[rownum], "none")))
                            rownum = rownum + 1
                    finally:
                        f.close()
                    
                    # Fill list with none predictions in case the file is empty or does not contain enough lines!
                    if len(l) == 4:
                        l.extend(["C*none","C*none"])
                    elif len(l) == 2:
                        l.extend(["B*none","B*none", "C*none","C*none"])
                    elif len(l) == 0:
                        l.extend(["A*none","A*none", "B*none","B*none", "C*none","C*none"])

                    d.update({name:l})
    
    
    outfile = open("output/{}_test".format(typer), 'w' )
    
    for key, value in sorted( d.items() ): #sort keys, i.e. the sample ID, so that it is the same in every result file
        outfile.write( str(key) + '\t' + str(" ".join(value)) + '\n' )
    outfile.close()

    return d
    
if __name__ == "__main__":
    readin()
