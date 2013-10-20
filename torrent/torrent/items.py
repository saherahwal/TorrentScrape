# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class TorrentItem(Item):
    title = Field()
    url = Field()
    size = Field()
    sizeType = Field()
    age = Field()
    seed = Field()
    leech = Field()
    torrent = Field()



