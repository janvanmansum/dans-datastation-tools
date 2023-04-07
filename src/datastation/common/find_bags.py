import os


def find_bags(path, max_depth=2) -> list:
    """
    Find all bags in the given path, up to the given depth.
    """
    if is_bag(path):
        yield path
    else:
        for root, dirs, files in os.walk(path):
            if is_bag(root):
                yield root
            if root.count(os.sep) >= max_depth:
                del dirs[:]


def is_bag(path: str) -> bool:
    return os.path.exists(os.path.join(path, 'bagit.txt'))
