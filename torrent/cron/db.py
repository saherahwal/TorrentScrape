import MySQLdb as mdb
import sys
import os
import os.path
import time
import urllib2
import shutil
  
import re

DIR_PATH = '/home/neo/TorrentScrape/torrent/torrents'

def getTorrentId(cur, title, url, website):
    query = "SELECT id FROM torrent where t_title = '%s' AND t_website = '%s' AND t_url = '%s';" % (title, website, url)
    cur.execute(query)
    t_id = cur.fetchone()
    if t_id == None:
	return None
    return int(t_id[0])
  
def main(argv=None):
      
    if argv is None:
        argv = sys.argv
  
    con = None
    cur = None

    files = getFiles()
  
    try:
        con = mdb.connect(host='localhost', user='neo', passwd='1234', db='6885')

	for filename in files:
		f = open(DIR_PATH + "/" + filename, "r")
		print filename
		lines = f.readlines()	
		f.close()	
		cur = con.cursor()
	      	cur.execute("START TRANSACTION;")
		cur.execute("BEGIN;")
		dt = filename[:filename.rindex(".")].split("-")
		t_date = dt[3] + "-" + dt[1] + "-" + dt[2]
		t_time = dt[4] + "00"
                query = "INSERT INTO date_time(t_date, t_time) VALUES(date('%s'),time('%s'));" % (t_date, t_time)
		cur.execute(query)
		query = "SELECT id from date_time where t_date = date('%s') AND t_time = time('%s')" % (t_date, t_time)
		cur.execute(query)
		dt_id = int(cur.fetchone()[0])
		
	        for line in lines:
			try:
				line = [word.replace("'", "*") for word in line.split(",")]
				website = line[0]
				category = line[1]
				title = line[2]
				url = line[3]
				age = line[4]
				seed = line[5]
				sizeType = line[6]
				torrent = line[7]
				leech = line[8]
				size = line[9]
				t_id = getTorrentId(cur, title, url, website)
				if (t_id == None):
			                query = "INSERT INTO torrent " + \
						" (t_website, t_category, t_title, t_url, t_sizeType, t_torrent, t_size) " + \
						"  VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s'); " % (website, category, title, url, sizeType, torrent, size)
					cur.execute(query)
					t_id = getTorrentId(cur, title, url, website)
		                query = "INSERT INTO torrent_datetime " + \
					" (torrent_id, datetime_id, age, leechers, seeders) " + \
					"  VALUES(%d, %d, '%s', '%s', '%s'); " % (t_id, dt_id, age, leech, seed)
				try:
            				cur.execute(query)
					#pass
			        except Exception, e:
        	        		print e
        	        		#cur.execute("ABORT;")
		        	        pass
			except Exception, e:
				print filename, line, e
				continue
		cur.execute("COMMIT;")
		os.rename(DIR_PATH + "/" + filename, DIR_PATH + "/done/" + filename)
    except mdb.Error, e:
	try:
		cur.execute("ABORT;")
	except:
		pass
        
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
  
    finally:
          
        if con:
            con.close()

def getFiles():
	files = os.listdir(DIR_PATH)	
	files = [filename for filename in files if os.path.isfile(DIR_PATH + "/" + filename)]
#	return [DIR_PATH + "/" + file for file in files]
	return files
  
if __name__ == "__main__":
    sys.exit(main())
