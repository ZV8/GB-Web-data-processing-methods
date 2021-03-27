import scrapy
from scrapy.http import HtmlResponse
from Lesson_6.jobparser.items import JobparserItem


class SjobruSpider(scrapy.Spider):
    name = 'sjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&noGeo=1']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//a[contains(@href, 'vakansii')]/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.vacancy_pars)
        next_page = response.xpath("//a[contains(@rel, 'next')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_pars(self, response: HtmlResponse):
        vacancy_name = response.xpath("//h1//text()").extract_first()
        vacancy_salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, site=self.allowed_domains[0], link=response.url)
