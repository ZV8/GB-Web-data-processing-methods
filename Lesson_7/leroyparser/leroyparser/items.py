# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Identity
from lxml import html
from collections import defaultdict


def process_img_url(value):
    if value:
        value = value.replace('w_1200', 'w_2000').replace('h_1200', 'h_2000')
    return value


def process_props(props_block):
    properties = []
    if props_block:
        card_prop_dt = html.fromstring(props_block).xpath("//dt[@class='def-list__term']/text()")
        card_prop_dd = html.fromstring(props_block).xpath("//dd[@class='def-list__definition']/text()")
        card_prop_dd = [d.replace('\n', '').strip() for d in card_prop_dd]
        properties = dict(zip(card_prop_dt, card_prop_dd))
    return properties


class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(lambda x: float(x.replace(' ', ''))))
    article = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    properties = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(process_props))
    photos = scrapy.Field(output_processor=Identity(), input_processor=MapCompose(process_img_url))
    _id = scrapy.Field()
    fields = defaultdict(scrapy.Field)
