# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import subprocess
import time
import urllib2
import os


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
	if len(item['title']) > 0:
		for i in item:
			if isinstance(item[i], list):
				item[i] = item[i][0]
			s += item[i].replace(",", "*") + ","
	#f = open('torrents/torrents.log','a')
        	self.f.write(s[:-1] + "\n")
		self.f.flush()
        #f.close()
        path = item['torrent']
        print "path = ", path
        subprocess.call(['./curl_torrent.sh', path])


    def exists(self, title):
	pass
 #       for line in open('torrents/torrents.log', 'r'):
 #           if title in line:
 #               return True
 #       return False


