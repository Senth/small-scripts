#!/bin/bash

SIZES=(
	"32"
	"128"
	"152"
	"167"
	"180"
	"192"
	"196"
)

if [ $# -lt 1 ]; then
	echo "No icon specified"
	exit
fi

icon=$1

for size in "${SIZES[@]}"; do
	convert "$icon" -resize "${size}x${size}" "favicon-${size}.png"
done
