#!/bin/bash

archive=$1
target_dir=$2

cd $target_dir
unzip $1
./manage.py migrate
