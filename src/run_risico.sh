#!/bin/bash

echo "Container args: $@"

sudo chown -R risico:risico ./data
# docker run -v /Volumes/data-sd/docker/wrf-02072018_00UTC/wrf/:/home/risico/wrf risico/builder

if [ "$#" -eq 1 ]; then
  RUN_DATE=$1
else
  RUN_DATE="${RISICO_RUN_DATE}"
fi

cd /home/risico/
export PYTHONPATH=$PYTHONPATH:/home/risico/adapter/
echo "Convert WRF files"
adapter/.venv/bin/python adapter/importer.py data/wrf/ data/observations input/ input_files.txt
echo "Run RISICO"
./RISICO2015 $RUN_DATE risico/configuration.txt input_files.txt
echo "Export file"
adapter/.venv/bin/python adapter/exporter.py risico/OUTPUT/ data/output/risico_$RUN_DATE.nc $RUN_DATE