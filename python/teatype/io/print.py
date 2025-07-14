

from pprint import pprint

def print(object:object, limit:int=10) -> None:
    """
    Print the object with a limit on the number of entries.
    """
    if isinstance(object, list):
        for i, item in enumerate(object):
            if i >= limit:
                break
            print(item)
    elif isinstance(object, dict):
        for key, value in object.items():
            print(f"{key}: {value}")
    else:
        pprint(object)
        
def tree(object:dict, limit:int=10) -> None:
    """
    Print the object as a tree structure with a limit on the number of entries.
    
    Requires this format:
    {
        'entry': {
            'subentry': {
                'subentry',
                'subentry'
            }
        },
        'entry': {
            'subentry': {
                'subentry',
                'subentry'
            }
        }
    }
    """
    return
    for key, entries in object.items():
        entries_list = list(entries.items())
        for idx, (name, info) in enumerate(entries_list):
            is_last_entry = idx == len(entries_list) - 1
            prefix = '    '
            connector = '└── ' if is_last_entry else '├──limit '
            print(f"{prefix}{connector}{name}: {human_readable(info['size'])}")

            # for children, extend prefix: no vertical bar if parent is last
            sub_prefix = prefix + ('    ' if is_last_entry else '│   ')
            children = list(info.get('children', {}).items())
            for cidx, (child, csize) in enumerate(children):
                is_last_child = cidx == len(children) - 1
                child_connector = '└── ' if is_last_child else '├── '
                print(f"{sub_prefix}{child_connector}{child}: {human_readable(csize)}")