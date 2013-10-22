import re
import sys

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from torrent.items import TorrentItem
from scrapy import log

class PiratebaySpider(CrawlSpider):
    name = 'piratebay'
    allowed_domains = ['thepiratebay.sx']
    categories = ['100', '101', '102', '103', '104', 
		  '200', '201', '202', '203', '204', 
		  '205', '206', '207', '208', '209', 
		  '300', '301', '302', '303', '304', 
		  '305', '306', '400', '401', '402', 
		  '403', '404', '405', '406', '407', 
		  '408', '600', '601', '602', '603', 
		  '604', '605']

    url_prefix = "http://thepiratebay.sx" #website.com/browse/cat/pagenum/order
    url_mid = '/browse/'
    url_suffix = '/3'
    pages_num = 29
    _page = 0
    cat_idx = 0

#    rules = (
#        Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
#    )

    def __init__(self, *args, **kwargs):
	super(PiratebaySpider, self).__init__(*args, **kwargs)
	self.start_urls = [self.url_prefix +
			   self.url_mid + 
			   self.categories[self.cat_idx] + '/'
			   + str(self._page) +
			   self.url_suffix]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
	entries = hxs.select('//tr')
	for entry in entries:
	        item = TorrentItem()
		item['title'] = entry.select('td[2]/div[1]/a[1]/text()').extract()
		item['url'] = entry.select('td[2]/div[1]/a[1]/@href').extract()
		item['torrent'] = entry.select('td[2]/a[starts-with(@title,"Download this torrent")]/@href').extract()
		size = entry.select('td[2]/font[1]/text()[2]').extract().split(",")[1].split("\xa0")
		item['size'] = size[0]
		item['sizeType'] = size[1]
		item['age'] = entry.select('td[2]/font[1]/text()[1]').extract()
		print item['age']
		item['seed'] = entry.select('td[3]/text()').extract()
		item['leech'] = entry.select('td[4]/text()').extract()
		yield item

        if (self._page < self.pages_num):
            self._page += 1
        else:
            #change category
            if self.cat_idx < len(self.categories) - 1:
		self.cat_idx += 1
                self._page = 0
            else:
                raise CloseSpider("done with piratebay site")

        yield Request( self.url_prefix +
                       self.url_mid +
                       self.categories[self.cat_idx] + '/'
                       + str(self._page) +
                       self.url_suffix, callback=self.parse)

