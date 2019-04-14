
import collections
import csv
import json
from pprint import pprint

PRODUCT_COUNT = 145
ROTATION_LEN = 5

STORE_GROUPS = {
    'L1A_Breakfast': 2,
    'L1B_Breakfast': 6,
    'L3A_Breakfast': 5,
    'L3B_Breakfast': 4,
    'L1A_Regular': 2,
    'L1B_Regular': 6,
    'L3A_Regular': 5,
    'L3B_Regular': 4,
}

def save_order(order):
    with open('output/order.csv', 'w') as order_csv:
        writer = csv.writer(order_csv)
        for p in range(1, PRODUCT_COUNT + 1):
            row = [order[str(p)][r] for r in range(ROTATION_LEN)]
            writer.writerow(row)


def check_all_rotation():
    order = {}
    for profile_name, store_count in STORE_GROUPS.items():
        with open('output/%s.csv' % profile_name, 'r') as rotation_csv:
            reader = csv.reader(rotation_csv)
            for r in reader:
                rotation = [r[i] for i in range(0, 9, 2)]
                for i, p in enumerate(rotation):
                    if p not in order:
                        order[p] = collections.Counter()
                    order[p][i] += store_count
    single_order = {p: i for p, i in order.items() if len(i) == 1}
    pprint(single_order)

    save_order(order)


if __name__ == '__main__':
    check_all_rotation()


