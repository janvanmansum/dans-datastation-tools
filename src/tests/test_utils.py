import os

from datastation.common.utils import is_sub_path_of


class TestIsSubPathOf:
    def test_returns_true_for_child_dir(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        child = parent.mkdir('child')
        assert is_sub_path_of(child, parent)
        assert not is_sub_path_of(parent, child)

    def test_returns_true_for_child_file(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        child = parent.join('child')
        child.write('test')
        assert is_sub_path_of(child, parent)
        assert not is_sub_path_of(parent, child)

    def test_returns_true_for_child_file_in_subdir(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        subdir = parent.mkdir('subdir')
        child = subdir.join('child')
        child.write('test')
        assert is_sub_path_of(child, parent)
        assert not is_sub_path_of(parent, child)

    def test_returns_true_for_child_dir_in_subdir(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        subdir = parent.mkdir('subdir')
        child = subdir.mkdir('child')
        assert is_sub_path_of(child, parent)
        assert not is_sub_path_of(parent, child)

    def test_returns_false_for_non_child_dir(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        child = tmpdir.mkdir('child')
        assert not is_sub_path_of(child, parent)
        assert not is_sub_path_of(parent, child)

    def test_converts_child_to_absolute_path(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        parent.mkdir('child')
        os.chdir(parent)
        assert is_sub_path_of('child', os.path.abspath(parent))

    def test_converts_parent_to_absolute_path(self, tmpdir):
        parent = tmpdir.mkdir('parent')
        child = parent.mkdir('child')
        os.chdir(parent)
        assert is_sub_path_of(os.path.abspath(child), '.')