#!/bin/bash

set -e

Help()
{
    echo "Search for terms in the research log."
    echo
    echo "Syntax: run-backup.sh -u <url> -o <outpath>"
    echo
    echo "Options:"
    echo "--arango-url | -u            The API url to get all the data from"
    echo "--outpath | -o               The outpath to write the backup to locally"
    echo "--password                   The password to login to the DB"
    echo "--username                   The username to login to the DB"
    echo "-h | --help                  Display this help message"
    echo
}

while [ $# -gt 0 ]; do
    case "$1" in
	--arango-url|-u) ARANGO_URL="$2"; shift 2 ;;
	--outpath|-o) OUTPATH="$2"; shift 2 ;;
	--password) PASSWORD="$2"; shift 2 ;;
	--username) USERNAME_="$2"; shift 2 ;;
	-h|--help) Help; exit ;;
	*) echo "Invalid option: $1" >&2; exit 1 ;;
    esac
done

year=$( date +%Y )
month=$( date +%m )
day=$( date +%d )

if [ -z ${ARANGO_URL+x} ]; then
    ARANGO_URL="_NULL"
fi

if [ -z ${OUTPATH+x} ]; then
    OUTPATH="backups/$year-$month-$day/"
fi

if [ -z ${PASSWORD+x} ]; then
    PASSWORD="_NULL"
fi

if [ -z ${USERNAME_+x} ]; then
    USERNAME_="_NULL"
fi

# first get all the data and write it to the backups outpath
python3 $(dirname $0)/backup.py \
	--arango-url $ARANGO_URL \
	--outpath $OUTPATH \
	--password $PASSWORD \
	--username $USERNAME_

# then zip the output
zip -r "${OUTPATH%/}.zip" "$OUTPATH"

# and remove the old directory
rm -r $OUTPATH
