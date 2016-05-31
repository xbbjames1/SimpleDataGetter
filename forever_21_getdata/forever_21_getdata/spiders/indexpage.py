import scrapy


class InventoryGet(scrapy.Spider):
    name = "InventoryCrawler"
    start_urls = ["http://www.forever21.com/",]

    def parse(self,response):
        print response.xpath('//li[starts-with(@id, "g_")]/span[1]').extract()
