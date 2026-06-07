#!/bin/bash
# 根据 PID 杀死子进程
#pkill -P $(pgrep -f 't4_daemon')
#pkill -9 -g $(ps -o pgid= -p $(pgrep -f 't4_daemon'))
kill -9 $(pgrep -f 't4_daemon')