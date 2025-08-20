#!/bin/bash

NAM=$( basename -- "${BASH_SOURCE[0]}" )
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CWD=$(pwd)

filename="${NAM}"
extension="${filename##*.}"
filename="${filename%.*}"

INIFILE="${DIR}/$filename.ini"
EXEFILE="${DIR}/$filename.py"

function Usage() {
    echo "?Usage: $NAM <type:path>" 1>&2
    exit 2
}

if [[ $# -ne 1 ]]; then
    Usage
fi

type="$1" 



obedge run -i "${EXEFILE} ${type}" -q mqtt,auth,10.0.0.150:1883,feed,admin --queue-username test --queue-password test -e "p:./newObdemo.py" -e "b:echo"  --console

