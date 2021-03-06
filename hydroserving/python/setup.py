import importlib

import setuptools

from hydroserving.cli.context_object import ContextObject
from hydroserving.core.contract import contract_to_dict
from hydroserving.core.model.entities import UploadMetadata
from hydroserving.python.contract_decorators import *


class ModelDefinitionError(Exception):
    pass


def python_runtime(major, minor):
    return "hydrosphere/serving-runtime-python-{major}.{minor}:dev".format(major=major, minor=minor)


def setup(
        name,
        entry_point=None,
        requirements=None,
        runtime=None,
        payload='.',
        monitoring=None,
        metadata=None):
    python_version = sys.version_info
    if not requirements:
        requirements = []
    if not runtime:
        runtime = python_runtime(python_version[0], python_version[1])
    print("Runtime", runtime)
    if not entry_point:
        raise ModelDefinitionError("Need to set up a prediction endpoint. Use `module:func` format.")
    (entry_module, entry_func) = entry_point.split(':')
    if not monitoring:
        monitoring = []

    func = get_entrypoint(entry_module, entry_func)
    print("Entrypoint", func.__name__)
    contract = func._serving_contract
    print("Model contract", contract)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"
    generate_setup(name, requirements, entry_point)
    if cmd == 'upload':
        upload(name, requirements, entry_point, contract, runtime, metadata)
    elif cmd == 'start':
        func._serving_server.start()
    else:
        print('No command supplied')


def generate_setup(name, requirements, entrypoint):
    src = """
# THIS FILE IS GENERATED BY HYDROSPHERE
# CHANGES IN THIS FILE COULD BE OVERIDDEN

import setuptools

setuptools.setup(
    name='{name}',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires={requirements},
    entry_points='''
        [console_scripts]
        {name}={entrypoint}._serving_server.start
    '''
)""".format(name=name, entrypoint=entrypoint, requirements=requirements)
    with open('setup.py', 'w') as f:
        f.write(src)

    manifest_src = """
recursive-include . *
"""
    with open('MANIFEST.in', 'w') as f:
        f.write(manifest_src)


def upload(name, requirements, entrypoint, contract, runtime, metadata):
    print("UPLOAD")
    # create tar.gz source distribution
    setuptools.setup(
        name=name,
        packages=setuptools.find_packages(),
        include_package_data=True,
        install_requires=requirements,
        entry_points='''
            [console_scripts]
            {name}={entrypoint}._serving_server.start
        '''.format(name=name, entrypoint=entrypoint),
        script_args=['sdist', '--formats=gztar']  # pass setup arguments as in `python setup.py install`
    )
    tar_path = './dist/{name}-0.0.0.tar.gz'.format(name=name)
    context = ContextObject.with_config_path()
    # create model object
    (r_name, r_tag) = runtime.split(':')
    metadata = UploadMetadata(
        name=name,
        contract=contract_to_dict(contract),
        runtime={
            'name': r_name,
            'tag': r_tag
        },
        install_command="cd {script_name}-0.0.0 && python setup.py install\nENTRYPOINT cd {script_name}-0.0.0 && {script_name}".format(
            script_name=name),  # Hacky
        metadata=metadata
    )
    context.model_service.upload(tar_path, metadata)


def get_entrypoint(module_path, func_path):
    module = importlib.import_module(module_path)
    named_func = inspect.getmembers(module, lambda a: inspect.isfunction(a) and a.__name__ == func_path)[0]
    return named_func[1]
