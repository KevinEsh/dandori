"""
GraphPlan.nodes[0] = {
    id(plan) # clase "Plan" no cuenta con un identificador unico en sus atributos por el momento
    "plan": Plan()
    "processName": str # Para identificar el plan con el proceso/paro dentro del grafo
}
"""

from copy import deepcopy
from attr import attrs, attrib
from datetime import datetime
from collections import defaultdict
from typing import List

from scheduler.algorithms.heuristics.fixers.globals import STATUS_NAME, DEFAULT_PARAMS
from scheduler.algorithms.heuristics.fixers.traductor import reset_interval_program, \
    solve_overlaped_plans

from scheduler.models import Program, Recipe, Time
from scheduler.validators import valid_recipe, valid_program
from scheduler.helpers.printers import solver_context
from scheduler.helpers.metadata import raise_invalid_date


@attrs
class Fixers:
    """Model to fix modified plans that could be overlaped

    Raises:
        NotImplementedError: In case it is not implemented method
    """

    program = attrib(default=Program())
    recetary = attrib(default=defaultdict(dict))  # material.code, [networks]
    parameters = attrib(default=DEFAULT_PARAMS)
    pivot = attrib(default=datetime.now())
    status = attrib(default=STATUS_NAME[0])
    scale = attrib(default="minutes")

    def set_scale(self, scale: str) -> None:
        """Set time scale which integer OR-tools variables will be set

        Args:
            scale (str): Try one of the followings: "days", "hours", "minutes", "seconds"

        Raises:
            NotImplementedError: If your scale is not implemented
        """
        _scales = ["days", "hours", "minutes", "seconds"]
        if scale not in _scales:
            raise NotImplementedError(
                f'scale {scale} not implemented. Try one of this: {_scales}')
        self.scale = scale

    def set_pivot(self, pivot: datetime) -> None:
        """Set the minimal time to start fixing plans

        Args:
            pivot (datetime): Starting date
        """
        raise_invalid_date(pivot)
        self.pivot = pivot

    def set_parameters(self, **params: int) -> None:
        """Set global parameters of Fixers
        """
        self.parameters.update(params)

    def set_program(self, program: Program) -> None:
        """Set the plans to be forced scheduled for the algorithm. These plans has to have valid data

        Args:
            program (GraphQLType): Program object that constains a list of no-overlaped plans
        """
        # Raise invalid program
        valid_program(program)
        # Copying all program data
        self.program = deepcopy(program)

    def add_recipes(self, recipes: List[Recipe]) -> None:
        """Add a new recipe to be considered as new way to create materials. This recipe will be registered in the recetary

        Args:
            recipes (GraphQLType): List of Schedule-Logic's Recipes to be added. Each has to have a list of processes conected in DAG form
            code (str): Optional default "None". You could choose between "unlock" & "locked"
        """
        # Raise invalid recipe
        for recipe in recipes:
            valid_recipe(recipe)

        # Register all recipes into the recetary
        for recipe in recipes:
            rcode = recipe.code

            # Add the material to the recetary and then register recipe graph template
            for rel in recipe.recipeMaterials:
                mcode = rel.material.code
                self.recetary[mcode][rcode] = recipe

    def __init_program(self):
        self.out_program = deepcopy(self.program)

    def run(self):
        """Run the heuristics to start to deoverlap the given program
        """
        self.__init_program()

        # Running Ortools solver
        with solver_context("Fixers") as report:
            s = solve_overlaped_plans(self.out_program, self.recetary, self.pivot, self.parameters)
            self.status = STATUS_NAME[s]
        report(self.status)

    def result(self) -> Program:
        """Return de current solution found

        Returns:
            Program: Program unoverlaped
        """
        if self.status == "UNKNOWN":
            return self.program

        reset_interval_program(self.out_program)
        return self.out_program
