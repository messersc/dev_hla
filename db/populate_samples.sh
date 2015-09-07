#!/bin/bash

# script to populate our 'database' with the cell lines from HLAssign

# remove after testing, this is to make sure that no entries for our project exist yet
git checkout  donor.tsv project.tsv sample.tsv

# add project (once)

PROJECT=$(./manage_table.py add_project \
        --institution BIH \
        --organization "HLA typing" \
        --pi "NA" \
        --project-pk "HLA")

#PROJECT=HLA
echo $PROJECT

# add donor for each cell line

while read CELL;

do
	DONOR=$(./manage_table.py add_donor \
        --customer-id ${CELL} \
        --project-pk ${PROJECT})

	echo $DONOR

	# add sample for each cell line

	VARSAMPLE=$(./manage_table.py add_sample --customer-id ${CELL}_normal_panel --donor-pk ${DONOR} --project-pk ${PROJECT} \
			--info cell_table=normal --info platform=HiSeq --info seq_typ=panel)
	echo $VARSAMPLE	

done < /vol/cs02/scratch/cmessers/projects/BIH/HLA/metadata/list_cells
