import scrapy
from forever_21_getdata import utiltools
from forever_21_getdata.items import Forever21GetdataItem
from forever_21_getdata.utiltools import validate_attr
MAIN_PAGE = "main_page"
PRODUCT = "product"
IMG = 'image'

class InventoryCrawler(scrapy.Spider):
    name = "InventoryCrawler"
    start_urls = ["http://www.forever21.com/", ]
    
    # concatenate generated paging parameter with inventory domain field url
    def url_maker(self, url_orgin, item_number, total_page):
        for p in range(total_page):
            sub_url = r'&pagesize=%d&page=%d' % (item_number, p+1)
            yield url_orgin+sub_url

    # default callback function ,used when Request has been created on start_url 
    def parse(self, response):
        res_tmp = response.xpath('//*[@id="g_women"]/span[@class="global_cat"]/a/@href')

        if len(res_tmp)!=1:
            raise Exception("Likely Changed")
            utiltool.send_mail("Potential Change of WebStructure, Inventroy Getter Error")

        for ivt in res_tmp:
            req_call = scrapy.Request(ivt.extract(), self.parse_number_get)
            req_call.meta["root_url"] = ivt.extract()
            yield req_call
    
    # get the total number of pages and scrape each page using p_inv_p func
    def parse_number_get(self, response):
        page_number = 0
        button_list = response.xpath('//span[contains(@class, "p_number")]/button/text()').extract()
        
        if len(button_list)>0:
            page_number = int(button_list[-1])
        else:
            raise Exception("Likely Changed")
            utiltools.send_mail("Potential Change o WebStructure, page_number Getter Error")

        page_number = page_number / 50
        url_g = self.url_maker(response.meta["root_url"], 60, page_number)

        for page_url in url_g:
            req = scrapy.Request(page_url, self.parse_inventory_page)
            yield req

    # process each inventory link
    def parse_inventory_page(self, response):
        # counter = 1
        product_entry = response.xpath('//div[@class="item_pic"]/a/@href')

        if len(product_entry)<1:
            raise Exception("Likely Changed")
            utiltools.send_mail("Potential Change of WebStructure, failed to extract product detail url")

        for item_index in product_entry:            
            req = scrapy.Request(item_index.extract(), self.parse_product_page)
            yield req

    # this method is to get the url from a js snippet     
    def strip_str(self, str):
        mid_str = str.split('(')[1].split(')')[0]
        re_str = mid_str.split(',')[1].strip('\'')
        return re_str


    # process each product page

    def parse_product_page(self, response):

        item_price = response.xpath('//*[@itemprop="price"]/text()').extract()[0]
        
        # size availibility to be done

        item_size = response.xpath('//ul[contains(@id, "ulProductSize")]/li/label/text()').extract()
        
        item_color = response.xpath('//li[contains(@id, "colorid_")]//img/@alt').extract()

        item_inter_img = response.xpath('//li[contains(@id, "liImageButton_")]/a/@href').extract()

        item_img = []

        for img_src in item_inter_img:
            img_file = "To be Downloaded"
            # img_file = utiltools.download_image(self.strip_str(img_src))
            item_img.append(img_file)
        try:
            testor = float(item_price[1::])
            assert (testor>=0)
            assert (item_size != None)
            assert (validate_attr(item_size,'size') and validate_attr(item_img,'image') and validate_attr (item_color,'color'))
        except AssertionError, e:
            print str(e)
            # utiltools.send_mail('Potential Change in WebStructure, invalidate item attribute has been found!')

        item = Forever21GetdataItem(size=item_size, color=item_color, img=item_img, price=item_price)

        yield item

