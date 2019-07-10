from setuptools import setup
setup(
  name = 'news_extract',
  packages = ['news_extract'], # this must be the same as the name above
  version = '1.0.2',
  description = 'news_extract',
  author = 'Deen Freelon',
  author_email = 'dfreelon@gmail.com',
  url = 'https://github.com/dfreelon/news_extract/', # use the URL to the github repo
  download_url = 'https://github.com/dfreelon/news_extract/', 
  install_requires = ['pandas'],
  keywords = ['information retrieval', 'nexisuni', 'factiva', 'deduplication'], # arbitrary keywords
  classifiers = [],
  include_package_data=True
)