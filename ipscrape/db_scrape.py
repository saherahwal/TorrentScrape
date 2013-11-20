import MySQLdb as mdb
import MySQLdb.cursors as cursors
import subprocess
import sys
import bencode
import hashlib
import udphttpscraper
from readtorrent import *

#def get_decoded_tracker_response(url):
#    agent="'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4)'"
#    proc = subprocess.Popen([
#"curl", "--globoff", "--compressed", "-A", agent , "-L", "--post302", url], stdout= subprocess.PIPE)
#    out, err = proc.communicate()
#    print bencode.bdecode(out)


def get_next_url(cursor):
    """ given the DB cursor from connection.cursor() call, yields the next url in the torrent DB"""
        
    query = "SELECT t_torrent FROM torrents WHERE t_torrent NOT LIKE 'magnet:?%';"
    cursor.execute("START TRANSACTION;")
    cursor.execute("BEGIN;")

    try:
        cursor.execute(query)
        for row in cursor:
            yield row
    except Exception, e:
        print "Error when executing query %d : %s" % (e.args[0], e.args[1])
        sys.exit(1)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    con = None
    
    try:
        print "connecting to DB"
        con = mdb.connect(host = "tal.xvm.mit.edu", user="neo", passwd='1234', db='6885', cursorclass=cursors.SSCursor)
        print "conn success"
        cursor = con.cursor()
        
        db_iter = get_next_url(cursor) #DB iterator

        for t in db_iter:
            try:
                url = t[0]
                meta_info = bencode.bdecode(get_decoded_indexer_response(url))
                
                info_hash = None
                announce = None
                announce_list = None
                if 'info' in meta_info and 'announce' in meta_info:
                    info_hash = hashlib.sha1(bencode.bencode(meta_info['info'])).hashdigest()
                    announce = meta_info['announce']
                    try_announce_list = [announce]
                    if 'announce-list' in meta_info:
                        for _aList in meta_info['announce-list']:
                            for _announce in _aList:
                                try_announce_list.append(_announce)                       
                    print "try_announce_list", try_announce_list                    
                   
            except Exception, e:
                print "Error curl and decode:", e
                print "cannot decode torrent file"
                continue    
                        
            
    except mdb.Error, e:
         print "Error %d : %s" % (e.args[0], e.args[1])         
         sys.exit(1);
    
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    sys.exit(main())



