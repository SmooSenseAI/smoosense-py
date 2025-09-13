import logging
import os
import pathlib
from collections.abc import Generator

import requests
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, jsonify, redirect, request, send_file
from flask import Response as FlaskResponse
from werkzeug.wrappers import Response

from smoosense.exceptions import AccessDeniedException, InvalidInputException
from smoosense.utils.api import handle_api_errors, require_arg
from smoosense.utils.local_fs import LocalFileSystem
from smoosense.utils.s3_fs import S3FileSystem

logger = logging.getLogger(__name__)
fs_bp = Blueprint("fs", __name__)


@fs_bp.get("/ls")
@handle_api_errors
def get_ls() -> Response:
    path = require_arg("path")
    limit = int(request.args.get("limit", 100))
    show_hidden = request.args.get("show_hidden", "false").lower() == "true"
    if path.startswith("s3://"):
        s3_client = current_app.config["S3_CLIENT"]
        items = S3FileSystem(s3_client).list_one_level(path, limit)
    else:
        items = LocalFileSystem.list_one_level(path, limit, show_hidden)
    return jsonify([item.model_dump() for item in items])


@fs_bp.get("/get-file")
@handle_api_errors
def get_file() -> Response:
    path = require_arg("path")
    ext = os.path.splitext(path)[1]
    mime_type = {
        ".json": "application/json",
        ".txt": "text/plain",
    }

    if path.startswith("http://"):
        logger.info(f"Fetching HTTP URL {path}")
        try:
            response = requests.get(path, stream=True, timeout=30)
            response.raise_for_status()

            # Get content type from response headers or use file extension
            content_type = response.headers.get(
                "content-type", mime_type.get(ext, "application/octet-stream")
            )

            # Create a Flask response with the content
            def generate() -> Generator[bytes, None, None]:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            flask_response = FlaskResponse(generate(), content_type=content_type)
            flask_response.headers["Access-Control-Allow-Origin"] = "*"
            flask_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            flask_response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return flask_response
        except requests.RequestException as e:
            logger.error(f"Failed to fetch HTTP URL {path}: {e}")
            raise InvalidInputException(f"Failed to fetch URL: {e}") from e
    elif path.startswith("s3://"):
        logger.info(f"Generating signed URL for {path}")
        s3_client = current_app.config["S3_CLIENT"]
        signed_url = S3FileSystem(s3_client).sign_get_url(path)
        return redirect(signed_url)
    else:
        if path.startswith("~"):
            path = os.path.expanduser(path)
        logger.info(f"Sending file {path}")
        return send_file(path, mimetype=mime_type.get(ext, "application/octet-stream"))


@fs_bp.post("/upload")
@handle_api_errors
def upload_file() -> Response:
    path = require_arg("path")
    try:
        content = request.json["content"] if request.json else None
        if content is None:
            raise KeyError("content")
    except (KeyError, ValueError, AssertionError) as e:
        raise InvalidInputException('Invalid content. Expecting JSON: {"content": "xxx"}') from e

    if path.startswith("s3://"):
        s3_client = current_app.config["S3_CLIENT"]
        try:
            S3FileSystem(s3_client).put_file(path, content)
            return jsonify({"status": "success"})
        except ClientError as e:
            msg = str(e)
            if "AccessDenied" in msg:
                raise AccessDeniedException(msg) from e
            else:
                raise e
    else:
        if path.startswith("~"):
            path = os.path.expanduser(path)
        pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
    return jsonify({"status": "success"})
