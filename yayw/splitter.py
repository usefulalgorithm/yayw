import re
from typing import List

import langdetect

_CHAR_SEGMENTED_LANGS = {
    "zh-cn",
    "zh-tw",
    "ja",
    "th",
}


class Splitter:
    def __init__(self, max_characters_per_post: int = 500) -> None:
        self._post_char_limit = max_characters_per_post
        self._page_number_char_count = 10

    @property
    def _content_char_limit(self) -> int:
        return self._post_char_limit - self._page_number_char_count

    def _add_page_number(self, posts: List[str]) -> List[str]:
        return [f"{post} ({i+1}/{len(posts)})" for i, post in enumerate(posts)]

    def _split_space_segmented_text(self, text: str) -> List[str]:
        posts: List[str] = []
        post = ""
        for tok in re.split(r"(\W)", text):
            if len(post) + len(tok) < self._content_char_limit:
                post += tok
            else:
                posts.append(post)
                post = tok if all(ch != " " for ch in tok) else ""
        return posts + ([post] if post else [])

    def _split_char_segmented_text(self, text: str) -> List[str]:
        return [
            text[0 + i : self._content_char_limit + i]
            for i in range(0, len(text), self._content_char_limit)
        ]

    def split_into_posts(self, text: str) -> List[str]:
        if len(text) < self._post_char_limit:
            # No need to split, just return it
            return [text]

        posts = (
            self._split_char_segmented_text(text)
            if langdetect.detect(text) in _CHAR_SEGMENTED_LANGS
            else self._split_space_segmented_text(text)
        )
        return self._add_page_number(posts)
