#!/usr/bin/python
import dns.resolver
import time
import urllib
import urllib2
import json
import logging

domain =        <--- Replace with yours
url = "https://www.cloudflare.com/api_json.html"
key =           <--- Replace with yours
email =         <--- Replace with yours
zone =          <--- Replace with yours
record =        <--- Replace with yours

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d-%-y %H:%M:%S',
                    filename='/var/log/dnspoller.log',
                    filemode='a') 

logger = logging.getLogger()

def getCurrentIP():
    myResolver = dns.resolver.Resolver(configure=False)
    myResolver.nameservers = ['216.146.35.35', '216.146.35.36']

    try:
    	myAnswers = myResolver.query(domain, "A")
    except dns.resolver.Timeout:
	logger.error('DNS lookup timed out')

    try:
	for rdata in myAnswers:
	    if rdata != 0:
                return rdata
    except UnboundLocalError:
	logger.error('Unable to complete DNS lookup, see Error above')

def getDetail(record, field):
    query_args = { 'a':'rec_load_all', 'tkn':key, 'email':email, 'z':zone }
    encoded_args = urllib.urlencode(query_args)
    req = urllib2.Request(url, encoded_args)

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logger.error('Received HTTPError retrieving ' + field +' :' + str(e.code))
    except urllib2.URLError, e:
        logger.error('Received URLError retrieving record ID  ' + field + ' :' + str(e.reason))
    except urllib2.HTTPException, e:
        logger.error('Received HTTPException retrieving record ID')

    try:
        dump = json.load(response)
	try:
	    for line in dump['response']['recs']['objs']:
                if line.get('name') == record and line.get('type') == 'A':
                    return line.get(field)
	except KeyError:
            logger.debug("KeyError detected, see this: " + dump) 
    except UnboundLocalError:
	logger.error('Unable to complete Cloudflare DNS API lookup, see Error above')
	return None

def ipUpdate(newIP):
    record_id = getDetail(record, 'rec_id')
    query_args = { 'a':'rec_edit', 'tkn':key, 'email':email, 'z':zone, 'content':newIP, 'name':record, 'type':'A', 'id':record_id, 'ttl':'120' }
    encoded_args = urllib.urlencode(query_args)
    req = urllib2.Request(url, encoded_args)

    try:
	response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logger.error('Received HTTPError when updating IP: ' + str(e.code))
    except urllib2.URLError, e:
    	logger.error('Received URLError when updating IP: ' + str(e.reason))
    except urllib2.HTTPException, e:
    	logger.error('Received HTTPException when updating IP')	

    try:
    	dump = json.load(response)
        try:
    	    if dump.get('result') != "success":
	        logger.error("Failed to apply update: " + dump.get('msg'))
            else:
	        logger.info("Changed IP for " + record + " to: " + str(newIP))
	except KeyError:
	    logger.debug("KeyError detected, see this: " + dump)
    except UnboundLocalError:
	logger.error('Unable to complete Cloudflare DNS API Update, see Error above')
	return None	

def ipPoller():    
    while True:
        ip1 = getCurrentIP()
 
 	ip2 = getDetail(record, 'content')
   
	if ip2 == None:
	    logger.warn("Cloudflare DNS record not retrieved")
        elif str(ip1) != str(ip2):
	    logger.info("New IP for " + record + " detected: "+ str(ip1))
	    ipUpdate(ip1)
        else:
            logger.info("IP Address for " + record + " has not changed")

 	time.sleep( 10 )

ipPoller()
