#!/usr/bin/python3

import os
import re
import csv
from collections import Counter
from readin_writeout import readin

def get_reference():
    ref = {}
    with open('output/ref') as f:
        for line in f:
            x = line.split()
            ref.update({x[0]:x[1:]})
    return ref

def fit_to_precision(hlas, precision="4d"):
    if precision == "2d":
        pattern = "(^[ABC]\\*[0-9]{2}).*"
        ncolon = 0
    elif precision == "4d":
        pattern = "(^[ABC]\\*[0-9]{2}:[0-9]{2,3}).*"
        ncolon = 1
    else: return('STOP')

    def fit_allele(string, regex=pattern, ncolon=ncolon):
         if string.count(":") >= ncolon:
            return(re.sub(regex, '\\1', string))
         else:
            return(None)

    try:
        hlas = list(map(fit_allele, hlas))
        hlas = filter(None, hlas)
        return Counter(hlas)
    except TypeError:
        return Counter()

def compare_ref_pred(ref, predictions):
    performancedict = {}

    for typer,samples in predictions.items():
        TP = 0
        FP = 0
        FN = 0
        notype = 0

        for samplename,hlas in samples.items():
            p = fit_to_precision(hlas)
            r = fit_to_precision(ref.get(samplename))

            TP += len(list((r & p).elements()))
            FP += len(list((p - r).elements()))
            FN += len(list((r - p).elements()))
            notype += 6-len(list(r.elements()))

        FP = FP-notype
        try:
            recall    = TP/(TP + FN)
            precision = TP/(TP + FP)
            F1 = 2*recall*precision/(recall+precision)
        except ZeroDivisionError:
            recall    = 0
            precision = 0
            F1 = 0

        performancedict.update({typer:{"TP":TP, "FP":FP, "FN":FN, "recall":recall, "precision":precision, "F1-measure":F1}})

    return performancedict


def print_all(ref, predictions):
    print("ref"+": "+str(len(ref)))
    for samplename, hla in ref.items():
        print('{}:{}'.format(samplename, hla))

    for typer, sample in predictions.items():
        print(typer+": "+str(len(predictions[typer])))
        for samplename, hla in sample.items():
            print('{}:{}'.format(samplename, hla))

def main():
    ref = get_reference()

    predictions = {}
    for typer in ['optitype','hlassign','bwakit', 'phlat']:
        predictions.update({typer:readin(typer = typer)})

    print_all(ref, predictions)
    pd = compare_ref_pred(ref, predictions)

    for typer, values in pd.items():
        print('{}:{}'.format(typer, values))

if __name__ == "__main__":
    main()
