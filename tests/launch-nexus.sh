#!/bin/bash

rm -rf /src/tests/data/db
nexus testdb create admin admin --cbdir /src/tests/data
crossbar start --loglevel warn --config /src/tests/data/izaber.yaml
