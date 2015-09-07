#!/bin/bash

filename='dev/list_cells'
echo Start
while read LINE; do 
	mkdir -p samples/$LINE/fastq/original
done < $filename
