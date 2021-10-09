import csv
import io
import os
import re
import sys

import django
from django.core.files.uploadedfile import InMemoryUploadedFile


class ImportCSV:
    @staticmethod
    def init_django():
        djangoproject_home = "."
        sys.path.append(djangoproject_home)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'btpb2b.settings'
        django.setup()

    def after_snake_case(self, snake_case_string):
        return snake_case_string

    def to_snake_case(self, atributo):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', atributo)
        return self.after_snake_case(re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower())

    def __init__(self, file, process_item, item_template=None, post_process=None, get_file=False):
        if not item_template:
            item_template = {}
        if type(file) == InMemoryUploadedFile:
            csv_file = file.read().decode('utf-8')
            csv_file = io.StringIO(csv_file)
        elif type(file) == str:
            csv_file = open(file)
        else:
            csv_file = file

        if get_file:
            self.file = csv_file
            return

        reader = csv.DictReader(csv_file)

        for row in reader:
            item = item_template.copy()
            for column in row.keys():
                item[self.to_snake_case(column)] = row[column].strip() if row[column] else row[column]
            if process_item is not None:
                process_item(item)

        self.item_processed = reader.line_num - 1
        if post_process and callable(post_process):
            self.result_post = post_process()
