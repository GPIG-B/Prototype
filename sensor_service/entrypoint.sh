#!/bin/bash

set -e

DIR=$(dirname "$0")

$DIR/cli.py \
    --manager_host manager \
    --manager_port 6789
