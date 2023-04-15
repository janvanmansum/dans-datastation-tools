import os


def is_sub_path_of(child, parent):
    """
    Returns True if child is a descendant directory of parent, or if child is a file in a descendant directory
    of parent. Returns False otherwise. If one of the paths does not exist, returns False. The paths are first
    converted to absolute paths."""
    if not os.path.exists(child) or not os.path.exists(parent):
        return False
    absolute_parent = os.path.abspath(parent)
    absolute_dir = os.path.abspath(child)
    return absolute_dir.startswith(absolute_parent)
