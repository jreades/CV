#######################
# We convert most structures to a list of 
# dictionaries so that we get a sort-order
# of the dicts (1 for each entry). This is
# used with the BibTeX entries and the CSV
# data.
#
# Credit to https://stackoverflow.com/a/73050/4041902
# for helping me to understand how to use the more 
# complex elements of the sorted function.
#######################
def sort_records(records:list, *args, reverse:bool=False) -> list:
    """
    Sorts a list of records (each one of which is a dict) using
    the fields provided in the args. You can optionally reverse
    the returned list setting the keyword arg reverse=True.

    What makes this function 'clever' is that the args themselves
    can provide alternate sort orders (in which case the reverse 
    argument is ignored). The following modifiers are accepted:
    - "-": reverse sort
    - "<", "<=": numeric or string less-than
    - ">", ">=": numeric or string greater-then
    For exact matches (equivalent to "==") do not add a modifier.

    Arguments:
    *args: any number of fields on which to sort (these must be keys in the record-level dicts)
    reverse: boolean, default False to get a reverse sort on simple sorts (without field-level modifiers)
    """
    # print(f"Sorting by {args}")
    if any([a.startswith('-') for a in args]) and any([not a.startswith('-') for a in args]):
        args = list(args)
        rv = rparse_to_dict(records, args.pop(0), args)
        #print("\nHave rv\n")
        return flatten(rv)
    elif all([a.startswith('-') for a in args]):
        revised_args = [a.replace('-','') for a in args]
        return sorted(records, key=lambda e: tuple([e[k] for k in revised_args]), reverse=True)
    else:
        return sorted(records, key=lambda e: tuple([e[k] for k in args]), reverse=reverse)

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