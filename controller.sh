#!/bin/bash

: ' 
    controller.sh --help       # usage help
    controller.sh              # look for "controller.ini" in same folder (°)
    controller.sh CN00         # run controller passing name "CN00" (°°)
    controller.sh CN00 1,10 30 # run controller passing name "CN00" and list of units "1,10" and delay (°°)

    (°)  : "controller.ini" needs to be a text file where first line is used as list of arguments (extra lines are ignored)
    (°°) : run "controller.py" in same folder possibly with additional arguments via "obedge" tool
'

NAM=$( basename -- "${BASH_SOURCE[0]}" )
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CWD=$(pwd)

filename="${NAM}"
extension="${filename##*.}"
filename="${filename%.*}"

INIFILE="${DIR}/$filename.ini"
EXEFILE="${DIR}/$filename.py"

function Usage() {
    echo "?Usage: $NAM [ --help | <name> <list_of_units> <delay> ] (e.g. $NAM CN00 1,10)" 1>&2
    exit 2
}

[[ $# -eq 0 && -f "${INIFILE}" ]] && params=($(head -n 1 "${INIFILE}")) || params=("$@")
num=${#params[@]}

[[ $num -ne 0 && $num -ne 1 && $num -ne 3 ]] && Usage
[[ $num -eq 1 && "$1" == "--help" ]]         && Usage

name="${params[0]}"
units="${params[1]}"
delay="${params[2]}"

echo obedge run -i \"${EXEFILE} ${name} ${units} ${delay}\" -q mqtt,auth,10.0.0.150:1883,feed,admin
obedge run  -q mqtt,auth,10.0.0.150:1883,feed,admin --queue-username test --queue-password test  -e 'p:./obdemo.py'  --console
