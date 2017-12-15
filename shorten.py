#!/bin/python3
import argparse, urllib3, hashlib, pymysql, sys, db, funcs
# "macro" for file.seek()
BEG = 0
CUR = 1
END = 2

# who needs safety
urllib3.disable_warnings()

# arg parsing...
parser = argparse.ArgumentParser( prog="btshortn.py", description="Driver for btcraig.in link shortener." )
parser.add_argument( "uri", metavar="link", help="The link to shorten. If http/https is not included http:// will be automatically added." )
parser.add_argument( "ip", metavar="address", help="The IP address of the person attempting to create a shortened URI." )
args = parser.parse_args()
base_url = "https://btcraig.in/"
webroot = "/var/www/html/"

# add http if http/s not included and trim trailing '/'
if not ( "http://" in args.uri or "https://" in args.uri ):
    uri = "http://{}".format( args.uri )
else:
    uri = args.uri
while args.uri[len(args.uri)-1] is '/':
    args.uri = args.uri[:len(args.uri)-1]

# attempt to fetch the uri to check for 200
http = urllib3.PoolManager()
try:
    res = http.request( 'HEAD', uri, timeout=2.5 )
    if not res.status == 200:
        print( "[ERR] {} does not appear to be reachable." )
        sys.exit( -1 )
except urllib3.exceptions.MaxRetryError:
    print( "[ERR] Could not contact {}.".format( uri ) )
    sys.exit( -1 )

# initial hash
m = hashlib.md5()
m.update( uri.encode() )
hash = m.hexdigest()

# check for collisions and insert
try:
    # connect to sql
    conn = pymysql.connect( host="localhost", user=db.user, password=db.password, db=db.name, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor )
    with conn.cursor() as cursor:
        query = "SELECT * FROM uri WHERE hash_long RLIKE '{}'".format( hash )
        cursor.execute( query )
        res = cursor.fetchone()
        while res is not None:
            if res["target"] == uri:
                print( "{}{}".format( base_url, res["hash_short"] ) )
                sys.exit( 0 )
            m = hashlib.md5()
            m.update( ( uri+funcs.rand_digits( 6 ) ).encode() )
            hash = m.hexdigest()
            res = cursor.fetchone()
        ins_query = "INSERT INTO uri (creator_ip, target, hash_short, hash_long) VALUES('{}', '{}', '{}', '{}')".format( args.ip, uri, hash[:6], hash )
        cursor.execute( ins_query )
        conn.commit()
        # insert into .htaccess -- since we got a uniq hash we can safely insert
        with open( "{}.htaccess".format( webroot ), "a" ) as f:
            f.seek( 0, END )
            f.write( "Redirect 301 /{} {}\n".format( hash[:6], uri ) )
            f.close()
        print( "{}{}".format( base_url, hash[:6] ) )
        sys.exit( 0 )
finally:
    conn.close()
