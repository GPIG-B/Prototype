from typing import Any, List
import numpy as np
import pandas as pd  # type: ignore


COOLDOWN = 100
cooldowns = {}


def get_fault_alerts(readings: Any, threshold: float = -0.08,
                     width: float = 0.05) -> List[str]:
    # Create a DataFrame from the readings
    wtss = [{**wt, 'ticks': r['ticks']} for r in readings for wt in r['wts']]
    df = pd.DataFrame(wtss).sort_values('ticks')
    if len(df.ticks.unique()) < 25:
        return []
    # Get the fault probability based on the power readings
    dfprob = _get_fprob(df, 'power', threshold, width)
    # Merge the probabilities into the DataFrame
    dft = df.merge(dfprob, on='wt_id')
    dft = dft.rename(columns={'smooth': 'power_fprob'})
    # Threshold the probabilities to get final predictions
    dft['pred'] = dft['power_fprob'] > 0.5
    # Drop rows with na values introduced by the moving average.
    dft = dft.dropna(axis=0)
    # Get the rows from the most recent tick
    last = dft[dft.ticks == dft.ticks.max()]
    # Keep only the rows where a fault was predicted
    last = last[last.pred]
    last_ids = list(last.wt_id)
    alerts = []
    for wt_id in last_ids:
        if wt_id in cooldowns:
            continue
        alerts.append(wt_id)
        cooldowns[wt_id] = COOLDOWN
    for k in list(cooldowns.keys()):
        cooldowns[k] -= 1
        if cooldowns[k] < 0:
            del cooldowns[k]
    return alerts


def _get_fprob(df: pd.DataFrame, col: str, threshold: float = -0.05,
               width: float = 0.05) -> pd.DataFrame:
    # Compute the 75th percentile of all WTs for each tick. This becomes the
    # reference for further comparisions.
    dft = df.groupby('ticks')
    reference = dft[col].quantile(0.75)
    # Add the reference to each row.
    df = df.merge(reference, how='left', on='ticks',
                  suffixes=('', '_reference'))
    # Compute the normalised deviation of each row from the reference.
    df[f'{col}_dev'] = (df[col] - df[f'{col}_reference']) \
                       / df[f'{col}_reference']
    # Compute the probability of a fault based on the deviation.
    df[f'{col}_fprob'] = 1 / (1 + np.exp((df[f'{col}_dev'] - threshold) \
                                         / width))
    # Average the probability over multiple ticks to mitigate the impact of
    # noise.
    df['smooth'] = (df
                    .groupby('wt_id')
                    [f'{col}_fprob']
                    # See: https://github.com/pandas-dev/pandas/issues/38523
                    .apply(lambda x: x.rolling(30, min_periods=20).mean()))
    return df[['wt_id', 'smooth']]
