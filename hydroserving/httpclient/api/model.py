from hydroserving.httpclient.errors import HSApiError
import json


class UploadMetadata:
    """
    This class represents `ModelUpload` data structure in manager.
    Field names must be the same.

    NOTE: Manager expects JSON fields in camelCase
    """
    def __init__(self, model_name, model_type, model_contract, description, namespace, data_profile_types):
        self.description = description
        self.contract = model_contract
        self.modelType = model_type
        self.name = model_name
        self.namespace = namespace
        self.dataProfileTypes = data_profile_types

    def to_dict(self):
        res = {}
        for k, v in self.__dict__.items():
            if v is None:
                continue
            res[k] = v
        return res


class ModelAPI:
    def __init__(self, connection):
        self.connection = connection

    def build(self, model_id):
        data = {
            "modelId": model_id
        }
        return self.connection.post("/api/v1/model/build", data)

    def list(self):
        return self.connection.get("/api/v1/model")

    def upload(self, assembly_path, metadata, create_encoder_callback=None):
        if not isinstance(metadata, UploadMetadata):
            raise HSApiError("{} is not UploadMetadata".format(metadata))

        return self.connection.multipart_post(
            url="/api/v1/model/upload",
            fields={
                "metadata": json.dumps(metadata.to_dict()),
                "payload": (metadata.name, open(assembly_path, "rb"))
            },
            create_encoder_callback=create_encoder_callback
        )

    def list_versions(self):
        return self.connection.get("/api/v1/model/version")

    def find_version(self, model_name, model_version):
        for version in self.list_versions():
            if version["modelName"] == model_name and version["modelVersion"] == model_version:
                return version
        return None
