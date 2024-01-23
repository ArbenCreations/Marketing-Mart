import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
class TridonSpider(scrapy.Spider):
    name = 'tridon'
    base_url = 'https://www.tridon.com.au'
    start_urls = [f'{base_url}/products/']
    def parse(self, response):
        # Extracting brands
        brand_links = response.xpath('//div[@class="card"]//a/@href').extract()
        print(response.urljoin(brand_links[0]))
        for brand_link in brand_links:
            if 'products/HIT' in brand_link or 'products/Rennsteig' in brand_link or 'products/Toledo' in brand_link or 'products/Toledo' in brand_link:
                yield scrapy.Request(url=response.urljoin(brand_link), callback=self.parse_brand)
    def parse_brand(self, response):
        # Extracting categories
        category_links = response.xpath('//div[@class="card text-center"]//a/@href').extract()
        print(response.urljoin(category_links[0]))
        for category_link in category_links:
            yield scrapy.Request(url=response.urljoin(category_link), callback=self.parse_category)
    def parse_category(self, response):
        # Checking if there are subcategories
        subcategory_links = response.xpath('//div[@class="card text-center"]//a/@href').extract()
        if subcategory_links:
            print(response.urljoin(subcategory_links[0]))
            for subcategory_link in subcategory_links:
                yield scrapy.Request(url=response.urljoin(subcategory_link), callback=self.parse_category)
        elif response.xpath('//div[@class="col text-center col-thumb"]//a/@href').extract():
            subcategory_links = response.xpath('//div[@class="col text-center col-thumb"]//a/@href').extract()
            if subcategory_links:
                print(response.urljoin(subcategory_links[0]))
                for subcategory_link in subcategory_links:
                    yield scrapy.Request(url=response.urljoin(subcategory_link), callback=self.parse_category)
        else:
            # Extracting product links
            product_links = response.xpath('//tr[@class="row1"]//a[1]/@href').extract()
            print("kwmkdf",response.urljoin(product_links[0]))
            for product_link in product_links:
                yield scrapy.Request(url=response.urljoin(product_link), callback=self.parse_product)
            # Extracting pagination links
            pagination_links = response.xpath('//ul[@class="pagination right"]//li/a/@href').extract()
            if pagination_links:
                for pagination_link in pagination_links:
                    yield scrapy.Request(url=response.urljoin(pagination_link), callback=self.parse_category)
    def parse_product(self, response):
        # Extracting product details here, adjust as needed
        product_name = response.xpath('//h3[@class="prodTitle"]/text()').get().strip()
        print(product_name)
        images_links = response.xpath('//div[@id="prodImgCol"]//img/@src').extract()
        formatted_images_links = ';'.join(urljoin(self.base_url, link) for link in images_links)
        # Extracting product description
        product_description = response.xpath('//ul[@class="prodFeatures disc"]//li').extract()
        # Extracting attributes
        attributes = response.xpath('//table[@id="cph_ucPart_tblAttributes"]//tr').extract()
        # Extracting item contents
        item_contents = response.xpath('//table[@id="cph_ucPart_gvContents"]//tr').extract()
        yield {
            'product_name': product_name,
            'product_url': urljoin(self.base_url, response.url),
            'images_links': formatted_images_links,
            'product_description': product_description,
            'product attributes': attributes,
            'item_contents': item_contents,
        }
# Create a CrawlerProcess
process = CrawlerProcess(settings={
        'FEEDS': {
            f'tridon_brands.csv': {
                'format': 'csv',
                 'encoding': 'utf-8-sig',
            }
        },
        #'FEED_EXPORT_ENCODING': 'utf-8',
        # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        "FEED_EXPORT_ENDCODING": 'utf-8-sig'
    })
# Attach the spider to the process
process.crawl(TridonSpider)
# Start the crawling process
process.start()