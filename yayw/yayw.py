import os
from typing import Optional

import click
from httpx import post
from loguru import logger

from yayw.splitter import Splitter


class YAYW:
    def __init__(
        self, user_id: str, access_token: str, max_characters_per_post: int = 500
    ) -> None:
        """
        Initialize the YAYW class with user ID, access token, and chunk threshold.

        :param user_id: User ID for YAYW
        :param access_token: Access token for YAYW
        :param chunk_threshold: Maximum characters per post
        """
        if not user_id or not access_token:
            logger.error(
                "Missing user id or access token, please configure YAYW_USER_ID and YAYW_ACCESS_TOKEN"
            )
        self._base_url = "https://graph.threads.net/v1.0"
        self._user_id = user_id
        self._access_token = access_token
        self._max_characters_per_post = max_characters_per_post

    def _create_and_publish_post(self, text: str, reply_to_id: Optional[str]) -> str:
        """
        Create and publish a post.

        :param text: The text content of the post
        :param reply_to_id: The ID of the post to reply to, if any
        :return: The ID of the created media
        """
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
        """
        Read the file at the given path, split its content into posts, and publish them.

        :param path: The path to the file to read
        """
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


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--user-id",
    default=os.environ.get("YAYW_USER_ID", ""),
    help="User ID for YAYW",
)
@click.option(
    "--access-token",
    default=os.environ.get("YAYW_ACCESS_TOKEN", ""),
    help="Access token for YAYW",
)
@click.option(
    "--max-post-length",
    default=int(os.environ.get("YAYW_MAX_POST_LENGTH", 500)),
    help="Maximum characters per post",
)
def run(path: str, user_id: str, access_token: str, max_post_length: int):
    YAYW(user_id, access_token, max_post_length).run(path)
