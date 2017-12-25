#!/bin/python3
import argparse, urllib3, hashlib, pymysql, sys, funcs, logging, db

BEG = 0; CUR = 1; END = 2
urllib3.disable_warnings()
base_url = "https://btcraig.in/"
webroot = "/var/www/html/"
log_level = logging.DEBUG

parser = argparse.ArgumentParser( prog="btshorten.py", description="Driver for btcraig.in link shortener." )
parser.add_argument( "uri", metavar="link", help="The link to shorten. If http/https is not included http:// will be automatically added." )
parser.add_argument( "ip", metavar="address", help="The IP address of the person attempting to create a shortened URI." )
parser.add_argument( "-m", "--manual", required=False, default=None, dest="hash", nargs=1, metavar="dest_string", help="Manually specify a string for the hash." )
args = parser.parse_args()

if args.hash is not None:
    disallow = [ "!><?:;{}[]|\/-+()*&^%$#@=_" ]
    for c in disallow:
        if c in args.hash:
            logging.debug( "Invalid char in manual mode!" )
            print( "[ERR] {} is not a valid character.".format( c ) )
            sys.exit( -1 )

logging.basicConfig( filename="/var/www/html/backend/shorten.log", level=log_level )
logging.debug( "URI :: {}\nIP :: {}\n\n".format( args.uri, args.ip ) )

if not ( "http://" in args.uri or "https://" in args.uri ):
    uri = "http://{}".format( args.uri )
else:
    uri = args.uri
while args.uri[len(args.uri)-1] is '/':
    args.uri = args.uri[:len(args.uri)-1]

try:
    http = urllib3.PoolManager()
    res = http.request( "HEAD", uri, timeout=.75 )
    logging.debug( "URI :: {}".format( uri ) )
    if res.status == 405:
        res = http.request( "GET", uri, timeout=.75 )
        logging.info( "Failed to 'HEAD' URI( {} ) got status -- {}".format( uri, res.status ) )
    if not res.status == 200:
        logging.warning( "Failed to contact: {}".format( uri ) )
        print( "[ERR] {} does not appear to be reachable.".format( uri ) )
        sys.exit( -1 )
except urllib3.exceptions.MaxRetryError:
    logging.warning( "Failed to contact: {}".format( uri ) )
    print( "[ERR] Could not contact {}.".format( uri ) )
    sys.exit( -1 )

if args.hash == None:
    m = hashlib.md5()
    m.update( uri.encode() )
    hash = m.hexdigest()
    hash_s = hash[:6]
else:
    logging.debug( args.hash )
    hash = args.hash[0]
    hash_s = args.hash[0]
conn = pymysql.connect( host=db.host, user=db.user, password=db.password, db=db.name, charset=db.cset, cursorclass=pymysql.cursors.DictCursor )
try:
    with conn.cursor() as cursor:
        query = "SELECT * FROM uri WHERE hash_long RLIKE '{}'".format( hash )
        logging.debug( query )
        cursor.execute( query )
        res = cursor.fetchone()
        if args.hash is not None and res is not None: #collision
            logging.warning( "COLLISION -- TAR: {} HASH: {}".format( uri, hash ) )
            if uri == res["target"]:
                print( "{}{}".format( base_url, res["hash_short"] ) )
                sys.exit( 0 )
            print( "[ERR] Collision detected on manual mode. Terminating." )
            sys.exit( -1 )
        while args.hash is not None and res is not None:
            if res["target"] == uri:
                print( "{}{}".format( base_url, res["hash_short"] ) )
                sys.exit( 0 )
            m = hashlib.md5()
            m.update( ( uri+funcs.rand_digits( 6 ) ).encode() )
            hash = m.hexdigest()
            hash_s = hash[:6]
            res = cursor.fetchone()
        ins_query = "INSERT INTO uri (creator_ip, target, hash_short, hash_long) VALUES('{}', '{}', '{}', '{}')".format( args.ip, uri, hash_s, hash )
        logging.debug( ins_query )
        cursor.execute( ins_query )
        conn.commit()
        with open( "{}.htaccess".format( webroot ), "a" ) as f:
            f.seek( 0, END )
            f.write( "Redirect 301 /{} {}\n".format( hash_s, uri ) )
            f.close()
        print( "{}{}".format( base_url, hash_s ) )
        sys.exit( 0 )
finally:
    conn.close()
