
# TODO: mover a la carpeta de los generadores y crear su clase particular
def batch_mutation_printer(model: str, a: int, b: int, mode: str = "create"):
    for i in range(a, b+1):
        print(f"m{i}: {mode}{model}(id:{i}){{successful messages{{field message}}}}")


if __name__ == "__main__":
    batch_mutation_printer("Process", 65, 80, "delete")
