import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tompkinsfinancial.items import Article
import requests
import json


class TompkinsfinancialSpider(scrapy.Spider):
    name = 'tompkinsfinancial'
    start_urls = ['https://tompkinsfinancial.q4ir.com/']

    def parse(self, response):

        json_response = json.loads(requests.get("https://tompkinsfinancial.q4ir.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1").text)
        articles = json_response["GetPressReleaseListResult"]
        for article in articles:
            link = response.urljoin(article['LinkToDetailPage'])
            date = article["PressReleaseDate"]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/span/text()').get() or response.xpath('//h2/span/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="module_container module_container--content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
