import click
import requests

from hydroserving.cli.hs import hs_cli
from hydroserving.cli.utils import ensure_metadata
from hydroserving.helpers.package import read_contract_cwd
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api import ModelAPI
from hydroserving.constants import help
from hydroserving.httpclient.remote_connection import RemoteConnection
import pprint


@hs_cli.command(help=help.STATUS_HELP)
@click.pass_obj
def status(obj):
    metadata = ensure_metadata(obj)
    pdict = pprint.pformat(metadata.model.__dict__)
    click.echo("Model metadata:")
    click.echo(pdict)


@hs_cli.command()
@click.pass_obj
def contract(obj):
    metadata = ensure_metadata(obj)
    contract_obj = read_contract_cwd(metadata.model)
    if contract_obj is None:
        click.echo("Contract is not specified.")
    else:
        click.echo("Contract:")
        click.echo(contract_obj)


@hs_cli.command(help=help.UPLOAD_HELP, context_settings=help.CONTEXT_SETTINGS)
@click.option('--host',
              default="localhost",
              show_default=True,
              help=help.UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=80,
              show_default=True,
              help=help.UPLOAD_PORT_HELP,
              required=False)
@click.pass_obj
def upload(obj, host, port):
    metadata = ensure_metadata(obj)
    remote = RemoteConnection("http://{}:{}".format(host, port))
    model_api = ModelAPI(remote)
    click.echo("Uploading model:")
    pmeta = pprint.pformat(metadata.model.__dict__)
    click.echo(pmeta)
    click.echo()
    try:
        result = upload_model(model_api, metadata.model)

        presult = pprint.pformat(result)
        click.echo("Upload result:")
        click.echo(presult)
    except requests.ConnectionError as err:
        click.echo("Connection error")
        click.echo(err)
        raise SystemExit(-1)


@hs_cli.command(help=help.STATUS_HELP, context_settings=help.CONTEXT_SETTINGS)
@click.option('--host',
              default="localhost",
              show_default=True,
              help=help.UPLOAD_HOST_HELP,
              required=False)
@click.option('--port',
              default=80,
              show_default=True,
              help=help.UPLOAD_PORT_HELP,
              required=False)
@click.argument('id')
def build_status(host, port, id):
    click.echo("Fetching build status for: {}".format(id))
    try:
        remote = RemoteConnection("http://{}:{}".format(host, port))
        response = remote.get("/api/v1/model/build/{}".format(id))
        presult = pprint.pformat(response)
        click.echo("Upload result:")
        click.echo(presult)
    except requests.ConnectionError as err:
        click.echo("Connection error")
        click.echo(err)
        raise SystemExit(-1)
