#!/bin/bash
module load bwakit

repeat_arg()
{
    arg=$1
    shift
    set -x

    for x in $*; do
        echo $arg $x
    done
}

run_bwakit()
{
    sample=$1
    set -x
    run-bwamem -H \
        -o ../analysis/${sample}/hla_typing/bwakit/${sample} \
        -t 8 \
	/vol/fs01/data/.Cubi-Vault/static_data/precomputed/BWA/0.7.11/GRCh38/hs38DH/hs38DH.fa \
        ../samples/${sample}/fastq/original/*_R1_*.fastq.gz \
        ../samples/${sample}/fastq/original/*_R2_*.fastq.gz
}
export -f repeat_arg
export -f run_bwakit


# we can copy over the log files later if we like



for sample in CELL_ID_108 CELL_ID_109 CELL_ID_122 CELL_ID_13 CELL_ID_16 CELL_ID_163 CELL_ID_165 CELL_ID_18 CELL_ID_21 CELL_ID_235 CELL_ID_36 CELL_ID_38 CELL_ID_39 CELL_ID_41 CELL_ID_45 CELL_ID_56 CELL_ID_6 CELL_ID_79 CELL_ID_94 CELL_ID_99; 
do
	mkdir -p ../analysis/${sample}/hla_typing/bwakit/
	run_bwakit ${sample} | sh
done


#parallel -j 2 -v 'run_optitype {}' ::: BIH-002 BIH-004 BIH-016 BIH-02
