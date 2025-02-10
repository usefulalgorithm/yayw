import pathlib
from typing import List
import pytest
from yayw.splitter import Splitter


class TestSplitter:
    def _split_into_posts(self, filename: str, length: int) -> List[str]:
        path = pathlib.Path(__file__).parent.resolve() / "data" / filename
        with open(path) as f:
            text = f.read()
        splitter = Splitter(length)
        posts = splitter.split_into_posts(text)
        return posts
        
    
    @pytest.mark.parametrize(
        ["filename", "length"],
        (
            ["short_en.txt", 30],
            ["long_en.txt", 400],
            ["short_zh.txt", 30],
            ["long_zh.txt", 400],
        )
    )
    def test_split_text_basic(self, filename: str, length: int):
        posts = self._split_into_posts(filename, length)
        assert all(len(post) < length for post in posts)
        assert all(not post.startswith(" ") for post in posts)

    @pytest.mark.parametrize(
        ["filename", "length"],
        (
            ["short_en.txt", 300],
            ["short_zh.txt", 300],
        )
    )
    def test_no_split(self, filename: str, length: int):
        posts = self._split_into_posts(filename, length)
        assert all(not post.endswith("/)") for post in posts)
        