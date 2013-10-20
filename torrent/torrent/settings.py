# Scrapy settings for torrent project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'torrent'

SPIDER_MODULES = ['torrent.spiders']
NEWSPIDER_MODULE = 'torrent.spiders'

ITEM_PIPELINES = ['torrent.pipelines.TorrentPipeline']


# Log Settings


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'torrent (+http://www.yourdomain.com)'
