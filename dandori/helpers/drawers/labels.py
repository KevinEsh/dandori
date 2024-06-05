"""TODO LIST
- [ ] Programar mas funciones get_label
"""


def get_label(plan):
    # TODO: Cambiar el nombre a uno mas especifico
    if not plan.toSolve:
        return "Paro\n"
    order = plan.toSolve.name
    resource = plan.resource.name
    quantity = plan.quantity
    return f"{order}"


def get_label_2(plan, maxletters: int = 100) -> str:
    if not plan.toSolve:
        return "Paro\n"
    maxletters = int(3*(plan.endAt - plan.startAt).total_seconds() // (4*3600))
    pname = plan.process.name[0:maxletters]
    sname = plan.process.name[maxletters:2*maxletters]
    code = plan.toSolve.name[0:maxletters]
    return pname + "\n" + sname + "\n" + code


def get_label_3(plan, maxletters: int = 100) -> str:
    if not plan.toSolve:
        return "Paro\n"
    maxletters = int(3*(plan.endAt - plan.startAt).total_seconds() // (4*3600))
    pname = plan.process.name[0:maxletters]
    sname = plan.process.name[maxletters:2*maxletters]
    code = plan.material.code[0:maxletters]
    return pname + "\n" + sname + "\n" + code
