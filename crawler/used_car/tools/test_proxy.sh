#!/bin/bash

proxies=`cat $(dirname $0)/../../proxy-ypp.txt`
url=http://www.toolsvoid.com/what-is-my-ip-address
url1=https://sfbay.craigslist.org/robots.txt

for proxy in $proxies; do
    echo "$proxy"
    #curl --socks5 "${proxy/socks5:\/\//}" $url 2>/dev/null |grep "IP Address" |grep "strong"
    curl --proxy "${proxy/http:\/\//}" $url 2>/dev/null |grep "IP Address" |grep "strong"
    #curl --socks5 "${proxy/socks5:\/\//}" $url1 2>/dev/null
done
