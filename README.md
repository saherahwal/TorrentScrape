torrentScrape
=============

Scrape torrent files from websites.


To run spider do the following:
scrapy crawl [spider_name]

To generate new spider, you should be under torrent/ directory and run the following:
scrapy genspider [name url]


where <name> looks like the following: [name_spider]
then change name attribute in python file to exclude the spider part so you can 
run it as : scrapy crawl domain

 
