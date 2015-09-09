#!/bin/bash

for i in analysis/*
do
	id=$(basename $i)

	mkdir -p $i/hla_typing/optitype
	cp -R work/*$id/* $i/hla_typing/optitype
done
