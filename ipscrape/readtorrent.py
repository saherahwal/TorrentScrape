## This module is written to parse bencoded torrent files ####
import hashlib
import bencode
import sys


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
    return meta_info['announce-list']


