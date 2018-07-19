import os
import json
import shutil
import unittest

import requests
import requests_mock
from click.testing import CliRunner

from hydroserving.cli import hs_cli
from hydroserving.helpers.package import with_cwd
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient import HydroservingClient
from hydroserving.models import ServingMetadata

MODEL_FOLDER = "./examples/local_dev"


def build_example(hs_api):
    meta = ServingMetadata.from_directory(os.getcwd())
    return upload_model(hs_api.models, meta.model)


class CLICase(unittest.TestCase):
    def test_incorrect_status(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(hs_cli, ["status"])
            print(result)
            assert result.exit_code == 0

    def test_correct_status(self):
        def _test_correct_status():
            runner = CliRunner()
            result = runner.invoke(hs_cli, ["status"])
            assert result.exit_code == 0
            assert "Model metadata:" in result.output
            assert "'name': 'example_script'" in result.output
        with_cwd(MODEL_FOLDER, _test_correct_status)

    def upload_matcher(self, request):
        if request.path_url == "/api/v1/model/upload":
            fields = request.text.encoder.fields
            assert "payload" in fields

            metadata_field = json.loads(fields['metadata'])
            assert 'modelContract' not in metadata_field
            assert metadata_field['modelType'] == "python:3.6"
            assert metadata_field["name"] == "example_script"
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(
                {
                    "model_name": "example_script",
                    "model_type": "python:3.6"
                }
            ).encode("utf-8")
            return resp
        return None

    def test_model_upload(self):
        with requests_mock.Mocker() as req_mock:
            req_mock.add_matcher(self.upload_matcher)
            hs_api = HydroservingClient("http://localhost")
            result = with_cwd(MODEL_FOLDER, build_example, hs_api)
            assert "example_script" in result["model_name"]
            assert "python:3.6" in result["model_type"]