import scrapy
from scrapy.http import HtmlResponse
from Lesson_7.leroyparser.leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class LeroyruSpider(scrapy.Spider):
    name = 'leroyru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LeroyruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        links = response.xpath(
            "//a[contains(@slot, 'name')]/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.pars_good)
        next_page = response.xpath("//a[contains(@rel, 'next')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def pars_good(self, response: HtmlResponse):
        ItemLoader.default_output_processor = TakeFirst()
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_css('name', "h1::text")
        loader.add_xpath('price', "//meta[@itemprop='price']/@content")
        loader.add_xpath('article', "//span[@slot='article']/@content")
        loader.add_xpath('properties', "//h2[contains(text(), 'Характеристики')]/..//dl[@class='def-list']")
        loader.add_xpath('photos', "//img[contains(@alt, 'product')]/@src")
        loader.add_value('link', response.url)

        # для динамически добавляемых полей (чтобы добавлять их отдельными столбцами в csv вместо единого столбца со словарем)
        card_prop_dt = response.xpath("//dt[@class='def-list__term']/text()").extract()
        card_prop_dd = response.xpath("//dd[@class='def-list__definition']/text()").extract()
        card_prop_dd = [d.replace('\n', '').strip() for d in card_prop_dd]
        properties = dict(zip(card_prop_dt, card_prop_dd))
        for key, val in properties.items():
            loader.add_value(key, val)

        yield loader.load_item()
