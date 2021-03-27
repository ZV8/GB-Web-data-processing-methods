import scrapy
from scrapy.http import HtmlResponse
from Lesson_6.jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=Data+science']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[contains(@data-qa, 'vacancy-serp__vacancy-title')]/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.vacancy_pars)
        next_page = response.xpath("//a[contains(@class, 'HH-Pager-Controls-Next')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_pars(self, response: HtmlResponse):
        vacancy_name = response.xpath("//h1//text()").extract_first()
        vacancy_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, site=self.allowed_domains[0], link=response.url)
