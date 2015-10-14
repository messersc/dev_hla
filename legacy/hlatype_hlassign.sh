#!/bin/bash

# Change before running
export TMPDIR=/vol/local/scratch/cmessers
export PDIR=/home/cmessers/biotools/HLAssign_cli_pilot/pilot_source_code

# load modules
# module load BLAT
export PATH=${PATH}:/home/cmessers/biotools/BLAT/
module load R || echo No R module

run_hlassign()
{
    export sample=$1
    set -x
		${PDIR}/run_HLAssign_CLI \
		../samples/${sample}/fastq/original/*_R1_*.fastq.gz \
        ../samples/${sample}/fastq/original/*_R2_*.fastq.gz \
		../analysis/${sample}/hla_typing/hlassign
}
export -f run_hlassign


for sample in CELL_ID_108 CELL_ID_109 CELL_ID_122 CELL_ID_13 CELL_ID_16 CELL_ID_163 CELL_ID_165 CELL_ID_18 CELL_ID_21 CELL_ID_235 CELL_ID_36 CELL_ID_38 CELL_ID_39 CELL_ID_41 CELL_ID_45 CELL_ID_56 CELL_ID_6 CELL_ID_79 CELL_ID_94 CELL_ID_99; 
do
	mkdir -p ../analysis/${sample}/hla_typing/hlassign/
	run_hlassign ${sample}
done
