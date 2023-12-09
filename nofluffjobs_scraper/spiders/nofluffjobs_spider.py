import scrapy
import re
from datetime import datetime, timedelta
from ..items import NofluffjobsItem


# Usage: scrapy crawl nofluffjobs_spider -0 filename.json
# Change MAX_PAGES for maximum scrapped pages

class NofluffjobsSpiderSpider(scrapy.Spider):
    name = "nofluffjobs_spider"
    allowed_domains = ["nofluffjobs.com"]
    base_url = "https://nofluffjobs.com/?page="
    sort_criteria = "criteria=salary%3Cpln500000m&sort=newest"
    start_urls = [f"{base_url}1&{sort_criteria}"]

    def parse(self, response):
        lists = response.xpath('//*[@data-cy="nfjPostingsList"]')

        for list in lists:
            for link in list.css('a::attr(href)').getall():
                if '/job' in link:
                    next_page = "https://nofluffjobs.com" + link
                    yield response.follow(next_page, callback=self.parse_details)

        current_page = int(response.url.split('=')[1].split('&')[0])

        MAX_PAGES = 50

        print('currentPage', current_page)
        if current_page < MAX_PAGES:
            # Build URL for the next page
            next_page_url = f"{self.base_url}{current_page + 1}&{self.sort_criteria}"

            # Make a request to the next page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_details(self, response):
        url = response.url
        details = response.css('article')

        creation_date = details.css('.posting-time-row::text').get()
        date_types = ['today', 'day', 'week', 'month']
        if any(el in creation_date for el in date_types):
            new_date = datetime.now()
            if 'today' in creation_date:
                new_date = datetime.now()
            else:
                counter = int(re.findall(r'\d+', creation_date)[0])
                if 'day' in creation_date:
                    new_date = datetime.now() - timedelta(days=counter)
                elif 'week' in creation_date:
                    new_date = datetime.now() - timedelta(weeks=counter)
                elif 'month' in creation_date:
                    new_date = datetime.now() - timedelta(days=30 * counter)
            creation_date = new_date.strftime('%Y-%m-%d')

        # salaries
        salary_ranges = details.css('.salary h4::text').getall()
        employment_types = details.css('.salary div span::text').getall()
        combined_salaries = []  # salary_min, salary_max, employment_type

        for salary_range, employment_type in zip(salary_ranges, employment_types):
            cleaned_salary_range = re.sub(r'[a-zA-Z\s]+', '', salary_range)
            cleaned_salary_range = cleaned_salary_range.replace('–', '-')

            # Check if the cleaned salary range is empty
            if not cleaned_salary_range:
                continue
            elif '-' in cleaned_salary_range:
                salary_min, salary_max = map(int, cleaned_salary_range.split('-'))
            else:
                salary_min = 0
                salary_max = int(cleaned_salary_range)

            combined_salaries.append({
                'salary_min': salary_min,
                'salary_max': salary_max,
                'employment_type': employment_type,
            })

        # image
        img = details.css('#postingLogoCompanyUrl img::attr(src)').get()

        # position_name
        position_name = details.css('.posting-details-description h1::text').get()

        # position_seniority
        position_seniority = details.css('#posting-seniority span::text').get()

        # skills
        skills_original = details.css('#posting-requirements span::text').getall()
        skills = [item.strip().replace('\n', '') for item in skills_original]

        # requirements_description
        requirements_description_original = details.css('section[data-cy-section="JobOffer_Requirements"]')
        requirements_description_title = requirements_description_original.css('h2::text').get()
        requirements_li_tags = requirements_description_original.css('li::text').getall()  # List text items
        requirements_p_tags = requirements_description_original.css('p strong::text').getall()  # Bold text
        requirements_description = requirements_li_tags + requirements_p_tags

        # offer_description
        offer_description = details.css('#posting-description')
        offer_title = offer_description.css('h2::text')
        offer_li_tags = offer_description.css('li::text').getall()
        offer_p_tags = offer_description.css('p::text').getall()
        offer_description = offer_li_tags + offer_p_tags

        # responsibilities
        responsibilities = details.css('#posting-tasks li::text').getall()

        # job_details
        job_details = details.css('#posting-specs li::text').getall()

        # methodology
        methodology = details.css('#posting-environment')
        methodology_strong = methodology.css('strong::text').getall()
        methodology_span = methodology.css('span::text').getall()
        methodology = methodology_strong + methodology_span

        # benefits
        benefits = details.css('#posting-benefits span::text').getall()

        company = details.css('#posting-company')

        # company_name
        company_name = company.css('a::text').get()

        # company_details
        company_details_titles = company.css('p span::text').getall()
        company_details = company.css('p::text').getall()

        combined_details = []

        for title, detail in zip(company_details_titles, company_details):
            combined_details.append(f"{title}{detail}")

        # company_description
        company_description_strong = company.css('article div strong::text').getall()
        company_description_text = company.css('article div::text').getall()
        company_description = company_description_strong + company_description_text

        job_item = NofluffjobsItem()

        job_item['creation_date'] = creation_date
        job_item['url'] = url,
        job_item['salaries'] = combined_salaries,
        job_item['image'] = img,
        job_item['position_name'] = position_name,
        job_item['position_seniority'] = position_seniority,
        job_item['skills'] = skills,
        job_item['requirements_description'] = requirements_description,
        job_item['offer_description'] = offer_description,
        job_item['responsibilities'] = responsibilities,
        job_item['job_details'] = job_details,
        job_item['methodology'] = methodology,
        job_item['benefits'] = benefits,
        job_item['company_name'] = company_name,
        job_item['company_details'] = combined_details,
        job_item['company_description'] = company_description

        yield job_item
