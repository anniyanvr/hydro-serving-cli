import ast
import pathlib
import sys
import hydro_serving_grpc.contract as hsc
import hydroserving.core.contract as ctr
from functools import wraps
import os

# PYTHON MODEL DECORATORS

class ContractError(Exception):
    pass

def entrypoint(func):
    func_args = func.__code__.co_varnames
    input_names = [x.name for x in func._serving_inputs]
    for a in func_args:
        if not a in input_names:
            raise ContractError("Missing contract for argument '{}'".format(a))

    func._serving_signature = ctr.ModelSignature(
            signature_name = func.__name__,
            inputs = func._serving_inputs,
            outputs = func._serving_outputs
        )
    func._serving_contract = ctr.ModelContract(
        model_name = func.__name__,
        predict = func._serving_signature
    )
    return func

def field(field_name, type, shape=None, profile=None):
    if not profile:
        profile = "NONE"
    field_def = {
        'type': type,
        'shape': shape,
        'profile': profile
    }
    return ctr.field_from_dict(field_name, field_def)

def input(field_name, type, shape=None, profile=None):
    f = field(field_name, type, shape)
    def dec(func):
        inputs = getattr(func, '_serving_inputs', [])
        inputs.append(f)
        func._serving_inputs = inputs
        return func
    return dec

def output(field_name, type, shape=None):
    f = field(field_name, type, shape)
    def dec(func):
        outputs = getattr(func, '_serving_outputs', [])
        outputs.append(f)
        func._serving_outputs = outputs
        return func
    return dec

# PARSERS

def top_level_functions(body):
    return [f for f in body if isinstance(f, ast.FunctionDef)]

def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)

# maybe use AST? https://stackoverflow.com/a/31005891
def infer_contract(script_path):
    if not os.path.exists(script_path):
        raise FileNotFoundError(script_path)
    print("Script path:", script_path)
    sys.path.append(script_path)
    script_ast = parse_ast(script_path)
    functions_list = top_level_functions(script_ast.body)
    possible_funcs = []
    for func in functions_list:
        print("Checking function:", ast.dump(func))
        for d in func.decorator_list:
            d_func = d.func
            d_name = d_func.value.id
            d_attr = d_func.attr
            if(d_name == "hs" or d_attr == "entrypoint"):
                possible_funcs.append(func)
    poss_dump = [ast.dump(x).attrs for x in possible_funcs]
    print("Possible model functions", print(poss_dump))
    return None


# FunctionDef(
#     name='test', 
#     args=arguments(args=[arg(arg='a', annotation=None), arg(arg='b', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), 
#     body=[Pass()],
#     decorator_list=[
#         Call(
#             func=Attribute(value=Name(id='hs', ctx=Load()), attr='inputs', ctx=Load()),
#             args=[],
#             keywords=[
#                 keyword(arg='a', value=Call(func=Name(id='Tensor', ctx=Load()), args=[], keywords=[keyword(arg='type', value=Name(id='INT', ctx=Load())), keyword(arg='shape', value=List(elts=[UnaryOp(op=USub(), operand=Num(n=1))], ctx=Load()))])),
#                 keyword(arg='b', value=Call(func=Name(id='Tensor', ctx=Load()), args=[], keywords=[keyword(arg='type', value=Name(id='DOUBLE', ctx=Load())), keyword(arg='shape', value=Name(id='scalar', ctx=Load()))]))
#             ]
#         ),
#         Call(
#             func=Attribute(value=Name(id='hs', ctx=Load()), attr='outputs', ctx=Load()),
#             args=[], 
#             keywords=[
#                 keyword(arg='sum', value=Call(func=Name(id='Tensor', ctx=Load()), args=[], keywords=[keyword(arg='type', value=Name(id='INT64', ctx=Load())), keyword(arg='shape', value=Name(id='scalar', ctx=Load()))])), 
#                 keyword(arg='product', value=Call(func=Name(id='Tensor', ctx=Load()), args=[], keywords=[keyword(arg='type', value=Name(id='DOUBLE', ctx=Load())), keyword(arg='shape', value=Name(id='scalar', ctx=Load()))]))
#             ]
#         )
#     ], 
#     returns=None
# )