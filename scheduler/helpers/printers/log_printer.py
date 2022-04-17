def default_log(*inputs, verbose: int = 0, **kwargs) -> None:
    # TODO: cambiar el log por un decorador mas chingon. Checar la implementacion en hnkn-orz
    # TODO: Definir una definicion para los niveles de verbose
    if verbose == 0:
        return
    elif verbose == 1:
        print(*inputs, **kwargs)
    else:
        raise NotImplementedError(f"verbose {verbose} is not implemented")
