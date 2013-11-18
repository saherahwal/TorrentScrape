import MySQLdb as mdb
import sys
import os
import os.path
import time
import urllib2
import shutil
  
import re

DIR_PATH = '/home/neo/TorrentScrape/torrent/torrents'
  
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
		cur.execute("COMMIT;")
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
				dt = filename[:filename.rindex(".")].split("-")
				t_date = dt[3] + "-" + dt[1] + "-" + dt[2]
				t_time = dt[4]
		                query = "INSERT INTO torrents " + \
					" (t_website, t_category, t_title, t_url, t_age, t_seed, t_sizeType, t_torrent, t_leech, t_size, t_date, t_time) " + \
					"  VALUES('"  + website + "','" + category + "', '" + title + "', '" + url + "', '" + age + "', '" + seed + "', '" + sizeType + "', '" + torrent + "', '" + leech + "','" + size + "', date('" + t_date  + "'), time('" + t_time + "'));"
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
