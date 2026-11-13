
from bakery import assert_equal
from chempy import balance_stoichiometry
from chempy import Substance
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
        state(State): a list of reactants, a list of products, an equation, and a list of masses
    Returns:
        Page: shows the chemical equation in the state and 3 buttons to call different equations.
    
    """
    return Page(state,
                [
                 Header("Chemical Equation Manipulator"),
                 state.equation,
                 Button("balance equation", "balance"),
                 Button("find value", "find_value"),
                 Button("percent yield", "percent_yield")
                 ])
assert_equal(
    index(State([], [], "", [])).content[1],
    ""
)
#part of the index
def show_equation(state: State) -> str:
    """
    takes in a state and shows what the chemical equation is
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
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
assert_equal(show_equation(
    State(
    [Compound("H2O", 2)],
    [Compound("H2", 2), Compound("O2", 1)],
    "",
    [])),
    "2 H2O ->2 H2 +1 O2 ")

#balancing functions
@route
def balance(state: State) -> Page:
    """
    takes in a state and generates a page to show the text boxes and buttons to define and balance the chemical equation
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
    Returns:
        Page: containing a button to continue and text boxes for the inputs
    """
    return Page(state, [
        "Separate reactants with spaces",
        TextBox("reactants"),
        "\n",
        "Separate Products with spaces",
        TextBox("products"),
        "\n",
        Button("Balance", "balance_equation"),
        Button("return", "index")
        ])
assert_equal(
    balance(State([], [], "", [])).content[0],
    "Separate reactants with spaces"
)
#a check specifically for the balancing function
def is_chemical(formula: str) -> bool:
    """
    takes in a string and checks if it is a chemical
    Arg:
        formula(str): a chemical that needs to be checked
    Return:
        bool: if the chemical is valid
    """
    try:
        Substance.from_formula(formula)
        return True
    except Exception:
        return False
assert_equal(is_chemical("H2O"), True)
assert_equal(is_chemical("NaCl"), True)
assert_equal(is_chemical("XYZ123"), False)


@route
def balance_equation(state: State, products: str, reactants: str) -> Page:
    """
    takes in a state, products, and reactants. Balances the the equation
    Mutates the state to include a list of the reactants, products, and the equation.
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
        products(str): the user inputed products
        reactants(str): the user inputed reactants
    Returns:
        Page: returns to the index with the new state
    """
    if not is_chemical(products) or not is_chemical(reactants):
        return error(state, "incorrect products or reactants")
    balanced_reactants, balanced_products = balance_stoichiometry(
        set(reactants.split()),
        set(products.split())
        )
    state = State([], [], "", [])
    for chemical, coefficient in balanced_products.items():
        state.compound_product.append(Compound(chemical, coefficient))
    for chemical, coefficient in balanced_reactants.items():
        state.compound_reactant.append(Compound(chemical, coefficient))
    state.equation = show_equation(state)
    return index(state)
assert_equal(
    balance_equation(
        State([], [], "", []),
        "H2O",
        "H2 O2"
    ).state.equation,
    "2 H2 +1 O2 ->2 H2O "
)
#for the find_value function        
def get_molar_mass(chemical: str) -> float:
    """
    this function takes in a chemical and returns its molar mass
    Args:
        chemical(str): a chemical compound
    Returns:
        float: the molar mass of the chemical compound
    """
    return float(Substance.from_formula(chemical).mass)

assert_equal(get_molar_mass("H2O"), 18.015)

#find value functions
@route
def find_value(state: State) -> Page:
    """
    takes in a state and gives two text boxes for the user to input there mass and compound
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
    returns:
        Page: a page with 2 textboxes and a button
    """
    return Page(state, [
        "what mass in grams",
        TextBox("mass"),
        "\n",
        "what compound",
        TextBox("compound"),
        "\n",
        Button("Find", "find"),
        Button("return", "index")
        ])
assert_equal(
    find_value(State([], [], "", [])).content[0],
    "what mass in grams"
)
@route
def find(state: State, mass: str, compound: str) -> Page:
    """
    It calculates the mols and masses of all compounds in the equation
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
        mass(str): the user inputed mass used to determine all other values
        compound(str): the user inputed chemical that determines the starting coefficient
    Returns:
        Page: a page with equation and all masses and mols
    """
    if (compound not in [c.element for c in state.compound_reactant]) and \
       (compound not in [c.element for c in state.compound_product]):
        return error(state, "bad compound")
    try:
        mass = float(mass)
        if mass <= 0:
            return error(state, "bad mass")
    except ValueError:
        return error(state, "bad mass")
    #combine products and reactants
    combined_coefficients = []
    combined_elements =  []
    for chemical in state.compound_reactant:
        combined_elements.append(chemical.element)
        combined_coefficients.append(chemical.coefficient)
    for chemical in state.compound_product:
        combined_elements.append(chemical.element)
        combined_coefficients.append(chemical.coefficient)
    #find mol of input
    input_mass = float(mass)
    input_moles = input_mass / get_molar_mass(compound)

    input_coefficient = 0

    for element, coefficient in zip(combined_elements, combined_coefficients):
        if element == compound:
            input_coefficient = coefficient
            break

    list_mols = []

    for coefficient in combined_coefficients:
        list_mols.append(
            input_moles * coefficient / input_coefficient
            )
    list_mass = []
    for mol, element, coefficient in zip(list_mols, combined_elements, combined_coefficients):
        list_mass.append(mol*(get_molar_mass(element)))
    final_list = []
    for mol, mass, element in zip(list_mols, list_mass, combined_elements):
        final_list.append("mols: " + str(mol) + " mass: " + str(mass) + " element: " + element + "\n")
    state.masses = list_mass
    return Page(state, [
        state.equation,
        "\n",
        *final_list,
        Button("return", "index")
        ])
assert_equal(
    find(
        State(
            [Compound("H2", 2), Compound("O2", 1)],
            [Compound("H2O", 2)],
            "2 H2 +1 O2 ->2 H2O ",
            []
        ),
        "18.015",
        "H2O"
    ).state.masses,
    [2.016, 15.999, 18.015]
)
#percent yield functions
@route
def percent_yield(state: State) -> Page:
    """
    allows the user to input what compound they want to check the percent yield of and what mass they want to compare
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
    Returns:
        Page: a page with 2 text boxes and a button
    """
    return Page(state, [
        "what compound's yield do you want?",
        TextBox("chemical"),
        "\n",
        "what is the actual yield of this compound?",
        TextBox("mass"),
        "\n",
        Button("calculate", "calculate_percent_yield"),
        Button("return", "index")
        ])
assert_equal(
    percent_yield(State([], [], "", [])).content[0],
    "what compound's yield do you want?"
)
@route
def calculate_percent_yield(state: State, chemical: str, mass: str) -> Page:
    """
    determines what the percent yield is.
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
        Chemical(str): the chemical that will be compared
        Mass(str): the mass that will be compared
    """

    if (chemical not in [c.element for c in state.compound_reactant]) and \
       (chemical not in [c.element for c in state.compound_product]):
        return error(state, "bad compound")
    try:
        mass_new = float(mass)
        if mass_new <= 0:
            return error(state, "bad mass")
    except ValueError:
        return error(state, "bad mass")
    mass_new = float(mass)

    
    full_compound_list = state.compound_reactant + state.compound_product
    percent = 0.0
    for substance, mass1 in zip(full_compound_list, state.masses):
        if substance.element == chemical:
            percent = str(mass_new/mass1*100)
    return Page(state, [
        "percent yield:",
        percent,
        "\n",
        Button("return", "index"),
        ])
assert_equal(
    calculate_percent_yield(
        State(
            [Compound("H2", 2), Compound("O2", 1)],
            [Compound("H2O", 2)],
            "2 H2 +1 O2 ->2 H2O ",
            [2.01588, 15.999, 18.015]
        ),
        "H2O",
        "9.0075"
    ).content[1],
    "50.0"
)
#general error equation
@route
def error(state: State, reason: str) -> Page:
    """
    tells the user something is wrong with their code and sends them to the index
    Args:
        state(State): a list of reactants, a list of products, an equation, and a list of masses
    Returns:
        Page: a page with the error message and a return
    """
    return Page(state, [
        reason,
        "\n",
        Button("return", "index")
        ])
assert_equal(
    error(State([], [], "", []), "bad mass").content[0],
    "bad mass"
)
start_server(State(
    [],
    [],
    "",
    []
    ))
