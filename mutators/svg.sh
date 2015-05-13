#!/bin/bash

MAX=500

while true; do
	n=`curl -s http://localhost:1337/howmany`

	if [ $n -lt $MAX ]; then
		echo -n "[`date`] queue low ($n), generating more tests.. "
	fi


	while [ $n -lt $MAX ]; do
		FILE=`ls svg | sort -R | head -n1`
		ctype=`file --mime-type -b svg/$FILE` 
		if [ "$ctype" == "text/plain" ]; then
			ctype="text/html"
		fi

		cat svg/$FILE | ./radamsa > /tmp/suchfuzz.html
		curl -s -X POST -H "Content-Type: $ctype" --data '@/tmp/suchfuzz.html' http://localhost:1337/new > /dev/null
		let n=$n+1

		if [ $n -eq $MAX ]; then
			echo "done"
		fi
	done

	sleep 10 
done
