#!/bin/bash
# Downloads .torrent files from kat.ph links
# following redirects and getting the actual torrent
# filename

AGENT="'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4)'"

function usage(){
 	echo "Usage: $0 [Kat Torrent URL]"
 		exit 1
}

if [ ! -n "$1" ]
then
    usage
fi



name=`echo $1 | sed 's/(?:(?<protocol>http(?:s?)|ftp)(?:\:\/\/)) (?:(?<usrpwd>\w+\:\w+)(?:\@))? (?<domain>[^/\r\n\:]+)? (?<port>\:\d+)? (?<path>(?:\/.*)*\/)? (?<filename>.*?\.(?<ext>\w{2,4}))? (?<qrystr>\??(?:\w+\=[^\#]+)(?:\&?\w+\=\w+)*)* (?<bkmrk>\#.*)?//'`".torrent"

echo $name


curl --globoff --compressed -A '$AGENT' -L --post302 $1 > 'torrents/'$name'.tmp'
cd torrents && mv $name'.tmp' $name



