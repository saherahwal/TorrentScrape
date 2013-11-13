from urlparse import urlparse, urlunsplit
import bencode
import binascii, urllib, socket, random, struct
import sys


def scrape_tracker( tracker_url, info_hash):
    """ 
        tracker_url: string of the announce url of the tracker
        info_hash: info hash to query the tracker for (this is related to specific file)

        This function return a dictionary of the response from the tracker for that hash_info
    """
    tracker = tracker_url.lower() #lower case
    url_parse = urlparse(tracker)
     
    if url_parse.scheme == "udp": #check scheme of tracker - protocol
        return scrape_tracker_udp(url_parse, info_hash)
    elif url_parse.scheme == "https" or url_parse.scheme == "http":
        if "announce" not in tracker:
            raise RuntimeError("%s doesn't support scrape" % tracker)
        url_parse = urlparse(tracker.replace("announce", "scrape"))
	return scrape_tracker_http(url_parse, info_hash)
    else:
        raise RuntimeError("Unknown tracker scheme: %s" % url_parse.scheme)



def scrape_tracker_udp(parsed_tracker, info_hash):
     """
         parsed_tracker: parsed tracker url
         info hash: the info hash provided to query tracker for
     """
     print "Scraping UDP %s for hash %s " % (parsed_tracker.geturl(), info_hash)

     xaction_id = "\x00\x00\x04\x12\x27\x10\x19\x70"
     connection_id = "\x00\x00\x04\x17\x27\x10\x19\x80"
     _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     _socket.settimeout(8)
     conn = (socket.gethostbyname(parsed_tracker.hostname), parsed_tracker.port)

     #Get connection id
     request, xaction_id = udp_create_connection_request()
     _socket.sendto(request, conn)
     buf = _socket.recvfrom(2048)[0]
     connection_id = udp_parse_connection_response(buf, xaction_id)

     #Scrape 
     request, xaction_id = udp_create_scrape_request(connection_id, info_hash)
     _socket.sendto(request, conn)
     buf = _socket.recvfrom(2048)[8]
     return udp_parse_scrape_response(buf, xaction_id, info_hash)



def scrape_tracker_http(parsed_tracker, info_hash):
    print "Scraping HTTP: %s for hash %s" % (parsed_tracker.geturl(), info_hash)
   
    qs = [] #querystring
    
    url_param = binascii.a2b_hex(info_hash)
    qs.append(("info_hash", url_param))

    print "url_param", url_param
    
    qs = urllib.urlencode(qs)    
    url = urlunsplit((parsed_tracker.scheme, parsed_tracker.netloc, parsed_tracker.path, qs, parsed_tracker.fragment))
    print "url", url
    handle = urllib.urlopen(url)

    if handle.getcode() is not 200:
        raise RuntimeError("%s status code returned. handle error" % handle.getcode())

   
    decoded = bencode.bdecode(handle.read())
    print "decoded tracker response", decoded
    
    result = {}
    for h, stats in decoded['files'].iteritems():
        d_hash = binascii.b2a_hex(h)
        s = stats["downloaded"]
        p = stats["incomplete"]
        c = stats["complete"]
        result[h] =  {"seeds" :s, "peers": p, "complete": c}

    return result



def udp_create_connection_request():
     connection_id = 0x41727101980 #default conn id
     action = 0x0 #( 0 means give me a new conn id)
     xaction_id = udp_get_transaction_id()
     buf = struct.pack("!q", connection_id)  # first 8 bytes is the connection id
     buf += struct.pack("!i", action) # next 4 bytes is action
     buf += struct.pack("!i", xaction_id) # next 4 bytes transaction id
     return (buf, xaction_id)


def udp_parse_connection_response(buf, sent_xaction_id):
    if len(buf) < 16:
         raise RuntimeError("Wrong response length getting connection id: %s" % len(buf))
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action

    res_xaction_id = struct.unpack_from("!i", buf, 4)[0]  #next 4 bytes is transaction id
    if res_xaction_id != sent_xaction_id:
        raise RuntimeError("Xaction ID doesnt match in connection response! Something is not right! Expected &s, got %s"
                                   %s (sent_xaction_id, res_xaction_id))
    if action == 0x0:
        connection_id = struct.unpack_from("!q", buf, 8)[0]  #unpack 8 bytes from byte 8, should be the connection id
        return connection_id
    elif action == 0x3:
        err = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error trying to get connection response: %s " % err) 



def udp_create_scrape_request(connection_id, info_hash):
    action = 0x2 #action 2 is scrape
    xaction_id = udp_get_transaction_id()
    buf = struct.pack("!q", connection_id) #first 8 bytes is connection id
    buf += struct.pack("!i", action) #next 4 bytes is action
    buf += struct.pack("!i", xaction_id) # 4 bytes of transaction id

    hex_rep = binascii.a2b_hex(info_hash)
    print "hex_repr", hex_rep
   
    buf += struct.pack("!20", hex_rep)
    return (buf, xaction_id)


def udp_parse_scrape_response( buf, sent_xaction_id, info_hash):
    if len(buf) < 16:
         raise RuntimeError("Wrong response length while scraping: %s" % len(buf))
    
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action
    res_xaction_id = struct.unpack_from("!i", buf, 4)[0]
    
    if res_xaction_id != sent_xaction_id:
        raise RuntimeError("Xaction ID does not match response from scrape!! expected %s but received %s"
                        % (sent_xaction_id, res_xaction_id))
    
    if action == 0x2:
        result = {}
        offset = 8 # next 4 bytes is xaction id, so we need to start at 8
        
        seeds = struct.unpack_from("!i", buf, offset)[0]
        offset += 4
        complete = struct.unpack_from("!i", buf, offset)[0]
        offset += 4
        leeches = struct.unpack_from("!i", buf, offset)[0]
	offset += 4

        result = {"seeds" : seeds, "leeches": leeches, "complete": complete}
        return result

    elif action == 0x3: #error case 
        #error occurred , get the error string from byte 8
        err = struct.unpack_from("!s", buf, 8)
        raise RuntimError("Error while scraping tracker: %s" %err)


def udp_get_transaction_id():
    return int(random.randrange(0,255))




if __name__ == "__main__":
    t_url = sys.argv[1]
    info_hash = sys.argv[2]
    scrape_tracker(t_url, info_hash)                
         





