from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url

from torrent.items import TorrentItem

class KatSpider(BaseSpider):
	
    name = "kat"
    allowed_domains = [ "kat.ph", "kickass.to" ]    
    categories = ['books', 'tv', 'music', 'games', 'applications', 'movies', 'other']
 

    url_prefix = 'http://kat.ph'
    url_mid = '/usearch/category%3A'
    url_suffix = '/?field=time_add&sorder=desc'
    pages_num = 0
    _page = 1
    cat_idx = 0
    current_category = categories[cat_idx]
     

    
    def __init__(self, *args, **kwargs):
        super(KatSpider, self).__init__(*args, **kwargs)
	self.start_urls = ['http://kat.ph/usearch/category%3A'   
   		+ self.current_category + '/1'    
   		+ '/?field=time_add&sorder=desc'  	
	]	


    def parse(self, response):
        hxs = HtmlXPathSelector(response)
	entries = hxs.select('//tr[starts-with(@id,"torrent_category")]')  
        items = []  
        for entry in entries: 
            item = TorrentItem()  
	    item['website'] = self.url_prefix
	    item['category'] = self.current_category	
            item['title'] = entry.select('td[1]/div[2]/a[2]/text()').extract()           
            item['url'] = entry.select('td[1]/div[2]/a[2]/@href').extract()  
            item['torrent'] = entry.select('td[1]/div[1]/a[starts-with(@title,"Download torrent file")]/@href').extract()  
            item['size'] = entry.select('td[2]/text()[1]').extract()  
            item['sizeType'] = entry.select('td[2]/span/text()').extract()  
            item['age'] = entry.select('td[4]/text()').extract()
	    item['age'] = item['age'][0].encode("utf-8").replace("\xc2\xa0", "")
            item['seed'] = entry.select('td[5]/text()').extract()  
            item['leech'] = entry.select('td[6]/text()').extract()
	    print "emitting new item with title=", item['title']
	    #items.append(item)
	    yield item
	
	page_attrs = hxs.select('//div[starts-with(@class, "pages")]').select('a')
	final_page = page_attrs[-1].select('@href').extract()
	self.pages_num = int(page_attrs[-1].select('span/text()').extract()[0])
	#print "pages_num=", self.pages_num

	if (self._page < self.pages_num):
            self._page += 1
	else:
	    #change category
	    if self.cat_idx < len(self.categories) - 1:
		self._page = 0
	        self.current_category = self.categories[self.cat_idx + 1] 
	    else:
                raise CloseSpider("done with kat.ph site")

	yield Request( self.url_prefix +  self.url_mid + self.current_category + '/' + str(self._page)  + self.url_suffix, callback=self.parse)

	
	



   
         	 
