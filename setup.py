from distutils.core import setup

with open('README.md', 'r') as f:
    readme = f.read()

setup(name='MECraker',
      version='1.0',
      description='Data collection tools for the Missouri Ethics Commission.',
      long_description=readme,
      long_description_content_type='text/markdown',
      license="GNU AFFERO GPL 3.0",
      author='Jaz Hays',
      author_email='emersonjazhays@gmail.com',
      url="https://github.com/RadJaz/MECraker",
      packages=['mec', 'mec.scripts', 'mec.report', 'mec.scraper', 'mec.watcher', 'mec.report.templates'],
      package_data={'mec.report.templates': ['*.json']},
      install_requires= ["requests", "PyMuPDF", "PyYAML"]
     )
