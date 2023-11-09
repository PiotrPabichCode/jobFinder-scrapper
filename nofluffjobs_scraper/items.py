# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NofluffjobsItem(scrapy.Item):
    creation_date = scrapy.Field()
    url = scrapy.Field()
    salaries = scrapy.Field()
    image = scrapy.Field()
    position_name = scrapy.Field()
    position_seniority = scrapy.Field()
    skills = scrapy.Field()
    requirements_description = scrapy.Field()
    offer_description = scrapy.Field()
    responsibilities = scrapy.Field()
    job_details = scrapy.Field()
    methodology = scrapy.Field()
    benefits = scrapy.Field()
    company_name = scrapy.Field()
    company_details = scrapy.Field()
    company_description = scrapy.Field()
