from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from torrent.items import TorrentItem

class SeedpeerSpider(BaseSpider):
    name = "seedpeer"
    allowed_domains = ["seedpeer.me"]
    categories =  ['books', 'tv', 'music', 'movies', 'games', 'applications', 'other']
    start_urls = (
        'http://www.seedpeer.me/',
        )

    ver_vals = [1,2,3,4]

    current_verVal = ver_vals[1]
    pages_num = 0
    _page = 1
    url_prefix = 'http://www.seedpeer.me'


    def __init__(self, *args, **kwargs):
        super(SeedpeerSpider, self).__init__(*args, **kwargs)
        self.start_urls = [self.url_prefix + '/verified/'
                    + str(self.current_verVal) + '/' 
                    + str(self._page)+ '.html']
   

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        body  = hxs.select('//div[(@id= "body")]//table')[0] #we need first table
        tbl_rows = body.select('.//tr')
        tbl_rows = tbl_rows[1:] ## first element is header -remove it
        for tr in tbl_rows:
            item = TorrentItem()
            item['title'] = u''.join(tr.select('td[1]/a[1]/text()').extract()[0]).encode('utf-8').strip() 
            item['category'] = str(tr.select('td[1]/a/small/a/text()').extract()[0])
            item['age'] = str(tr.select('td[2]/text()').extract()[0])
            size, sizeType = str(tr.select('td[3]/text()').extract()[0]).split()
            item['size'] = size
            item['sizeType'] = sizeType
            item['seed'] = str(tr.select('td[4]/font/text()').extract()[0])
            item['leech'] = str(tr.select('td[5]/font/text()').extract()[0])
            item['website'] = self.url_prefix+'/'
            item['url'] = str(tr.select('td[1]/a/@href').extract()[0])
            request = Request(self.url_prefix + str(tr.select('td[1]/a/@href').extract()[0]), callback= self.parse_torrent)
            request.meta['item'] = item
            yield request
        
        pagesDiv = hxs.select('//div[(@id= "pagination")]') 
        
        pages = pagesDiv.select('.//a')
        print "pages = ",pages 
        pages= pages[1:] # remove first elt
        
        self.pages_num = int(pages[-1].select('text()').extract()[0])
         
        print "pages_num = ", self.pages_num

        if(self._page < self.pages_num):
            self._page += 1
        else:
            #done       
            raise CloseSpider("done with seedpeer.me site")

        yield Request( self.url_prefix + '/verified/' + \
                       str(self.current_verVal) + '/' +\
                       str(self._page) + '.html' , callback = self.parse)
           
    
    def parse_torrent(self, response):
        print "parsing detail"
        hxs = HtmlXPathSelector(response)
        torrent_download = str(hxs.select('//div[@class="downloadTorrent"]/a/@href').extract()[0])
        item = response.meta['item']
        item['torrent'] = self.url_prefix + torrent_download


        print "item is=", item['title'], item['category'], item['age'], item['size'], item['sizeType'], item['seed'], item['leech'], item['website'] ,item['url'], item['torrent']

        yield item

            
