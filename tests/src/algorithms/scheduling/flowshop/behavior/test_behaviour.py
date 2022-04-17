import pytest
from scheduler.validators.valid_metadata import valid_metadata
from scheduler.examples import generate_random_inputs, build_models
from scheduler.examples.scheduling import make_flowshop_example

cases = generate_random_inputs(cases=10, size=(1, 5))


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_difference_result(flowshop_result, build_instances, guid, inputs):
    """
    From random inputs generetate the result to ckeck symmetry with a random solution
    """
    program = flowshop_result(guid, **inputs)
    assert program, \
        f"Program (guid={guid}) was not successful"
    data = build_instances(guid, **inputs)
    assert valid_metadata(data["demand"]), \
        f"Demand (guid={guid}) was not successful"
    model = make_flowshop_example(data=data)
    model.run()
    program2 = model.result()
    demand2 = model.request()
    assert program2, \
        f"Program from {data} generetated was not symmetry"
    assert demand2, \
        f"Demand from {data} datageneretated was not symmetry"


@pytest.mark.flowshop
@pytest.mark.parametrize(["guid", "inputs"], cases.items())
def test_ignitions(ignit_program, ignit_constrains, ignit_target, build_instances, guid, inputs):
    """
    Build an example instance to run just the ignition,checks on initiates Network Depency Graph from GraphTemplate
    """
    data = build_instances(guid, **inputs)
    model = make_flowshop_example(data=data)
    program = ignit_program(model)
    assert program, \
        f"Program from {data} got problem while try ignition"
    constrain = ignit_constrains(model)
    assert constrain, \
        f"Constrains from {data} got problem while try ignition"
    target = ignit_target(model)
    assert target, \
        f"Target from {data} got problem while try ignition"
