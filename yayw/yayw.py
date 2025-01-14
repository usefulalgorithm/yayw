import os
import sys
from typing import List, Optional

from httpx import post
from loguru import logger


class YAYW:
    def __init__(
        self, user_id: str, access_token: str, chunk_threshold: int = 450
    ) -> None:
        self._base_url = "https://graph.threads.net/v1.0"
        self._user_id = user_id
        # TODO think refresh mechanism
        self._access_token = access_token
        self._chunk_threshold = chunk_threshold

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

    def _split_lines_into_chunks(self, lines: List[str]) -> List[str]:
        texts: List[str] = []
        chunk, char_count = [], 0
        for line in lines:
            line_char_count = len(line)

            if char_count + line_char_count > self._chunk_threshold:
                # finalize chunk and make new one
                texts.append("".join(chunk))
                chunk, char_count = [], 0

            chunk.append(line)
            char_count += line_char_count

        if chunk:
            texts.append("".join(chunk))

        logger.info(f"# of chunks: {len(texts)}")

        # Finalize chunks
        texts = [text + f" ({i + 1}/{len(texts)})" for i, text in enumerate(texts)]

        return texts

    def run(self, path: str) -> None:
        with open(path) as f:
            texts = self._split_lines_into_chunks(f.readlines())

        if not texts:
            logger.warning("Nothing to yap about")
            return

        media_id = None
        for text in texts:
            media_id = self._create_and_publish_post(text, reply_to_id=media_id)
            logger.info(f"Created post: {media_id}")


def yayw(
    path: str,
    user_id: str = os.environ["YAYW_USER_ID"],
    access_token: str = os.environ["YAYW_ACCESS_TOKEN"],
    max_post_length: int = int(os.environ.get("YAYW_MAX_POST_LENGTH", 450)),
):
    YAYW(user_id, access_token, max_post_length).run(path)
