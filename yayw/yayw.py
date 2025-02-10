import os
from typing import Optional

from httpx import post
from loguru import logger

from yayw.splitter import Splitter


class YAYW:
    def __init__(
        self, user_id: str, access_token: str, chunk_threshold: int = 500
    ) -> None:
        self._base_url = "https://graph.threads.net/v1.0"
        self._user_id = user_id
        # TODO think refresh mechanism
        self._access_token = access_token
        self._max_characters_per_post = chunk_threshold

    def _create_and_publish_post(self, text: str, reply_to_id: Optional[str]) -> str:
        resp = post(
            f"{self._base_url}/{self._user_id}/threads",
            params={
                "access_token": self._access_token,
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": reply_to_id,
            },
            timeout=30,
        )
        creation_id = resp.json()["id"]
        logger.info(f"creation_id: {creation_id}")

        resp = post(
            f"{self._base_url}/{self._user_id}/threads_publish",
            params={
                "access_token": self._access_token,
                "creation_id": creation_id,
            },
            timeout=30,
        )
        media_id = resp.json()["id"]
        return media_id

    def run(self, path: str) -> None:
        with open(path) as f:
            posts = Splitter(
                max_characters_per_post=self._max_characters_per_post
            ).split_into_posts(f.read())

        if not posts:
            logger.warning("Nothing to yap about")
            return

        media_id = None
        for current_post in posts:
            media_id = self._create_and_publish_post(current_post, reply_to_id=media_id)
            logger.info(f"Created post: {media_id}")


def yayw(
    path: str,
    user_id: str = os.environ["YAYW_USER_ID"],
    access_token: str = os.environ["YAYW_ACCESS_TOKEN"],
    max_post_length: int = int(os.environ.get("YAYW_MAX_POST_LENGTH", 500)),
):
    YAYW(user_id, access_token, max_post_length).run(path)
