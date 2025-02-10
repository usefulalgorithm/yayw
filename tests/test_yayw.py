import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock
from yayw.yayw import YAYW


@pytest.fixture
def yayw_instance():
    return YAYW(
        user_id="test_user", access_token="test_token", max_characters_per_post=500
    )


def test_init_missing_user_id():
    with patch("yayw.yayw.logger") as mock_logger:
        YAYW(user_id="", access_token="test_token")
        mock_logger.error.assert_called_with(
            "Missing user id or access token, please configure YAYW_USER_ID and YAYW_ACCESS_TOKEN"
        )


def test_init_missing_access_token():
    with patch("yayw.yayw.logger") as mock_logger:
        YAYW(user_id="test_user", access_token="")
        mock_logger.error.assert_called_with(
            "Missing user id or access token, please configure YAYW_USER_ID and YAYW_ACCESS_TOKEN"
        )


@patch("yayw.yayw.post")
def test_create_and_publish_post(mock_post, yayw_instance):
    mock_response = MagicMock()
    mock_response.json.side_effect = [{"id": "creation_id"}, {"id": "media_id"}]
    mock_post.return_value = mock_response

    media_id = yayw_instance._create_and_publish_post("test_text", None)
    assert media_id == "media_id"
    assert mock_post.call_count == 2


@patch("yayw.yayw.Splitter")
@patch("builtins.open", new_callable=mock_open, read_data="test content")
def test_run(mock_open, mock_splitter, yayw_instance):
    mock_splitter_instance = mock_splitter.return_value
    mock_splitter_instance.split_into_posts.return_value = ["post1", "post2"]

    with patch.object(
        yayw_instance, "_create_and_publish_post", return_value="media_id"
    ) as mock_create_and_publish_post:
        yayw_instance.run("test_path")
        mock_create_and_publish_post.assert_called_with("post2", reply_to_id="media_id")
        assert mock_create_and_publish_post.call_count == 2


def test_run_no_posts(yayw_instance):
    with (
        patch("yayw.yayw.Splitter") as mock_splitter,
        patch("yayw.yayw.logger") as mock_logger,
    ):
        mock_splitter_instance = mock_splitter.return_value
        mock_splitter_instance.split_into_posts.return_value = []

        with tempfile.NamedTemporaryFile() as f:
            yayw_instance.run(f.name)
            mock_logger.warning.assert_called_with("Nothing to yap about")
