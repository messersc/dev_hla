#!/bin/bash

filename='list_cells'
rm -r ../samples
while read LINE; do 
	mkdir -p ../samples/${LINE}/fastq/original
 	for FILE in ../incoming/${LINE}/*.fastq* ;
	do
		BASENAME=$(basename ${FILE})
		ln -svr ${FILE} ../samples/${LINE}/fastq/original/${BASENAME}
	done	
done < $filename
