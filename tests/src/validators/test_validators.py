import pytest
from dandori.examples import generate_random_inputs
from dandori.validators import valid_demand, valid_program, valid_material, valid_order,\
    valid_resource, valid_recipe, valid_stop, valid_uom  # valid_lot, valid_invGroup, valid_changeover

cases = generate_random_inputs(cases=10, size=(1, 5))

# TODO: SDLSR-125
# @pytest.mark.validator
# @pytest.mark.parametrize(["guid", "inputs"], cases.items())
# def test_valid_inventoryGroup(build_instances, guid, inputs):
#     try:
#         data = build_instances(guid, **inputs)
#         valid_inventoryGroup(data["demand"], depth=1)
#     except Exception as exc:
#         pytest.fail(exc.args[0])

# TODO: SDLSR-126
# @pytest.mark.validator
# @pytest.mark.parametrize(["guid", "inputs"], cases.items())
# def test_valid_lot(build_instances, guid, inputs):
#     try:
#         data = build_instances(guid, **inputs)
#         valid_lot(data["demand"], depth=1)
#     except Exception as exc:
#         pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_material(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_material(data["products"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_order(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_order(data["demand"].orders[0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


# @pytest.mark.validator
# @pytest.mark.parametrize(["guid", "inputs"], cases.items())
# def test_valid_plan(build_instances, guid, inputs):
#     try:
#         data = build_instances(guid, **inputs)
#         valid_plan(data["program"].plans[0], depth=1)
#     except Exception as exc:
#         pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_resource(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_resource(data["processors"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_function(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_resource(data["processors"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_program(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_program(data["program"], depth=0)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_recipe(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_recipe(data["recipes"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_demand(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_demand(data["demand"], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_stop(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_stop(data["stops"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])


@pytest.mark.validator
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_valid_uom(build_instances, guid, inputs):
    try:
        data = build_instances(guid, **inputs)
        valid_uom(data["uoms"][0], depth=1)
    except Exception as exc:
        pytest.fail(exc.args[0])

#TODO: SDLSR-128
# @pytest.mark.validator
# @pytest.mark.parametrize(["guid", "inputs"], cases.items())
# def test_valid_changeover(build_instances, guid, inputs):
#     try:
#         data = build_instances(guid, **inputs)
#         valid_changeover(data["changeovers"][0], depth=1)
#     except Exception as exc:
#         pytest.fail(exc.args[0])
