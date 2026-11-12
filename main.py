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
    
    return Page(state,
                [
                 state.equation,
                 Button("balance_equation", "balance"),
                 ])
def show_equation(state: State) -> str:
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
        
    
start_server(State(
    [],
    [],
    "",
    []
    ))
