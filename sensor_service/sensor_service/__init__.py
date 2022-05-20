from typing import Any
import pandas as pd  # type: ignore


def process(readings: Any) -> None:
    wtss = [{**wt, 'ticks': r['ticks']} for r in readings for wt in r['wts']]
    df = pd.DataFrame(wtss)
