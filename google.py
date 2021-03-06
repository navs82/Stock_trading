import os

import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
import requests

from zipline.utils.calendars import register_calendar_alias
from zipline.utils.cli import maybe_show_progress
from .core import register
import pdb



def _cachpath(symbol, type_):
    return '-'.join((symbol.replace(os.path.sep, '_'), type_))


def google_equities(symbols, start=None, end=None):
    """Create a data bundle ingest function from a set of symbols loaded from
    google.

    Parameters
    ----------
    symbols : iterable[str]
        The ticker symbols to load data for.
    start : datetime, optional
        The start date to query for. By default this pulls the full history
        for the calendar.
    end : datetime, optional
        The end date to query for. By default this pulls the full history
        for the calendar.

    Returns
    -------
    ingest : callable
        The bundle ingest function for the given set of symbols.

    Examples
    --------
    This code should be added to ~/.zipline/extension.py

    .. code-block:: python

       from zipline.data.bundles import google_equities, register

       symbols = (
           'AAPL',
           'IBM',
           'MSFT',
       )
       register('my_bundle', google_equities(symbols))

    Notes
    -----
    The sids for each symbol will be the index into the symbols sequence.
    """

    print(symbols)
    print(start)
    print(end)

    # strict this in memory so that we can reiterate over it
    symbols = tuple(symbols)

    def ingest(environ,
               asset_db_writer,
               minute_bar_writer,  # unused
               daily_bar_writer,
               adjustment_writer,
               calendar,
               start_session,
               end_session,
               cache,
               show_progress,
               output_dir,
               # pass these as defaults to make them 'nonlocal' in py2
               start=start,
               end=end):
        if start is None:
            start = start_session
        if end is None:
            end = None
        print(start)
        print(end)
        metadata = pd.DataFrame(np.empty(len(symbols), dtype=[
            ('start_date', 'datetime64[ns]'),
            ('end_date', 'datetime64[ns]'),
            ('auto_close_date', 'datetime64[ns]'),
            ('symbol', 'object'),
        ]))

        def _pricing_iter():
            sid = 0
            pdb.set_trace()
            with maybe_show_progress(
                    symbols,
                    show_progress,
                    label='Downloading Google pricing data: ') as it, \
                    requests.Session() as session:
                for symbol in it:
                    path = _cachpath(symbol, 'ohlcv')
                    try:
                        df = cache[path]
                    except KeyError:
                        df = cache[path] = DataReader(
                            symbol,
                            'google',
                            start,
                            end,
                            session=session,
                        ).sort_index()

                    # the start date is the date of the first trade and
                    # the end date is the date of the last trade
                    start_date = df.index[0]
                    end_date = df.index[-1]
                    # The auto_close date is the day after the last trade.
                    ac_date = end_date + pd.Timedelta(days=1)
                    metadata.iloc[sid] = start_date, end_date, ac_date, symbol

                    df.rename(
                        columns={
                            'Open': 'open',
                            'High': 'high',
                            'Low': 'low',
                            'Close': 'close',
                            'Volume': 'volume',
                        },
                        inplace=True,
                    )
                    yield sid, df
                    sid += 1

        daily_bar_writer.write(_pricing_iter(), show_progress=show_progress)

        symbol_map = pd.Series(metadata.symbol.index, metadata.symbol)
        asset_db_writer.write(equities=metadata)

        #adjustments = []
        #with maybe_show_progress(
        #        symbols,
        #        show_progress,
        #        label='Downloading Yahoo adjustment data: ') as it, \
        #        requests.Session() as session:
        #    for symbol in it:
        #        path = _cachpath(symbol, 'adjustment')
        #        try:
        #            df = cache[path]
        #        except KeyError:
        #            df = cache[path] = DataReader(
        #                symbol,
        #                'google',
        #                start,
        #                end,
        #                session=session,
        #            ).sort_index()

        #        df['sid'] = symbol_map[symbol]
        #        adjustments.append(df)

        #adj_df = pd.concat(adjustments)
        #adj_df.index.name = 'date'
        #adj_df.reset_index(inplace=True)

        #splits = adj_df[adj_df.action == 'SPLIT']
        #splits = splits.rename(
        #    columns={'value': 'ratio', 'date': 'effective_date'},
        #)
        #splits.drop('action', axis=1, inplace=True)

        #dividends = adj_df[adj_df.action == 'DIVIDEND']
        #dividends = dividends.rename(
        #    columns={'value': 'amount', 'date': 'ex_date'},
        #)
        #dividends.drop('action', axis=1, inplace=True)
        # we do not have this data in the yahoo dataset
        #dividends['record_date'] = pd.NaT
        #dividends['declared_date'] = pd.NaT
        #dividends['pay_date'] = pd.NaT

        #adjustment_writer.write()

    return ingest



# bundle used when creating test data
# register(
#     '.test',
#     google_equities(
#         (
#             'AMD',
#             'CERN',
#             'COST',
#             'DELL',
#             'GPS',
#             'INTC',
#             'MMM',
#             'AAPL',
#             'MSFT',
#         ),
#         pd.Timestamp('2007-01-02', tz='utc'),
#         pd.Timestamp('2017-01-01', tz='utc'),
#     ),
# )

# register_calendar_alias("YAHOO", "NYSE")