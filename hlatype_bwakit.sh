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



for sample in CELL_ID_16; 
do
	mkdir -p ../analysis/${sample}/hla_typing/bwakit/
	run_bwakit ${sample} | sh
done


#parallel -j 2 -v 'run_optitype {}' ::: BIH-002 BIH-004 BIH-016 BIH-02
