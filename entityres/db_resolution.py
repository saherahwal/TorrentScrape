import MySQLdb as mdb
import MySQLdb.cursors as cursors
import subprocess
import sys
import datetime
import time

COMMON = ["the", "a", "an", "and", "avi", "mpg", "mp3", "rar", "-"] + [str(x) for x in range(0,9)]

class Torrent:
    def __init__(self, row):
        self.id = row[0]
        self.title = row[1].strip().lower()
        self.size = float(row[2].strip())
        self.sizetype = row[3].strip().lower()
        self.torrent = row[4].strip().lower()
        self.url = row[5].strip().lower()
        self.website = row[6].strip().lower()


def get_torrents(cursor):
    """ given the DB cursor from connection.cursor() call, yields the next torrent in the torrent DB"""
        
    query = "SELECT id, t_title, t_size, t_sizetype, t_torrent, t_url, t_website FROM torrent;"
    try:
        cursor.execute(query)
        for row in cursor:
            yield row
    except Exception, e:
        print "Error when executing query ", e
        sys.exit(1)



def get_torrent_by_name(cursor, t_name):
    """ given the cursor from connection to DB, get the data row of location for given ip
        
        Args: 
             cursor: cursor from connection.cursor() 

             ip: int-32 of the ip address for location lookup
    """
    query = "SELECT id, t_title, t_size, t_sizetype, t_torrent, t_url, t_website FROM torrent WHERE t_title LIKE '%" + str(t_name) + "%';"
    try:
        cursor.execute(query)
        for row in cursor:
            yield row

    except Exception as e:
        print "Error when looking up location for ip= ", ip ,". %d: %s" % (e.args[0], e.args[1])


def insert_dups(cursor, date, time):
    """ given cursor, date, time: add date and time to the database """
    query = "INSERT INTO date_time (`t_date`, `t_time`) VALUES (date('%s'), time('%s'));" % (date, time)
    try:
        cursor.execute("START TRANSACTION;")
        cursor.execute("BEGIN;")
        cursor.execute(query)
        cursor.execute("COMMIT;")
        #print "insert success" 
    except Exception as e:
        print "Could not add date %s and time %s to date_time table: " % (date, time), e

         
            
def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    con = None
    
    host = "tal.xvm.mit.edu"
    user = "neo"
    passwd = "1234"
    db = "6885"
    

    try:
        print "connecting to DB"
        con_db = mdb.connect(host = host, user=user, passwd=passwd, db=db , cursorclass=cursors.SSCursor)
        con_torrent = mdb.connect(host = host, user=user, passwd=passwd, db=db , cursorclass=cursors.SSCursor)
        
        cur = con_db.cursor()
        
        for torr_data in get_torrents(cur):
	    t = time.time()
            record_score = 0.0
            record_id = ""
            #try:
            t_orig = Torrent(torr_data)
	    print t_orig.id
            cur_t = con_torrent.cursor()
            maxscore = 10.0
	    words = t_orig.title.split(" ")
	    if t_orig.title.count(" ") < t_orig.title.count("."):
            	words = t_orig.title.split(".")
#	    else:
#		words += t_orig.title.split(".")
	    words = [word for word in words if word not in COMMON]
	    print words
            for word in words:
	    	for data in get_torrent_by_name(cur_t, word):
                	t_check = Torrent(data)
                        if t_check.id != t_orig.id:
                            if t_orig.title == t_check.title and \
                                t_orig.size == t_check.size:
                                    print t_orig.id, t_check.id
                            elif levenshtein(t_orig.title, t_check.title) < 10.0 \
                                and t_orig.size < t_check.size + 1 and t_orig.size > t_check.size - 1:
                                    print t_orig.id, t_check.id
	    print time.time() - t
        
            cur_t.close()
             
                   
            #except Exception, e:
             #   print "Error: ", e
              #  print "ERROR"
               # continue    
        cur.close()            
    except mdb.Error, e:
         print "Error %d: %s " %  (e.args[0], e.args[1])         
         sys.exit(1);
    
    finally:
        con_db.close()
        con_torrent.close()

if __name__ == "__main__":
    sys.exit(main())



