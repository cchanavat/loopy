#!/bin/sh

# start - send - kill - logs


TYPE=$1
NAME=$2

case "$TYPE" in

	"start") screen -S $NAME -L -Logfile logs/$NAME.log ;;

	"send") screen -S $NAME -p 0 -X stuff "$3" ;;

	"kill") screen -X -S $NAME kill ;;
	
	"logs") screen -S $NAME -X colon "logfile flush 0^M"

esac 


