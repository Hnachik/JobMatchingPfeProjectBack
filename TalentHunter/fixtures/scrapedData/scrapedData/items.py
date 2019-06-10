# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapedDataItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    company_description = scrapy.Field()
    job_type = scrapy.Field()
    fields = scrapy.Field()
    location = scrapy.Field()
    publication_date = scrapy.Field()
    expiration_date = scrapy.Field()
    job_description = scrapy.Field()
    job_requirements = scrapy.Field()
    company_logo = scrapy.Field()
    post_url = scrapy.Field()
