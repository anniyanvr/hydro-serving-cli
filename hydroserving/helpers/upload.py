import pprint

from hydroserving.httpclient.api import UploadMetadata
from hydroserving.helpers.assembly import assemble_model
from hydroserving.models.model_metadata import ModelMetadata
import click


def upload_model(model_api, model):
    tar = assemble_model(model)
    model_metadata = ModelMetadata.from_folder_metadata(model)

    click.echo("Uploading to {}".format(model_api.connection.remote_addr))

    contract = None
    if model_metadata.model_contract is not None:
        contract = str(model_metadata.model_contract)

    metadata = UploadMetadata(
        model_name=model_metadata.model_name,
        model_type=model_metadata.model_type,
        model_contract=contract if contract else None,
        description=model_metadata.description,
        namespace=model_metadata.namespace,
        data_profile_types=None
    )
    click.echo("Upload request metadata:")
    click.echo(pprint.pformat(metadata.to_dict()))
    click.echo()

    with click.progressbar(length=1, label='Uploading model assembly')as bar:
        create_encoder_callback = create_bar_callback_factory(bar)
        result = model_api.upload(tar, metadata, create_encoder_callback)
    return result


def create_bar_callback_factory(bar):
    def create_click_callback(multipart_encoder):
        bar.length = multipart_encoder.len

        def callback(monitor):
            bar.update(monitor.bytes_read)

        return callback

    return create_click_callback
