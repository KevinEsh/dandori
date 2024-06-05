from gstorm import GraphQLType
# * Validator dependencies
from dandori.validators.valid_metadata import valid_metadata
from dandori.validators.valid_material import valid_material
from dandori.validators.valid_process import valid_process

model = "Recipe"


def valid_recipe(recipe: GraphQLType, depth: int = 0) -> None:
    """Validate if input instance is a valid "Recipe" otherwise raise a ValueError exception

    Args:
        recipe (GraphQLType): GraphQLType instance from a "Recipe" class

    Raises:
        ValueError: Is not a Recipe's instance
        ValueError: Has not code
        ValueError: Has not processes added
        ValueError: Has not material associated
    """
    modelname = valid_metadata(recipe)
    if modelname != model:
        raise ValueError(f"instance {recipe.id} is not '{model}' model")
    if not recipe.code:
        raise ValueError(f"{model} instance {recipe.id} has no 'code'")
    if not recipe.recipeProcesses:
        raise ValueError(
            f"{model} instance {recipe.id} has no 'recipeProcesses'")
    if not recipe.recipeMaterials:
        raise ValueError(
            f"{model} instance {recipe.id} has no 'recipeMaterials'")

    # Recursive validation
    if not depth:
        return

    for arc in recipe.recipeProcesses:
        valid_process(arc.process, depth-1)
    for arc in recipe.recipeMaterials:
        valid_material(arc.material, depth-1)


if __name__ == "__main__":
    # Pa' juegar a las pruebitas. Se puede pasar el código a los test de estos validadores aftermath
    from dandori.models import RecipeMaterial, RecipeProcess
    from dandori.models import Recipe
    rps = [RecipeProcess() for _ in range(10)]
    rms = [RecipeMaterial() for _ in range(10)]
    r = Recipe(code="1")
    r.recipeProcesses.extend(rps)
    r.recipeMaterials.extend(rms)
    valid_recipe(r)
