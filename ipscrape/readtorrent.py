## This module is written to parse bencoded torrent files ####
import hashlib
import bencode
import sys
import subprocess



def get_decoded_indexer_response(url):
    """ return curl output download of torrent file """
    agent="'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4)'"
    proc = subprocess.Popen([
"curl", "--globoff", "--compressed", "-A", agent, "-L", "--post302", url], stdout= subprocess.PIPE)
    out, err = proc.communicate()
    return out

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

