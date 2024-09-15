#!/bin/bash

CWB=$HOME/cwb-demo

echo "Create directories"
mkdir -p $CWB/data/verne_mittelpunkt
mkdir -p $CWB/data/verne_interior
mkdir -p $CWB/data/verne_interior_short
mkdir -p $CWB/data/verne_mittelpunkt_short
mkdir -p $CWB/registry

echo "Remove prior versions of demo corpora"
rm -f $CWB/data/verne_mittelpunkt/*
rm -f $CWB/data/verne_interior/*
rm -f $CWB/registry/verne_mittelpunkt
rm -f $CWB/registry/verne_interior

echo "Encode verne_reise_nach_dem_mittelpunkt_der_erde.txt"
cwb-encode -d $CWB/data/verne_mittelpunkt -R $CWB/registry/verne_mittelpunkt -f verne_reise_nach_dem_mittelpunkt_der_erde.txt -c utf8 -xsB -P pos -S corpus:0 -S text:0+id -S s:0+id

echo "Run cwb-make on VERNE_MITTELPUNKT"
cwb-make -r $CWB/registry -M 500 -V VERNE_MITTELPUNKT

echo "Encode verne_journey_into_the_interior_of_the_earth.txt"
cwb-encode -d $CWB/data/verne_interior -R $CWB/registry/verne_interior -f verne_journey_into_the_interior_of_the_earth.txt -c utf8 -xsB -P pos -S corpus:0 -S text:0+id -S s:0+id

echo "Rund cwb-make on VERNE_INTERIOR"
cwb-make -r $CWB/registry -M 500 -V VERNE_INTERIOR

echo "Encode verne_interior_short"
cwb-encode -d $CWB/data/verne_interior_short -R $CWB/registry/verne_interior_short -f verne_interior_short.txt -c utf8 -xsB -0 corpus -S s:0

echo "Run cwb-make on VERNE_INTERIOR_SHORT"
cwb-make -r $CWB/registry -M 500 -V VERNE_INTERIOR_SHORT

echo "Encode verne_mittelpunkt_short"
cwb-encode -d $CWB/data/verne_mittelpunkt_short -R $CWB/registry/verne_mittelpunkt_short -f verne_mittelpunkt_short.txt -c utf8 -xsB -0 corpus -S s:0

echo "Run cwb-make on VERNE_MITTELPUNKT_SHORT"
cwb-make -r $CWB/registry -M 500 -V VERNE_MITTELPUNKT_SHORT

echo "Done. Run:"
echo "    cqp -r $CWB/registry/ -e"
echo "to access VERNE_MITTELPUNKT or VERNE_INTERIOR."
