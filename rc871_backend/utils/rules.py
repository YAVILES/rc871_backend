import ast
import copy
from typing import Union

from bunch import Bunch
from django.conf import settings
from money.money import Money


def convert_expr2_expression(expr) -> ast.Expression:
    expr.lineno = 0
    expr.col_offset = 0
    result = ast.Expression(expr.value, lineno=0, col_offset=0)

    return result


def reduce(value):
    if type(value) != dict:
        return value
    else:
        return Bunch(**value)


def exec_with_return(code: str, price: Union[Money, float], params: dict) -> any:
    if 'fixed' in params:
        params['fixed'] = Money(params['fixed'], settings.CURRENCY)

    params = Bunch(params)
    price = price

    ZERO = Money('0', settings.CURRENCY)
    currency = settings.CURRENCY
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]
    exec(compile(init_ast, "<ast>", "exec"), globals(), locals())
    if type(last_ast.body[0]) == ast.Expr:
        return eval(compile(convert_expr2_expression(last_ast.body[0]), "<ast>", "eval"), globals(), locals())
    else:
        exec(compile(last_ast, "<ast>", "exec"), globals(), locals())
