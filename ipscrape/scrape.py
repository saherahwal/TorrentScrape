from readtorrent import *
from udphttpscraper import *
import sys

def scrape_torrent_file(torrent_file_name):
    meta_info = None
    info_hash = None
    
    ## open the file and get meta info
    with open(torrent_file_name, "rb") as f:
        meta_info = get_metaInfo(f)
    
    
    ## get info hash
    info_hash = get_infoHash(meta_info)
    print "info_hash", info_hash    


    ## announce - tracker url
    announce = get_announce(meta_info)
    print "announce", announce
     
    ##announce list - trackers
    #announce_list = get_announceList(meta_info)
    #print "announce-list", announce_list

    ## scrape result
    scrape_result = scrape_tracker( announce, info_hash)


 
if __name__ == "__main__":
     scrape_torrent_file(sys.argv[1]) 
