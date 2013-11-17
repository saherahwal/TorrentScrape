from readtorrent import *
from udphttpscraper import *
import sys

def scrape_torrent_file(torrent_file_name):
    meta_info = None
    info_hash = None
    
    ## open the file and get meta info
    with open(torrent_file_name, "rb") as f:
        meta_info = get_metaInfo(f)
    
    
    ## print meta_info
    print "meta info", meta_info

    ## get info hash
    info_hash = get_infoHash(meta_info)
    print "info_hash", info_hash    


    ## announce - tracker url
    announce = get_announce(meta_info)
    print "announce", announce
     
    ##announce list - trackers
    announce_list = get_announceList(meta_info)
    print "announce-list", announce_list
    
    ##scrape announce and announce-list (bencoded)
    try_announce_list = [announce]
    if(announce_list):
        for _aList in announce_list:
            for _announce in _aList:
                 try_announce_list.append(_announce)     
    #            result_list.append( scrape_tracker(_announce, info_hash))
    
    #print result_list    
    
    scrape_result = scrape_tracker( try_announce_list, info_hash)
    print scrape_result
    return scrape_result

 
if __name__ == "__main__":
     scrape_torrent_file(sys.argv[1]) 
