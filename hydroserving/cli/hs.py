import click
import os

from hydroserving.constants.help import SYSTEM_HELP
from hydroserving.helpers.package import get_subfiles
from hydroserving.models import ServingMetadata, ModelDefinition
from hydroserving.models.context_object import ContextObject


@click.group()
@click.option('--name',
              default=None,
              show_default=True,
              required=False)
@click.option('--model_type',
              default=None,
              required=False)
@click.option('--contract',
              type=click.Path(exists=True),
              default=None,
              required=False)
@click.option('--description',
              default=None,
              required=False)
@click.option('--system',
              default=False,
              is_flag=True,
              show_default=False,
              help=SYSTEM_HELP,
              required=False)
@click.pass_context
def hs_cli(ctx, name, model_type, contract, description, system):
    ctx.obj = ContextObject()
    metadata = ServingMetadata.from_directory(os.getcwd())

    if metadata is None:  # no metadata, try to fill as much as possible
        if name is None:
            name = os.path.basename(os.getcwd())

        metadata = ServingMetadata(ModelDefinition(
            name=name,
            model_type=model_type,
            contract_path=contract,
            description=description,
            is_system=system,
            payload=get_subfiles("./"),
            profile_fields=None
        ), None)
    else:  # metadata is present. override fields with CLI args
        if name is not None:
            metadata.model.name = name
        if model_type is not None:
            metadata.model.model_type = model_type
        if contract is not None:
            metadata.model.contract_path = contract
        if description is not None:
            metadata.model.description = description

        metadata.model.is_system = metadata.model.is_system or system

    ctx.obj.metadata = metadata
