#!/bin/bash
cd /home/saher/MEng/TorrentScrape/ipscrape
from=$1
to=$2
while [ $from -lt $to ];
do 
    let t=from+$3
    echo "calling db scrape from $from to $t"
    python db_scrape.py $from $t& 
    let from=t
done
