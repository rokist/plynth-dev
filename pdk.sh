#!/bin/sh

CWDIR=`pwd`

WORKING_DIR=`dirname $0`

cd $WORKING_DIR

WORKING_DIR=`pwd`


PLYNTH_ENV_DIR="__plynth_venv"

back_command=".back_command"
next_command=".next_command"

if test -e $back_command ; then
    rm $back_command
fi
if test -e $next_command ; then
    rm $next_command
fi

__utils/python -B -u __utils/pdk.py "[$WORKING_DIR]" $*

for i in {1..8}; do
    if test -e $back_command ; then
        command_list=`cat $back_command`
        rm $back_command

        idx=0
        while read line
        do
            idx=$(expr $idx + 1)
            declare var$idx="$line"
        done <<END
        $command_list
END

        $var1
        $var2
        $var3
        $var4
        $var5
        $var6
        $var7

        cd $WORKING_DIR
    fi

    if test -e $next_command test then
        command_list=`cat $next_command`
        rm $next_command

        #echo $command_list

        if test $command_list == "__same__" test; then
            __utils/python -B -u __utils/pdk.py "[$WORKING_DIR]" $*
        else
            __utils/python -B -u __utils/pdk.py "[$WORKING_DIR]" $command_list
        fi

    fi
done
