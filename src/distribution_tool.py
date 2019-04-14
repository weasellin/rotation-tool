from itertools import product

from pprint import pprint

search_range = 0.4

ROTATION_LEN = 5

##################
# Ragular Config #
##################

# PROD_COUNTS = (63, 10, 11, 1, 1)
# PROD_ITEM_COUNTS = (200, 160, 100, 160, 100)
#
# STORE_COUNTS = (2, 6, 9)
# STORE_ROTATION_COUNTS = (182, 182, 184)
#
# PROD_STORE_FLAGS = (
#     (1, 1, 1, 0, 0),
#     (1, 1, 1, 0, 0),
#     (1, 1, 1, 1, 1),
# )

# Result
# =======================================
# store group: (2, 6, 5, 4)
# product group: (39, 24, 10, 11, 1, 1)
# store item counts
# ((14, 10, 8, 4, 0, 0),
#  (13, 9, 11, 7, 0, 0),
#  (10, 14, 10, 6, 16, 12),
#  (11, 14, 7, 5, 20, 10))


####################
# Breakfast Config #
####################

PROD_COUNTS = (59, 10, 11, 1, 1)
PROD_ITEM_COUNTS = (200, 40, 100, 40, 100)

STORE_COUNTS = (2, 6, 9)
STORE_ROTATION_COUNTS = (159, 158, 158)

PROD_STORE_FLAGS = (
    (1, 1, 1, 0, 0),
    (1, 1, 1, 0, 0),
    (1, 1, 1, 1, 1),
)

# Result
# =======================================
# store group: (2, 6, 5, 4)
# product group: (38, 21, 10, 11, 1, 1)
# store item counts
# ((9, 17, 3, 6, 0, 0),
#  (13, 10, 2, 6, 0, 0),
#  (12, 10, 2, 8, 4, 12),
#  (11, 14, 3, 3, 5, 10))


def assert_config():
    prod_item_count = sum(x * y for x, y in zip(PROD_COUNTS, PROD_ITEM_COUNTS))
    store_rotation_count = sum(x * y for x, y in zip(STORE_COUNTS, STORE_ROTATION_COUNTS))
    assert prod_item_count == store_rotation_count * ROTATION_LEN


def product_group_split(split_group, split_num):
    prod_counts = list(PROD_COUNTS)
    item_counts = list(PROD_ITEM_COUNTS)
    prod_counts.insert(split_group + 1, split_num)
    prod_counts[split_group] = prod_counts[split_group] - split_num
    item_counts.insert(split_group + 1, item_counts[split_group])
    return tuple(prod_counts), tuple(item_counts)


def store_group_split(split_group, split_num):
    store_counts = list(STORE_COUNTS)
    rotation_counts = list(STORE_ROTATION_COUNTS)
    store_counts.insert(split_group + 1, split_num)
    store_counts[split_group] = store_counts[split_group] - split_num
    rotation_counts.insert(split_group + 1, rotation_counts[split_group])
    return tuple(store_counts), tuple(rotation_counts)

def prod_store_flag_split(prod_split_group, store_split_group):
    ps_flags = []
    for s, ps_flag in enumerate(PROD_STORE_FLAGS):
        ps_flag = list(ps_flag)
        ps_flag.insert(prod_split_group + 1, ps_flag[prod_split_group])
        ps_flags.append(tuple(ps_flag))
        if s == store_split_group:
            ps_flags.append(tuple(ps_flag))
    return tuple(ps_flags)


def get_store_prod_item_ranges(pg_flags, prod_item_counts, store_counts, store_group_id):
    store_prod_item_ranges = []
    for p, item_count in enumerate(prod_item_counts):
        if pg_flags[store_group_id][p]:
            store_count = sum(x * y[p] for x, y in zip(store_counts, pg_flags))
            r = tuple(range(int(item_count / store_count * (1.0 - search_range)),
                            int(item_count / store_count * (1.0 + search_range)) + 1))
        else:
            r = tuple([0])
        store_prod_item_ranges.append(r)
    return tuple(store_prod_item_ranges)

for j in range(9 // 2 + 1):
    for i in range(63 + 1):
        print(f'{i}, {j}')
        prod_counts, prod_item_counts = product_group_split(0, i)
        store_counts, rotation_counts = store_group_split(2, j)
        pg_flags = prod_store_flag_split(0, 2)
        store_group_count = len(store_counts)

        store_item_count_list = tuple([] for s in range(store_group_count))

        for store_group in range(len(store_counts)):
            rotation_count = rotation_counts[store_group]
            r = get_store_prod_item_ranges(pg_flags, prod_item_counts, store_counts, store_group)
            for item_counts in product(*r):
                if sum(x * y for x, y in zip(prod_counts, item_counts)) == rotation_count * ROTATION_LEN:
                    store_item_count_list[store_group].append(item_counts)

        for store_item_counts in product(*store_item_count_list):
            is_matched = True
            for prod_group_id in range(len(prod_counts)):
                if sum(x * y[prod_group_id] for x, y in zip(store_counts, store_item_counts)) != prod_item_counts[prod_group_id]:
                    is_matched = False
                    break
            if is_matched:
                print('Match found!')
                print(f'store group: {store_counts}')
                print(f'product group: {prod_counts}')
                print('store item counts')
                pprint(store_item_counts)

