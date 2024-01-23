import gzip
import shutil
from scrapy.spiders import SitemapSpider
from scrapy.spiders import Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
import scrapy
from rich import print
import json
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
class CrawlingSpider(scrapy.Spider):
    name="cigweld"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.cigweld.com.au/range/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }
    def start_requests(self):
        url = "https://www.cigweld.com.au/range/page/1/"
        yield scrapy.Request(url=url, callback=self.search_results, headers=self.headers)
    def search_results(self,response):
        total_pg=response.xpath('//a[@class="page-numbers"]//text()').getall()[-1]
        print(total_pg)
        for p in range(1,int(total_pg)+1):
            print(p)
            url = f"https://www.cigweld.com.au/range/page/{p}/"
        # payload = "{\r\n    \"take\": 15,\r\n    \"skip\": 0,\r\n    \"page\": 1,\r\n    \"pageSize\": 15,\r\n    \"sort\": [],\r\n    \"filter\": \"SearchKey\",\r\n    \"searchTerm\": \"Torches\",\r\n    \"searchSuggestions\": true,\r\n    \"productSuggestions\": true,\r\n    \"isPriorPurchase\": false,\r\n    \"isUserFavourites\": false,\r\n    \"includeHeadings\": false,\r\n    \"staticContentSearchMode\": \"Disabled\",\r\n    \"limitProductAndStaticContentResult\": false,\r\n    \"maxProductSearchResult\": 0,\r\n    \"maxStaticContentSearchResult\": 0,\r\n    \"returnTypeOrder\": null,\r\n    \n}"
        # for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parsed_links, headers=self.headers)
    def parsed_links(self,response):
        links=response.xpath('//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]//@href').getall()
        for l in links:
            yield scrapy.Request(url=l, callback=self.parse, headers=self.headers)
        # soup=BeautifulSoup(response.text,u'html.parser')
        # data=response.json()['data']
    def parse(self,response):
        try:
            product_name=response.xpath('//h1[@class="product_title entry-title"]//text()').get()
        except:
            product_name=''
        try:
            sku=response.xpath('//p[@class="sku"]//text()').get().split(":")[1].strip()
        except:
            sku=''
        try:
            product_name1=response.xpath('//div[@class="woocommerce-product-details__short-description"]//h3//text()').get()
            # print(product_name1)
        except:
            product_name1=''
        try:
            image_urls = [img.xpath('./@href').get() for img in response.xpath('//div[@class="woocommerce-product-gallery__image"]//a')]
        except:
            image_urls=''
        try:
            # Extract content within the "Product Information" tab
            product_information_content = response.xpath('//div[@id="tab-emo_product_information"]//div[@class="typography"]').getall()
            product_information_content = ' '.join(product_information_content).strip()
        except:
            product_information_content = ''
        try:
            # Extract product features from the "Product Information" tab
            product_features = response.xpath('//div[@id="tab-emo_product_information"]//ul[@class="product-features"]').getall()
            product_features = ' '.join(product_features).strip()
        except:
            product_features = ''
        try:
            # Extract specifications from the "Specifications" tab
            specifications = response.xpath('//div[@id="tab-emo_specifications"]//div[@class="typography"]/*[not(@class)]').getall()
            specifications = ' '.join(specifications).strip()
        except:
            specifications = ''
        try:
            # Extract download information from the "Downloads" tab
            downloads = response.xpath('//div[@id="tab-emo_downloads"]//ul[@class="product-downloads"]/li')
            download_info = ';'.join([
                f'{download.xpath(".//p//text()").get()} ({download.xpath(".//a/@href").get()})' for download in downloads
            ])
        except:
            download_info = ''
        yield {
            'Product Name1':product_name,
            'SKU':sku,
            'Product Name2':product_name1,
            'Image URLs':image_urls,
            'Product Information':product_information_content,
            'product_features': product_features,
            'Specifications': specifications,
            'Downloads': download_info,
            'URL': response.url,
            }
# Create a CrawlerProcess
process = CrawlerProcess(
    settings={
       'DOWNLOAD_TIMEOUT': 60,
        'DOWNLOAD_DELAY': 1,  # Increase the delay to 5 seconds
        'RETRY_TIMES': 3,
        'RETRY_TIMEOUT': 10,
        'FEEDS': {
            f'cigwelddata_new3.csv': {
                'format': 'csv',
            }
        },
        # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        # "FEED_EXPORT_ENDCODING": 'utf-8-sig'
    }
)
# Add your spider to the process
process.crawl(CrawlingSpider)
# Start the crawling process
process.start()