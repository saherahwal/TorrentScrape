# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import subprocess
import time
import urllib2
import os
#import pycurl
import cStringIO
from bencode import bencode

class TorrentPipeline(object):
    

    def __init__(self):
        if not os.path.exists('torrents'):
            os.makedirs('torrents')
        self.f = open('torrents/torrents-' + time.strftime('%m-%d-%Y-%H%M') + '.log', 'w+')
#	f.close()
#	    f = open('torrents/torrents.log', 'w')
#	    f.close()	
   
	  

#    def process_item(self, item, spider):
#	print "processing item now", item['title']
#        if not self.exists(item['title'][0]):
#	    print "starting item download"
#	    self.download_item(item)
#            time.sleep(5) # pause to prevent 502 errors 
#	return item

    
    def process_item(self, item, spider):
	s = ""
        c = ","
	if len(item['title']) > 0:
	 	for i in item:
			if isinstance(item[i], list):
				item[i] = item[i][0]
		#	s += item[i].replace(",", "*") + ","
	      	
                item['website'] = item['website'].replace(",", "*")
                item['category'] = item['category'].replace(",", "*")
                item['title']= item['title'].replace(",", "*")
                item['url'] = item['url'].replace(",", "*")
                item['age'] = item['age'].replace(",", "*")
                item['seed'] = item['seed'].replace(",", "*")
                item['size'] = item['size'].replace(",", "*")


		wLog = c.join([item['website'], item['category'], item['title'], item['url'], item['age'], item['seed'], item['sizeType'], item['torrent'] , item['leech'], item['size']])
                #self.f.write(s[:-1].encode("UTF-8") + "\n")
		self.f.write(wLog.encode("UTF-8") + "\n")
                self.f.flush()
        
        path = item['torrent']
        #print "path = ", path
        #subprocess.call(['./curl_torrent.sh', path])

        #subprocess.call(['./curl_torrent.sh', path])
        
        ## buffer read
        #buf = cStringIO.StringIO()
        #c = pycurl.Curl()
        #path = str(path)
        #agent="'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4)'"
        #print "type of c.URL", type(c.URL)
        #print "type of path", type(path)
        #print "agent", agent
        #c.setopt(c.URL, path)
        #c.setopt(c.FOLLOWLOCATION, 1)
        #c.setopt(c.TRANSFER_ENCODING, 1)
        #c.setopt(c.USERAGENT, agent)
        #c.setopt(c.WRITEFUNCTION, buf.write)
        #c.perform()
        #b = bencode.bdecode(buf.getvalue())
        #print "decoded bencode=", decoded
        #print str(buf.getvalue())
        #buf.close()


    def exists(self, title):
	pass
 #       for line in open('torrents/torrents.log', 'r'):
 #           if title in line:
 #               return True
 #       return False


