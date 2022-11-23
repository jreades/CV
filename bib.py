import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase

parser = BibTexParser(common_strings=False)
parser.ignore_nonstandard_types = False
parser.homogenise_fields = False

def load_bib(path:str) -> BibDatabase:
  #try:
  with open(path) as bibfile:
    bib_str = bibfile.read()
  return bibtexparser.loads(bib_str, parser)

controls = re.compile(r'^((?:<=?|>=?)*)\b', re.IGNORECASE)
def filter_bib(bib:BibDatabase, filters:dict={}, defaults:dict={}) -> list:
    rv = []
    for e in bib.entries:
        #print(e['title'])
        include_ok = []
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
                
            elif defaults.get(k, False):
                #print("Default used!")
                m = controls.match(v)
                if m.end() == 0:
                    if defaults[k]==v: 
                        e[k]=defaults[k]
                        include_ok.append(True)
                    else:
                        include_ok.append(False)
                else:
                    nums = re.search(r'^.*?(\d+)',defaults[k])
                    if len(nums.group(1)) > 0:
                        if eval(f"{nums.group(1)}{v}"):
                            e[k]=defaults[k]
                            include_ok.append(True)
                        else:
                            #print(f"{e[k]} didn't comply with {v}")
                            include_ok.append(False)
                    else:
                        print(f"Unable to parse digits from default {defaults[k]} to test against {v}")
                        include_ok.append(False)
            else:
                #print(f"{k} not found!")
                include_ok.append(False)
        
        if all(item is True for item in include_ok):
            rv.append(e)
    return rv

# https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
def sort_bib(bib:list, *args, reverse:bool=False) -> list: #, **kwargs) -> list:
    #print(f"Sorting by {args}")
    if any([a.startswith('-') for a in args]) and any([not a.startswith('-') for a in args]):
        args = list(args)
        rv = rparse_to_dict(bib, args.pop(0), args)
        #print("\nHave rv\n")
        return flatten(rv)
    elif all([a.startswith('-') for a in args]):
        revised_args = [a.replace('-','') for a in args]
        return sorted(bib, key=lambda e: tuple([e[k] for k in revised_args]), reverse=True)
    else:
        return sorted(bib, key=lambda e: tuple([e[k] for k in args]), reverse=reverse)

def flatten(entries:dict) -> list:
    rv = []
    for k, v in entries.items():
        #print(f"Key: {k}")
        if isinstance(v,list):
            #print(" ...is list")
            rv.extend(v)
        elif isinstance(v,dict):
            #print(" ...is dict")
            rv.extend(flatten(v))
    #print(f"returning rv: {rv}")
    return rv

def rparse_to_dict(entries:list, field:str, *argv) -> dict:
    #print(f"\nSorting on: {field}")
    #print(f"List has {len(entries)} items")
    
    # Convert tuple to list
    #print(f"argv: {argv}")
    #print(f"len(argv): {len(argv)}")
    if len(argv)==0 or len(argv[0])==0:
        args = list()
    else:
        args = list(argv[0])

    # Empty data structure to return
    d = {}

    # Deal with reverse sorts
    reversed = False
    if field.startswith('-'):
        reversed = True
        field = field.replace('-','')

    # We are at the bottom level of the sort
    if len(args) == 0:
        #print(f"Returning sorted entries for key {field} (reversed is {reversed})")
        return sorted(entries, key=lambda d: d[field], reverse=reversed)
    else:
        #print(f"Still to parse: {args} for {len(entries)} items.")

        # For each entry in the list (input)
        # allocate it to a key in the dictionary
        # so that we can later sort by the keys
        for e in entries:
            v = e.get(field, 'None')
            if d.get(v,False):
                d[v].append(e)
            else:
                d[v] = list([e])

        for key in d.keys():
            if len(d[key]) == 0:
                # Shouldn't happen, but for completeness
                del(d[key])
            elif len(d[key]) == 1:
                # No need to sort it
                pass
            else:
                try:
                    #print(f"d[{key}] = rparse_to_dict(d[{key}] ({len(d[key])}), {args[0]}, {args[1:]})")
                    d[key] = rparse_to_dict(d[key], args[0], args[1:])
                    #print(f"Recursive d[{key}] set.")
                except IndexError:
                    print(f"Trapped index error: {args}")
                pass
        
        #tmp = {k : v for k, v in sorted(d.items(), reverse=reversed)}
        #print(tmp.keys())
        return {k : v for k, v in sorted(d.items(), reverse=reversed)}