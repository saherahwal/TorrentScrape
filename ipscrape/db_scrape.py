import MySQLdb as mdb
import MySQLdb.cursors as cursors
import subprocess
import sys
import bencode
import hashlib
from udphttpscraper import *
from readtorrent import *
import datetime


def get_next_url(cursor):
    """ given the DB cursor from connection.cursor() call, yields the next url in the torrent DB"""
        
    query = "SELECT t_torrent, id, t_url FROM torrent WHERE t_torrent NOT LIKE 'magnet:?%';"
    try:
        cursor.execute(query)
        for row in cursor:
            yield row
    except Exception, e:
        print "Error when executing query ", e
        sys.exit(1)



def do_location_lookup(cursor, ip):
    """ given the cursor from connection to DB, get the data row of location for given ip
        
        Args: 
             cursor: cursor from connection.cursor() 

             ip: int-32 of the ip address for location lookup
    """
    assert type(ip) == int
    query = "SELECT * FROM ip2location_db9 WHERE %s >= `ip_from` AND %s <= `ip_to`;" % (str(ip), str(ip))
    try:
        cursor.execute(query)
        for row in cursor:
            yield row

    except Exception as e:
        print "Error when looking up location for ip= ", ip ,". %d: %s" % (e.args[0], e.args[1])


def get_id_date_time(cursor, date, time):
    """ given the cursor, date and time returns the id of the associated date and time """
    query = "SELECT id FROM date_time WHERE `t_date` = date('%s') AND `t_time` = time('%s');" % (date, time)
    try:
        cursor.execute(query)
        return  cursor.fetchone()        
    except Exception as e:
        print "Error when getting date and time from date_time table for date %s and time %s " % (date, time) , e  



def insert_date_time(cursor, date, time):
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

         

def insert_torrent_location(cursor, torrent_id, datetime_id, ip, location):
    """ given cursor, torrent_id, datetime_id, ip, and location: add new location row to 
         torrent_location 

         location example: (407753984L, 407768319L, 'CA', 'CANADA', 'MANITOBA', 'WINNIPEG', 49.8844, -97.14704, 'R2C 0A1')
                format is (ip_from, ip_to, country_code, country_name, region, city, latitude, longitude, zip)
    """
    query = "INSERT INTO torrent_location (`torrent_id`, `ip`, `country_code`, `country_name`, `region_name`, \
`city_name`, `latitude`, `longitude`, `zip_code`, `ipv4`, `datetime_id`) VALUES ( %d, %d, '%s', '%s', '%s', '%s', %u, %u, '%s', '%s', %d);" % (torrent_id, ip, location[2], location[3], location[4], location[5], location[6], location[7], location[8], to_string(ip), datetime_id)
    #print "the query is ", query
    try:
        cursor.execute("START TRANSACTION;")
        cursor.execute("BEGIN;")
        cursor.execute(query)
        cursor.execute("COMMIT;")
        print "[location insertion success]"        
    except Exception as e:
        print "Could not add new location row to `torrent_location` table: ", e  
           
    
def fix_url(url):
    """ pirates bay hacky fix for url since it is stored incorrectly """
    if len(url) > 2:
        if url[:2] == '//':
            return "http:" + url
    return url
            



def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    con_select = None
    con_lookup = None
    con_insert = None
    con_datetime = None
    con_dt_insert = None
    host = "tal.xvm.mit.edu"
    user = "neo"
    passwd = "1234"
    db = "6885"
    

    try:
        print "connecting to DB"
        con_select = mdb.connect(host = host, user=user, passwd=passwd, db=db , cursorclass=cursors.SSCursor)
        print "con_select success"
        con_lookup = mdb.connect(host = host, user=user, passwd=passwd, db=db, cursorclass=cursors.SSCursor)        
        print "con_lookup success"
        con_datetime = mdb.connect(host = host, user=user, passwd=passwd, db=db, cursorclass=cursors.SSCursor)
        print "con_datetime success"
        con_dt_insert = mdb.connect(host = host, user=user, passwd=passwd, db=db, cursorclass=cursors.SSCursor)
        print "con_dt_insert success"
        con_insert = mdb.connect(host = host, user=user, passwd=passwd, db=db, cursorclass=cursors.SSCursor)        
        print "con_insert success"

        cur_select = con_select.cursor()
        cur_dtinsert = con_dt_insert.cursor() 
       
        db_iter = get_next_url(cur_select) #DB iterator
                       
        for torr_data in db_iter:            
            cur_datetime = con_datetime.cursor()
            cur_insert = con_insert.cursor()
            try:
                url = fix_url(torr_data[0])
                ref = torr_data[2] # for seedpeer referal
                            
                                                
                meta_info = None
                if "seedpeer" in url:
                    i = url.index("/download/")
                    meta_info = bencode.bdecode(get_decoded_indexer_response(url, url[:i]+ ref))
                else:
                    meta_info = bencode.bdecode(get_decoded_indexer_response(url))
                
                info_hash = None
                announce = None
                announce_list = None
                if 'info' in meta_info and 'announce' in meta_info:
                    info_hash = hashlib.sha1(bencode.bencode(meta_info['info'])).hexdigest()
                    announce = meta_info['announce']
                    try_announce_list = [announce]
                    if 'announce-list' in meta_info:
                        for _aList in meta_info['announce-list']:
                            for _announce in _aList:
                                try_announce_list.append(_announce)
                     
                    #print "try_announce_list", try_announce_list                    
                    scrape_ip_res = scrape_tracker(try_announce_list, info_hash)
                    #print "res IPs", scrape_ip_res  

                  
                    now = datetime.datetime.now()
                    date = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
                    time = str(now.time().hour)+":"+str(now.time().minute)+":"+str(now.time().second)


                    dt_lookup = get_id_date_time(cur_datetime, date, time)              
                    dt_id = None        
                    if dt_lookup is None:
                        insert_date_time(cur_datetime, date, time)
                        dt_lookup = get_id_date_time(cur_datetime, date, time)
                        #print "dt_found", dt_lookup[0]                                               
                    
                        #print "dt_found=", dt_lookup[0]
                    dt_id = dt_lookup[0] ##datetime id or timestamp id
                    #cur_datetime.close()
 
                    while scrape_ip_res !=  set([]):
                        cur_lookup = con_lookup.cursor()
                        ip_tup = scrape_ip_res.pop()
                        ip = ip_tup[1]
                        #print "ip is", ip
                        location = do_location_lookup(cur_lookup, ip)
                        loc = location.next()
                        #print "location =",loc
			insert_torrent_location(cur_insert, torr_data[1], dt_id, ip, loc)

                cur_datetime.close()
                cur_insert.close()                                     
             
                   
            except Exception, e:
                print "Error: ", e
                print "ERROR"
                continue    
        cur_select.close()
        cur_dtinsert.close()                    
            
    except mdb.Error, e:
         print "Error %d: %s " %  (e.args[0], e.args[1])         
         sys.exit(1);
    
    finally:
        if con_select:
            con_select.close()
        if con_lookup:
            con_lookup.close()
        if con_dt_insert:
            con_dt_insert.close()
        if con_datetime:
            con_datetime.close()
        if con_insert:
            con_insert.close()

if __name__ == "__main__":
    sys.exit(main())



