#github name: Chemical-Equation-Manipulator
from bakery import assert_equal
from chempy import balance_stoichiometry
from drafter import *
from dataclasses import dataclass

#dataclasses
@dataclass
class Compound:
    element: str
    coefficient: int
    

#state dataclass
@dataclass
class State:
    compound_reactant: list[Compound]
    compound_product: list[Compound]
    equation: str
    masses: list[float]
#index
@route
def index(state: State) -> Page:
    """
    Shows the user what options they have and the chemical equation if they had set it already
    Args:
        state(State): a compound, reactant_length, product_length, and masses of all the chemical compounds
    """
    return Page(state,
                [
                 state.equation,
                 Button("balance_equation", "balance"),
                 Button("find_value", "find"),
                 Button("limiting_reactant", "limiting reactant"),
                 Button("percent_yield", "percent yield"),
                 ])
def show_equation(state: State) -> str:
    """
    takes in a state and shows the chemical equation is
    Args:
        state (State): a compound, reactant_length, product_length, and masses of all the chemical compounds
    returns:
        Str: The chemical Equation
    """
    if not state.compound_reactant or not state.compound_product:
        return "nothing"
    equation1 = ""
    for reactant in state.compound_reactant:
        equation1 = equation1 + str(reactant.coefficient) + " " + reactant.element + " +"
    equation2 = ""
    for product in state.compound_product:
        equation2 = equation2 + str(product.coefficient) + " " + product.element + " +"
    return equation1[:-1] + "->" + equation2[:-1]

@route
def balance(state: State) -> Page:
    """
    takes in a state and generates a page to balance an equation
    Args:
        state(State): a compound, reactant_length, product_length, and masses of all the chemical compounds
    Returns:
        Page: containing buttons and text boxes for inputs
    """
    return Page(state, [
        "Separate reactants spaces",
        TextBox("reactants"),
        "Separate Products spaces",
        TextBox("products"),
        Button("Balance?", "balance_equation")
        ])
@route
def balance_equation(state: State, products: str, reactants: str):
    balanced_reactants, balanced_products = balance_stoichiometry(
        set(reactants.split()),
        set(products.split())
        )
    
    for chemical, coefficient in balanced_products.items():
        state.compound_product.append(Compound(chemical, coefficient))
    for chemical, coefficient in balanced_reactants.items():
        state.compound_reactant.append(Compound(chemical, coefficient))
    state.equation = show_equation(state)
    return index(state)
        
    
    
@route
def find_value(state: State) -> Page:
    pass
@route
def limiting_reactant(state: State) -> Page:
    pass
@route
def percent_yield(state: State) -> Page:
    pass
start_server(State(
    [],
    [],
    "",
    []
    ))
