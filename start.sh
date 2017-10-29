#!/usr/bin/env bash

pushd frontend
mkdir -p /www/data
npm install && npm run build --production
cp -r build/* /www/data/
popd

docker-compose -f $(dirname $0)/docker-compose-prod.yml up -d