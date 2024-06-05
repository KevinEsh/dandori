from gstorm import GraphQLType
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np


def normalize_data(dataframe: pd.DataFrame, cols: List[str]) -> None:
    """Normalize incoming data in given columns

    Args:
        dataframe (pd.DataFrame): DataFrame in which the normalization will take place
        cols (List[str]): List of columns names in DataFrame to be normalized
    """
    selected = dataframe[cols]
    dataframe[cols] = (selected-selected.min())/(selected.max()-selected.min())


def weighted_priorities(dataframe: pd.DataFrame,
                        weights: float, prange: Tuple[int] = (0, 100)) -> pd.DataFrame:
    """Calculate weighted sum and sort by score

    Args:
        dataframe (pd.DataFrame): DataFrame with orders that can be performed and their possible stopped resources
        priorities_weight (dict, optional): Assignation weights to each relevan component. Defaults to {'priority':0.5, 'HotOrder':0.3, 'OrderEnd':0.1, 'ExistStoppedResources':0.1}.

    Returns:
        pd.DataFrame: DataFrame ordered by Priority, HotOrder and score to be fulfilled ASAP
    """
    cols = list(weights.keys())
    vals = weights.values()
    datetime_to_int(dataframe)
    normalize_data(dataframe, cols)
    # Calculating weighted sum
    w = pd.Series(vals, index=cols)
    temp = dataframe.multiply(w, axis="columns")
    dataframe["score"] = ((prange[1] - prange[0]) *
                          temp.sum(axis="columns") + prange[0]).astype(int)
    dataframe[dataframe["score"] > prange[1]] = prange[1]
    dataframe[dataframe["score"] < prange[0]] = prange[0]
    dataframe.sort_values(by="score", inplace=True, ascending=False)
    return dataframe


def parse_to_dataframe(demand: GraphQLType) -> pd.DataFrame:
    """Generates pandas data frame from class.

    Args:
        demand (GraphQLType): Demand model

    Returns:
        pd.DataFrame: Demand model with attributes as columns.
    """
    return pd.DataFrame([order.__dict__ for order in demand.orders])


def get_scores(dataframe: pd.DataFrame) -> Dict[int, int]:
    """Gets score column from data frame as dict.

    Args:
        dataframe (pd.DataFrame): Weighted priorities-like data frame.

    Returns:
        Dict[int, int]: Index as keys and priority score as values.
    """
    return dataframe.to_dict().get("score")


def datetime_to_int(dataframe: pd.DataFrame) -> None:
    """Parses scheduler's models datetime attributes as int (startAt, endAt,
    insertedAt, updatedAt)

    Args:
        dataframe (pd.DataFrame): Data frame parsed scheduler model.
    """
    fields = ["startAt", "endAt", "insertedAt", "updatedAt"]
    dataframe[fields] = dataframe[fields].astype(int)


if __name__ == "__main__":
    n = 10
    dataframe = pd.DataFrame({
        "A": np.random.randint(0, 10, n),
        "B": np.random.randint(0, 10, n),
        "C": np.random.randint(0, 10, n),
        "D": np.random.randint(0, 10, n),
    })

    weighted_priorities(dataframe, weights={"A": 0.1, "B": 0.9})
    print(dataframe)
    weighted_priorities(dataframe, weights={"A": 0.1, "B": 0.6, "C": 0.3})
    print(dataframe)
    print(dataframe["score"])
    s = get_scores(dataframe)
    print(s)
