import os, re
import csv

def load_csv(path:str):
    if not os.path.exists(path):
        return None
    else:
        data = {}
        with open(path, 'r') as f:
            csv_reader = csv.DictReader(f)
            first_line = next(csv_reader)

            for k in first_line.keys():
                data[k] = [first_line[k]]

            for row in csv_reader:
                for k in row.keys():
                    data[k].append(row[k])
        return data

controls = re.compile(r'^((?:<=?|>=?)*)\b', re.IGNORECASE)
def filter_csv(data:dict, filters:dict={}, defaults:dict={}) -> list:
    #print(data.keys())
    #row_count = len(data[list(data.keys())[0]])

    hits = []

    if len(filters) == 0: # No filters
        if len(defaults) > 0: # Add default values
            for field, target in defaults.items():
                if defaults.get(field,False):
                    data[field] = [target] * len(data[list(data.keys())[0]])
        indices = list(range(0,len(data[list(data.keys())[0]])))
        hits.append(set(indices))
    else:
        for field, target in filters.items():
            #print(f"{field} -> {target}")

            if data.get(field,False):

                m = controls.match(target)

                if m.end()==0:
                    print(f"Simple match: {target}")
                    indices = [i for i, x in enumerate(data[field]) if x==target]
                    #print(indices)
                    hits.append(set(indices))
                else:
                    #print(f"Numeric match: {target}")
                    indices = []
                    for ix, val in enumerate(data[field]):
                        nums = re.search(r'^.*?(\d+)',val)
                        #print(f"nums: {nums.group(1)}")
                        if len(nums.group(1)) > 0:
                            if eval(f"{nums.group(1)}{target}"):
                                indices.append(ix)
                        else:
                            print(f"Unable to parse digits from entry {val} to test against {target}")
                    #print(indices)
                    if len(indices) > 0:
                        hits.append(set(indices))
            
            elif defaults.get(field,False):
                indices = list(range(0,len(data[list(data.keys())[0]])))
                data[field] = [target] * len(data[list(data.keys())[0]])
                #print(f"data[{field}] = {data[field]}")
                #print(indices)
                hits.append(set(indices))
            else:
                print(f"{field} doesn't exist in data structure ({', '.join(data.keys())})")
        
    #print(hits)
    selected = set.intersection(*hits)

    rv = []

    for ix in selected:
        d = {}
        for dk, dv in data.items():
            d[dk] = dv[ix]
        rv.append(d)

    return rv