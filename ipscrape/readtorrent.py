## This module is written to parse bencoded torrent files ####
import hashlib
import bencode
import sys
import subprocess
import urllib


def get_decoded_indexer_response(url, referer=None):
    """ return curl output download of torrent file """
    agent="'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4)'"
    proc = None
    timeout = "120" #seconds timeout for whole operation
    if referer:
        proc = subprocess.Popen([
"curl", "--globoff", "--compressed", "-A", agent, "-L", "--post302", "--referer", referer  , "--max-time", timeout, url], stdout= subprocess.PIPE)
    else:
        proc = subprocess.Popen([
"curl", "--globoff", "--compressed", "-A", agent, "-L", "--post302", "--max-time", timeout, url], stdout= subprocess.PIPE)
    out, err = proc.communicate()
    return out


def test_seedpeer_urllib(url):
    url_handle = urllib.urlopen(url)
    return url_handle.read()



def get_metaInfo(torrent_file):
    """ get the meta info of the torrent file, decodes the bencoding of .torrent"""
    meta_info = bencode.bdecode(torrent_file.read())
    return meta_info


def get_infoHash(meta_info):
    """ returns the hex digest of the info hash required to scrape a tracker """
    info_hash = meta_info['info']
    info_hash =  hashlib.sha1(bencode.bencode(info_hash)).hexdigest()
    return  info_hash


def get_announce(meta_info):
    return meta_info['announce']


def get_announceList(meta_info):
    if meta_info.has_key('announce-list'):
        return meta_info['announce-list']
    return None


if __name__ == "__main__":
    inp = sys.argv[1]
    #inp2 = sys.argv[2]
    u = get_decoded_indexer_response(inp)
    #v = test_seedpeer_urllib(inp) 
    print u
    print "decode ", bencode.bdecode(u)    
