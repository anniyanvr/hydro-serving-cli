import os

import click

from hydroserving.constants.click import CONTEXT_SETTINGS
from hydroserving.constants.config import HOME_PATH_EXPANDED
from hydroserving.models.context_object import ContextObject, ContextServices


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(message="%(prog)s version %(version)s")
@click.option('--override-server',
              default=None,
              required=False)
@click.pass_context
def hs_cli(ctx, override_server):
    if not os.path.isdir(HOME_PATH_EXPANDED):
        os.mkdir(HOME_PATH_EXPANDED)
    ctx.obj = ContextObject()

    if override_server is not None:
        click.echo('Warning: Current server is overridden to {}'.format(override_server))

    ctx.obj.services = ContextServices.with_config_path(HOME_PATH_EXPANDED, override_server)
