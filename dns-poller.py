#!/usr/bin/python
import dns.resolver
import time
import urllib
import urllib2
import json

domain = # 	<---- The dynamically updating test domain
url = "https://www.cloudflare.com/api_json.html"
key = # 	<---- Fill this in with your own api key
email = # 	<---- Fill this ine with your own cloudflare login email
zone = # 	<---- Your own email domain
record = # 	<---- The record to assess

def getCurrentIP():
    myResolver = dns.resolver.Resolver()
    myAnswers = myResolver.query(domain, "A")
    myResolver.nameservers = ['ns1.dyndns.org', 'ns2.dyndns.org']

    for rdata in myAnswers:
	if rdata != 0:
            return rdata

def getRecID(record):
    query_args = { 'a':'rec_load_all', 'tkn':key, 'email':email, 'z':zone }
    encoded_args = urllib.urlencode(query_args)
    req = urllib2.Request(url, encoded_args)
    response = urllib2.urlopen(req)
    dump = json.load(response)

    for line in dump['response']['recs']['objs']:
	if line.get('name') == record:
	    return line.get('rec_id')

def getSetIP(record):
    query_args = { 'a':'rec_load_all', 'tkn':key, 'email':email, 'z':zone }
    encoded_args = urllib.urlencode(query_args)
    req = urllib2.Request(url, encoded_args)
    response = urllib2.urlopen(req)
    dump = json.load(response)

    for line in dump['response']['recs']['objs']:
        if line.get('name') == record:
            return line.get('content')

def ipUpdate(newIP):
    record_id=getRecID(record)
    query_args = { 'a':'rec_edit', 'tkn':key, 'email':email, 'z':zone, 'content':newIP, 'name':record, 'type':'A', 'id':record_id, 'ttl':'120' }
    encoded_args = urllib.urlencode(query_args)
    req = urllib2.Request(url, encoded_args)
    response = urllib2.urlopen(req)
    dump = json.load(response)

    if dump.get('result') != "success":
	print "Failed to apply update: " + dump.get('msg')
    else:
        print "Updated IP to: " + dump['response']['rec']['obj']['content']

def ipPoller():    
    while True:
        ip1 = getCurrentIP()
 
 	ip2 = getSetIP(record)
   
        if str(ip1) != str(ip2):
	    print "New IP detected: "+ip1
	    ipUpdate(ip1)

 	time.sleep( 10 )
   
ipPoller() 
