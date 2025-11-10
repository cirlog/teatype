from teatype.io.dict import render_tree

test_dict = {
    "a": {
        "b": {
            "c": 1,
            "d": 2
        },
        "e": 3
    },
    "f": 4
}

def test_render_tree():
    for line in render_tree(test_dict, indent_size=4):
        print(line)