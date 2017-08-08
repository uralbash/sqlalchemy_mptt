#! /bin/bash
#
# test.sh
# Copyright (C) 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
#
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
PROJECT_NAME='sqlalchemy_mptt'

RST_FILES=`find . -name "*.rst" -printf "%p "`
RST_CHECK=$(rstcheck $RST_FILES               \
              --ignore-directives code-block  \
              --report 2 3>&1 1>&2 2>&3 | tee >(cat - >&2)) # fd=STDERR_FILENO
FLAKE8=$(flake8 ./$PROJECT_NAME/)

echo -e "${RED}"
# if [ -n "$RST_CHECK" ] ||
if [ -n "$FLAKE8" ]
then
    echo -e "RST_CHECK: ${RST_CHECK:-OK}"
    echo -e "FLAKE8: ${FLAKE8:-OK}"
    exit 1
else
    echo -e "${GREEN}OK!"
fi
echo -e "${NC}"
