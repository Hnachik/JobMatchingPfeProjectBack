import scrapy
from ..items import ScrapedDataItem


class ScrapedDataSpider(scrapy.Spider):
    name = 'scrapdata'
    page_number = 2
    start_urls = [
        'https://www.tanitjobs.com/jobs/?searchId=1559550706.3656&action=search&page=1'
    ]

    def parse(self, response):
        urls = response.css('a.link::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_item, meta={'url': url})

        next_page = 'https://www.tanitjobs.com/jobs/?searchId=1559550706.3656&action=search&page=' + \
                    str(ScrapedDataSpider.page_number)
        if ScrapedDataSpider.page_number < 1:
            ScrapedDataSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):
        
        item = ScrapedDataItem()
        fields = []
        post_url = response.meta['url']
        company_description = response.css('.profile__info__description p::text').extract_first()
        job_title = response.css('.details-header__title::text').extract_first().strip()
        company_name = response.css('.listing-item__info--item-company::text').extract_first().strip()
        location = response.css('.listing-item__info--item-location::text').extract_first().strip()
        company_logo = response.css('.profile__img-company::attr(src)').extract_first()
        publication_date = response.css('.listing-item__info--item-date::text').extract_first().strip()
        expiration_date = response.css('.content-text:nth-child(6)::text').extract_first()
        job_type = response.css('.job-type__value::text').extract_first()

        job_description = ''.join(response.css('.details-body__content:nth-child(2) *::text').extract())
        job_requirements = ''.join(response.css('.details-body__content:nth-child(4) *::text').extract())

        for value in response.css('.job-type__value::text').extract():
            fields.append(value.strip())
        fields.remove(fields[0])

        item['job_title'] = job_title
        item['company_name'] = company_name
        item['job_type'] = job_type
        item['fields'] = fields
        item['location'] = location
        item['publication_date'] = publication_date
        item['expiration_date'] = expiration_date
        item['job_description'] = job_description
        item['job_requirements'] = job_requirements
        item['company_logo'] = company_logo
        item['company_description'] = company_description
        item['post_url'] = post_url

        yield item