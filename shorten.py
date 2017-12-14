#!/bin/python3

import argparse, urllib3, hashlib, pymysql, sys, db

# who needs safety
urllib3.disable_warnings()

parser = argparse.ArgumentParser( prog="btshortn.py", description="Driver for btcraig.in link shortener." )
parser.add_argument( "uri", metavar="link", help="The link to shorten. If http/https is not included http:// will be automatically added." )
parser.add_argument( "ip", metavar="address", help="The IP address of the person attempting to create a shortened URI." )
args = parser.parse_args()

if not ( "http://" in args.uri or "https://" in args.uri ):
    uri = "http://{}".format( args.uri )
else:
    uri = args.uri
while args.uri[len(args.uri)-1] is '/':
    args.uri = args.uri[:len(args.uri)-1]

http = urllib3.PoolManager()
try:
    res = http.request( 'HEAD', uri )
    if not res.status == 200:
        print( "[ERR] {} does not appear to be reachable." )
        sys.exit( -1 )
except urllib3.exceptions.MaxRetryError:
    print( "[ERR] Could not contact {}.".format( uri ) )
    sys.exit( -1 )

m = hashlib.md5()
m.update( uri.encode() )
hash = m.hexdigest()[:6]

conn = pymysql.connect( host="localhost", user=db.user, password=db.password, db=db.name, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor )

try:
    with conn.cursor() as cursor:
        query = "SELECT hash_val FROM uri WHERE hash_val RLIKE '{}'".format( hash )
        print( query )
        cursor.execute( query )
        exists = False
        # TODO
        # Check if hash is in table
        # If hash in table, check target match
        # If hash in table and target match -- return existing URI
        # If hash is NOT in table insert entry into table, modify .htaccess
        # Return hashed URI to user
finally:
    conn.close()
