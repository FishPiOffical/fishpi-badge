#!/bin/bash
kill $(pidof python)
nohup flask run --host=0.0.0.0 &
tail -f nohup.out
