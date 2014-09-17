from urlparse import urlparse, urlunsplit
import bencode
import binascii, urllib, socket, random, struct
import sys


def scrape_tracker( tracker_urls, info_hash):
    """ 
        tracker_url: string of the announce url of the tracker
        info_hash: info hash to query the tracker for (this is related to specific file)

        This function return a dictionary of the response from the tracker for that hash_info
    """
    result_IPs = set([])
    for t in tracker_urls:
        try:
            tracker = t.lower() #lower case
            url_parse = urlparse(tracker)
     
            if url_parse.scheme == "udp": #check scheme of tracker - protocol
                result_IPs = set(result_IPs.union(set(scrape_tracker_udp(url_parse, info_hash))))
            elif url_parse.scheme == "https" or url_parse.scheme == "http":
                if "announce" not in tracker:
                    raise RuntimeError("%s doesn't support scrape" % tracker)
       
            #url_parse = urlparse(tracker.replace("announce", "scrape"))
            #tracker.replace(tracker[tracker.rindex("/")+1:], "scrape")
            #url_parse = urlparse(tracker)
	        result_IPs = set(result_IPs.union(set(http_announce(url_parse, info_hash))))
            else:
                raise RuntimeError("Unknown tracker scheme: %s" % url_parse.scheme)

        except IOError as e:
            #print "I/O error({0}): {1}".format(e.errno, e.strerror)
            print "error in scraping tracker", e
            continue
        except Exception, ex:
            #print "Error: ", sys.exc_info()[0]
            print "Error: Exception ", ex
    #print "length of set=", len(result_IPs) 
    return result_IPs             




def scrape_tracker_udp(parsed_tracker, info_hash):
     """
         parsed_tracker: parsed tracker url
         info hash: the info hash provided to query tracker for
     """
     print "Scraping UDP %s for hash %s " % (parsed_tracker.geturl(), info_hash)

     xaction_id = "\x00\x00\x04\x12\x27\x10\x19\x70"
     connection_id = "\x00\x00\x04\x17\x27\x10\x19\x80"
     _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     _socket.settimeout(12)
     conn = (socket.gethostbyname(parsed_tracker.hostname), parsed_tracker.port)

     #Get connection id
     request, xaction_id = udp_create_connection_request()
     _socket.sendto(request, conn)
     buf = _socket.recvfrom(4096)[0]
     connection_id = udp_parse_connection_response(buf, xaction_id)

     ##Announce
     num_peers = 200
     request, xaction_id = udp_create_announce_request(connection_id, info_hash, num_peers)
     _socket.sendto(request, conn)
     buf = _socket.recvfrom(4096)[0]
     return udp_parse_announce_response(buf, xaction_id, info_hash, num_peers)
    


     #Scrape 
     
     #request, xaction_id = udp_create_scrape_request(connection_id, info_hash)
     #_socket.sendto(request, conn)
     #buf = _socket.recvfrom(2048)[0]
     #return udp_parse_scrape_response(buf, xaction_id, info_hash)



def http_scrape(parsed_tracker, info_hash):
    print "Scraping HTTP: %s for hash %s" % (parsed_tracker.geturl(), info_hash)
   
    qs = [] #querystring
    
    url_param = binascii.a2b_hex(info_hash)
    qs.append(("info_hash", url_param))

    #print "url_param", url_param
    
    qs = urllib.urlencode(qs)    
    url = urlunsplit((parsed_tracker.scheme, parsed_tracker.netloc, parsed_tracker.path, qs, parsed_tracker.fragment))
    #print "url", url
    
    try:
        handle = urllib.urlopen(url)

        if handle.getcode() is not 200:
            raise RuntimeError("%s status code returned. handle error" % handle.getcode())

        _read = handle.read()   
        #print "_read result=", _read
        decoded = bencode.bdecode(_read)
        #print "decoded handle=", decoded
    

        result = {}
        for h, stats in decoded['files'].iteritems():
            d_hash = binascii.b2a_hex(h)
            s = stats["downloaded"]
            p = stats["incomplete"]
            c = stats["complete"]
            result[h] =  {"seeds" :s, "peers": p, "complete": c}

        return result
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)


def http_announce(parsed_tracker, info_hash):
    #print "Scraping HTTP: %s for hash %s" % (parsed_tracker.geturl(), info_hash)
   
    qs = [] #querystring
    
    ## query string params
    peer_id = get_random_byte_string(20)       
    downloaded = 0
    left = 0
    uploaded = 0
    event = 1 # 1 for start
    ip = 0 # defualt to use client IP
    numwant = 2 ## we want 200 IP addresses
     
     
    
    url_param = binascii.a2b_hex(info_hash)
    qs.append(("info_hash", url_param))
    qs.append(("peer_id", peer_id))
    qs.append(("left", left))
    qs.append(("uploaded", uploaded))
    qs.append(("event", event))
    qs.append(("ip", ip))
    qs.append(("num_want", numwant))

    #print "url_param", url_param
   
    qs = urllib.urlencode(qs)    
    url = urlunsplit((parsed_tracker.scheme, parsed_tracker.netloc, parsed_tracker.path, qs, parsed_tracker.fragment))
    #print "url", url
    
    
    handle = urllib.urlopen(url)

    if handle.getcode() is not 200:
        raise RuntimeError("%s status code returned. handle error" % handle.getcode())

    
    _read = handle.read()   
    #print "_read result=", _read
    decoded = bencode.bdecode(_read)
    #print "decoded handle=", decoded    
    decoded_hex = binascii.b2a_hex(decoded['peers'])    
    index = 0
    result_list = []
    while index < len(decoded_hex):
        ip = int(decoded_hex[index: index + 8], 16)
        index += 8
        port = int(decoded_hex[index: index + 4], 16)
        index += 4
        result_list.append( (to_string(ip), ip, port) )
          
    #print "result from http", result_list
    return result_list
    
    



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



def udp_create_announce_request(connection_id, info_hash, num_peers):
    """ connection_id: from connection req/resp
    info_hash: from bencoded torrent file
    num_peers: number of peers/IPs to send to client"""

    action = 0x1 ## announce action is 1
    xaction_id = udp_get_transaction_id() ##random xaction id
    buf = struct.pack("!q", connection_id) #first 8 bytes is connection id
    buf += struct.pack("!i", action) # next 4 bytes is action
    buf += struct.pack("!i", xaction_id) # next 4 bytes is xaction id
    
    
    hex_rep = binascii.a2b_hex(info_hash)
    buf += struct.pack("!20s", hex_rep) #info hash

    peer_id = get_random_byte_string(20)
   # print "peer id generated = ", peer_id
    buf += struct.pack("!20s", peer_id)

    downloaded = 0L
    buf += struct.pack("!q", downloaded)

    left = 0L
    buf += struct.pack("!q", left);  
          
    uploaded = 0L
    buf += struct.pack("!q", uploaded);  
    
    event = 1  # 1: start event, might need to change to None upon next request
    buf += struct.pack("!i", event)
   
    ip = 0
    buf += struct.pack("!i", ip)

    key = get_random_int() ## random key
   # print "random key = ", key
    buf += struct.pack("!i", key)

    num_want = num_peers ## for test purposes just get one IP
    buf += struct.pack("!i", num_want)

    port = 6882
    buf += struct.pack("!H", port)

    return (buf, xaction_id)



def udp_parse_announce_response(buf, sent_xaction_id, info_hash, num_peers):
    if len(buf) < 16:
        raise RuntimeError("Wrong response length while scraping %s" % len(buf))
    
    action = struct.unpack_from("!i", buf)[0] ## get action (first 4 bytes)
    res_xaction_id = struct.unpack_from("!i", buf, 4)[0] ## get transaction id
    
    
    if res_xaction_id != sent_xaction_id:
        raise RuntimeError("Xaction ID does not match response from scrape!! expected %s but received %s"
                        % (sent_xaction_id, res_xaction_id))

    if action == 0x1:

        try:
            result = {} # result map
            ips = []
            interval = struct.unpack_from( "!i", buf, 8)[0] ## interval : num of seconds to wait before reannouncing yourself
            leechers = struct.unpack_from("!i", buf, 12)[0] ## leechers: number of peers in sward that didn't finish downloading
            seeders = struct.unpack_from("!i", buf, 16)[0] ## seeders: number of peers that have finished downloading and are seeding
            peer_IPs = [] ## store list of (IP, TCP port) pairs per peer/client 
        
            result = { "interval": interval, "leechers": leechers, "seeders": seeders, "peers": peer_IPs}
        
            offset = 20 #start reading IPv4 addresses at this offset
            for i in xrange(num_peers):
                ip = struct.unpack_from("!I", buf, offset)[0] ## get ip of peer
                port = struct.unpack_from("!H", buf, offset+4)[0] ## get port they listen at 
                offset += 6
                result["peers"].append( (to_string(ip), ip, port) )
                       
        except:
            pass      
        #print "num of ips is = ", len(result['peers'])
        ips = result["peers"]
        #return result
        return ips

    elif action == 0x3:
        #error occurred , get the error string from byte 8
        err = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error while scraping tracker: %s" %err)

    else:
        raise RuntimeError("Unexpected action num " + action + " action should be 1 for announce action") 

def udp_create_scrape_request(connection_id, info_hash):
    action = 0x2 #action 2 is scrape
    xaction_id = udp_get_transaction_id()
    buf = struct.pack("!q", connection_id) #first 8 bytes is connection id
    buf += struct.pack("!i", action) #next 4 bytes is action
    buf += struct.pack("!i", xaction_id) # 4 bytes of transaction id

    hex_rep = binascii.a2b_hex(info_hash)
    buf += struct.pack("!20s", hex_rep)
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
	
        #print "buffer size =", len(buf)       
         
        offset += 4
        result = {"seeds" : seeds, "leeches": leeches, "complete": complete}
        
        return result

    elif action == 0x3: #error case 
        #error occurred , get the error string from byte 8
        err = struct.unpack_from("!s", buf, 8)
        raise RuntimError("Error while scraping tracker: %s" %err)



### definition of utility functions. Consider moving these to different python module

def udp_get_transaction_id():
    return int(random.randrange(0,255))

def get_random_int():
    return int(random.randrange(-(2**31), 2**31-1))

def get_random_byte_string(numBytes):
    """ get random byte string of numBytes bytes"""
    st = ''.join(chr(random.randint(0,255)) for i in range(numBytes))    
    return st

def to_string(ip):
    """ Convert 32-bit integer ip to dotted IPv4 address."""
    return ".".join(map(lambda n : str(ip >> n & 0xFF), [24, 16, 8, 0]))



if __name__ == "__main__":
    t_url = sys.argv[1]
    info_hash = sys.argv[2]
    scrape_tracker(t_url, info_hash)                
         





