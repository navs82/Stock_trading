import datetime

from zipline.data.bundles import register

from zipline.data.bundles.google import google_equities

equities2 = {
    'AAPL',
}

start = datetime.datetime(2010, 1, 1)
end = datetime.datetime(2017, 1, 27)

register(
    'my-google-equities-bundle',  # name this whatever you like
    google_equities(equities2),
)


