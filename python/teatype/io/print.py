from pprint import pprint

def print(obj:object, limit:int=10) -> None:
    """
    Print the object with a limit on the number of entries.
    """
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            if i >= limit:
                break
            print(item)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{key}: {value}")
    else:
        pprint(obj)