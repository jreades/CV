import os
from bib import load_bib, filter_bib, sort_bib

bib_db  = load_bib(os.path.join('assets','pubs.bib'))
my_pubs = filter_bib(bib_db, {'year':'<2017', 'priority':'<2'}, {'priority':'1'}) 

for p in sort_bib(my_pubs, 'priority', 'year', '-ENTRYTYPE', ):
  print(f"{p['title'][:25]}: {p['ENTRYTYPE']}, {p['priority']}, {p['year']}")

exit()