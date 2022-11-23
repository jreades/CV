import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase

parser = BibTexParser(common_strings=False)
parser.ignore_nonstandard_types = False
parser.homogenise_fields = False

def load_bib(path:str) -> BibDatabase:
  with open(path) as bibfile:
    bib_str = bibfile.read()
  return bibtexparser.loads(bib_str, parser)

controls = re.compile(r'^((?:<=?|>=?)*)\b', re.IGNORECASE)
def filter_bib(bib:BibDatabase, filters:dict={}, defaults:dict={}) -> list:
    rv = []
    for e in bib.entries:

        # Add the defaults to the entry
        for d in defaults.keys():
            if e.get(d,True):
                e[d] = defaults[d]
        
        # We need multiple conditions to hold
        include_ok = []

        if len(filters) == 0: # No filters
            include_ok.append(True)
        
        else: # It has filters...
            for k,v in filters.items(): 
                if e.get(k, False): # it has the key
                    #print("Key used!")
                    m = controls.match(v)
                    if m.end() == 0:
                        if e[k]==v: 
                            include_ok.append(True)
                        else:
                            include_ok.append(False)
                    else:
                        nums = re.search(r'^.*?(\d+)',e[k])
                        if len(nums.group(1)) > 0:
                            if eval(f"{nums.group(1)}{v}"):
                                include_ok.append(True)
                            else:
                                #print(f"{e[k]} didn't comply with {v}")
                                include_ok.append(False)
                        else:
                            print(f"Unable to parse digits from entry {e[k]} to test against {v}")
                            include_ok.append(False)
                else:
                    #print(f"{k} not found!")
                    include_ok.append(False)
        
        if all(item is True for item in include_ok):
            rv.append(e)
    return rv