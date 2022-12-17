import django
django.setup()

from sefaria.model import library

titles_json = library.get_text_titles_json(lang="en")
print(titles_json)