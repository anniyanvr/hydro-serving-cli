import os
import unittest

from hydroserving.helpers.package import with_cwd
from hydroserving.models import ServingMetadata


class MetadataCase(unittest.TestCase):
    def test_absent_metadata(self):
        def _test_absent_metadata():
            metadata = ServingMetadata.from_directory(os.getcwd())
            print(os.getcwd())
            assert not metadata

        with_cwd("tests/test_metadata_resources/no_metadata", _test_absent_metadata)

    def test_full_metadata(self):
        def _test_full_metadata():
            metadata = ServingMetadata.from_directory(os.getcwd())
            print(os.getcwd())
            print(metadata)
            model = metadata.model
            assert model.name
            assert model.model_type
            assert model.contract_path
            assert model.payload
            assert model.description
            assert model.is_system is True
            assert model.profile_fields['name'] == "TEXT"
            assert model.profile_fields['avatar'] == "IMAGE"
            assert model.profile_fields['gender'] == "CATEGORICAL"

            dep = metadata.local_deployment
            assert dep.name
            assert dep.runtime
            assert dep.port
            assert dep.build

        with_cwd("tests/test_metadata_resources/full_metadata", _test_full_metadata)

    def test_partial_metadata(self):
        def _test_partial_metadata():
            metadata = ServingMetadata.from_directory(os.getcwd())
            print(os.getcwd())
            print(metadata)
            model = metadata.model
            assert model.name
            assert model.model_type
            assert model.contract_path
            assert model.payload
            assert model.is_system is True
            assert model.profile_fields['name'] == "TEXT"
            assert model.profile_fields['avatar'] == "IMAGE"
            assert model.profile_fields['gender'] == "CATEGORICAL"

        print(os.getcwd())
        with_cwd("tests/test_metadata_resources/partial_metadata", _test_partial_metadata)
