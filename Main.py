from Extract import extract
from Transform import transform
from Load import load_price_data

"""
prices = extract([208816533, 207838586, 439991267, 158878388, 211305205, 303748673])
"""
prices = {
    "article": [208816533, 207838586, 439991267, 158878388, 211305205, 303748673],
    "price": [
        146.0,
        9349.0,
        30800.0,
        517.0,
        1860.0,
        13563.0,
    ],
}

csv_path = transform(prices)
load_price_data(csv_path)
