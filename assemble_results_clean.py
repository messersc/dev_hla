#!/usr/bin/python3

import os
import re
import csv
import sys

def main():
    for typer in ['optitype','hlassign','bwakit']:
        readin( typer = typer)


def readin(typer, dir = sys.argv[1]):
    
    if typer == "optitype": 
        regexp = re.compile(r'.*result.tsv$')
    if typer == "bwakit": 
        regexp = re.compile(r'.*hla.top$')
    if typer == "hlassign": 
        regexp = re.compile(r'.*calls.tsv$')

    
    d = {}

    for root, dirs, files in os.walk(dir):
        for name in files:
            if regexp.search(name):
                name = (os.path.join(name))
                f = open(os.path.join(root,name))
                
                #print(name)
                newnameregex = re.compile(r'.*(CELL_ID_[0-9]{1,3}).*')
                name = newnameregex.sub(r'\1', name)
                #print(name)
                               
                if typer == "optitype":
                    try:
                        reader = csv.reader(f, delimiter='\t')
                        for row in reader:
                            if row[0]=="0":
                                val = row[1:7]
                                val.sort()
                                d.update({name:val})
                    finally:
                        f.close()
                
                if typer == "bwakit":
                    l = []
                    try:
                        reader = csv.reader(f, delimiter='\t')
                        for row in reader:
                            for cell in row:
                                if cell.startswith("HLA-"):
                                    l.append(cell.replace("HLA-", ""))
                    finally:
                        f.close()
                        l.sort()

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

    
    
    outfile = open( typer, 'w' )
    
    for key, value in sorted( d.items() ):
        outfile.write( str(key) + '\t' + str(" ".join(value)) + '\n' )
    outfile.close()
    
if __name__ == "__main__":
    main()
