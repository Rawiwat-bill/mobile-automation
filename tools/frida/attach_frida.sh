#!/bin/bash
export PATH="$HOME/Library/Python/3.14/bin:$PATH"
frida -U -n com.bangkokbank.blue.dev -l "$1" > /tmp/frida_trace_live.log 2>&1
