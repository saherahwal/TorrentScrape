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
	    f = open('torrents/torrents.log', 'w')
	    f.close()	
   
	  

    def process_item(self, item, spider):
	print "processing item now", item['title']
        if not self.exists(item['title'][0]):
	    print "starting item download"
	    self.download_item(item)
            time.sleep(5) # pause to prevent 502 errors 
	return item

    
    def download_item(self, item):
        title = item['title'][0]
	print 'Downloading ' + title
	f = open('torrents/torrents.log','a')
        f.write(title+"\n")
        f.close()
        path = item['torrent'][0]
        subprocess.call(['./curl_torrent.sh', path])


    def exists(self, title):
        for line in open('torrents/torrents.log', 'r'):
            if title in line:
                return True
        return False


