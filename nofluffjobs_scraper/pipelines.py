# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from itemadapter import ItemAdapter

class NofluffjobsScraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # Nested Fields
        nested_fields = ["salaries", "skills", "requirements_description", "offer_description", "responsibilities", "job_details", "methodology", "benefits", "company_details"]
        for field_name in nested_fields:
            value = adapter.get(field_name)
            adapter[field_name] = value[0] if value and len(value) > 0 else []

        # Single String Fields
        single_fields = ["url", "image", "position_name", "position_seniority", "company_name", "company_description", "requirements_description", "offer_description", "responsibilities"]
        for field_name in single_fields:
            value = adapter.get(field_name)
            if value and len(value) > 0 and value[0]:
                adapter[field_name] = value[0].strip()
            else:
                adapter[field_name] = ""

        # Strip Array Fields
        strip_array_fields = ["skills", "job_details", "methodology", "benefits", "company_details"]
        for field_name in strip_array_fields:
            values = adapter.get(field_name)
            adapter[field_name] = [detail.strip() for detail in values]

        # Extract Location
        company_details = adapter.get('company_details')
        if len(company_details) > 2:
            location = company_details[2]
            pattern = r'(?:Locations?|Main location):\s*([\w\s\d+]+)'
            match = re.search(pattern, location)
            if match:
                adapter['company_details'][2] = match.group(1).strip()

        # Clear NBSP
        clear_nbsp = ["requirements_description", "offer_description"]
        for field_name in clear_nbsp:
            value = adapter.get(field_name)
            adapter[field_name] = value.replace(u"\xa0", " ")
        if len(company_details) > 3:
            adapter['company_details'][3] = company_details[3].replace(u"\xa0", " ")

        # Salaries
        salaries = adapter.get('salaries')
        for salary in salaries:
            employment_type = salary.get('employment_type')

            if 'B2B' in employment_type:
                salary['employment_type'] = 'b2b'
            elif 'employment' in employment_type:
                salary['employment_type'] = 'work_contract'
            elif 'mandate' in employment_type:
                salary['employment_type'] = 'mandate-contract'
            else:
                salary['employment_type'] = 'any'

        return item
