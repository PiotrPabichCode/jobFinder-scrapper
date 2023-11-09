# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class NofluffjobsScraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # Stripping whitespaces
        field_names = adapter.field_names()
        without_stripping = ['position_description', 'requirements_description']
        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name not in without_stripping:

                if value is not None and len(value) > 0:
                    first_value = value[0]
                    if isinstance(item, str):
                        adapter[field_name] = first_value.strip()
                    elif isinstance(first_value, dict):
                        adapter[field_name] = {k: v.strip() for k, v in first_value.items()}

        # salaries
        salaries = adapter.get('salaries')[0]  # Extracting the list from the tuple
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
