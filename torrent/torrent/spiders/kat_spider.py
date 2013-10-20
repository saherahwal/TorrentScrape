from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url

from torrent.items import TorrentItem

class KatSpider(BaseSpider):
	
    name = "kat"

    allowed_domains = [ "kat.ph" ]

    def __init__(self, *args, **kwargs):
        super(KatSpider, self).__init__(*args, **kwargs)
        self.keywords = kwargs['keywords'].split(',')
        self.category = kwargs['category']
	self.start_urls = ['http://kat.ph/usearch/category%3A'   
   		+ self.category   
   		+ '/?field=time_add&sorder=desc'  	
	]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
	entries = hxs.select('//tr[starts-with(@id,"torrent_category")]')  
        items = []  
        for entry in entries: 
            print "entry now = ", entry
	    item = TorrentItem()  
            item['title'] = entry.select('td[1]/div[2]/a[2]/text()').extract()           
            for s in self.keywords:		
		if s.lower() in item['title'][0].lower():
		     print "found keyword", s.lower()
		     item['url'] = entry.select('td[1]/div[2]/a[2]/@href').extract()  
                     item['torrent'] = entry.select('td[1]/div[1]/a[starts-with(@title,"Download torrent file")]/@href').extract()  
                     item['size'] = entry.select('td[2]/text()[1]').extract()  
                     item['sizeType'] = entry.select('td[2]/span/text()').extract()  
                     item['age'] = entry.select('td[4]/text()').extract()  
                     item['seed'] = entry.select('td[5]/text()').extract()  
                     item['leech'] = entry.select('td[6]/text()').extract()
		     items.append(item)     
        return items 	 
