import sys
import json
import csv
import collections
import math

from numpy.random import choice
from pprint import pprint

Product = collections.namedtuple('Product', 'priority, remain, weight')

ROTATION_LEN = 5
DEBUG = False


def load_profile(profile):
    with open('data/profile.list') as prof_json:
        prof = json.load(prof_json)
        profile['prod_groups'] = prof[profile['name']]


def load_product(profile):
    with open('data/product_list.csv') as prod_csv:
        prod = csv.DictReader(prod_csv)
        prod_list = filter(lambda r: r['product_group'] in profile['prod_groups'], prod)
        profile['prod_list'] = {}
        profile['prod_pool'] = {}
        for p in prod_list:
            id = int(p['id'])
            profile['prod_list'][id] = p
            profile['prod_pool'][id] = {
                    'priority': int(p['priority']),
                    'remain':   int(profile['prod_groups'][p['product_group']]),
                    'weight':   0.01
                }

def reset_product(profile):
    profile['rotation'] = []
    for (prod_id, prod) in profile['prod_list'].items():
        profile['prod_pool'][prod_id]['remain'] = int(profile['prod_groups'][prod['product_group']])
        profile['prod_pool'][prod_id]['weight'] = 0.01


def load_conflict(profile):
    prod_set = set(profile['prod_list'].keys())
    with open('data/conflict.list') as conflict_json:
        conflict_list = json.load(conflict_json)
        profile['conflict_list'] = []
        for conflict in conflict_list:
            if len(prod_set & set(conflict)) > 1:
                profile['conflict_list'].append(set(conflict))


def save_profile_rotation(profile):
    with open('output/%s.csv' % profile['name'], 'w') as rotation_csv:
        writer = csv.writer(rotation_csv)
        for r in profile['rotations']:
            row = []
            for p in r:
                row.append(str(p))
                row.append(profile['prod_list'][p]['name'])
            writer.writerow(row)


def load_profile_rotation(profile):
    with open('output/%s.csv' % profile['name'], 'r') as rotation_csv:
        profile['rotations'] = []
        reader = csv.reader(rotation_csv)
        for r in reader:
            profile['rotations'].append(list(map(lambda i: r[i], range(0, 9, 2))))


def draw_rotation_order(profile, order):
    # update weight
    id_list = []
    weight_list = []
    rotation_count = len(profile['rotations'])
    for (prod_id, prod) in profile['prod_pool'].items():
        ## nmc_d_rule
        if order < 1 and prod['priority'] > 6:
            continue
        if order < 3 and prod['priority'] > 8:
            continue
        # if order < 4 and prod['priority'] > 8:
        #     continue
        if order > 3 and prod['priority'] < 9:
            continue
        ## nmc_d_rule
        #if order < 4 and prod['priority'] > 6:
        #    continue
        ## nmc_b_A_rule
        #if order < 2 and prod['priority'] > 5 and rotation_count < 80:
        #    continue
        # nmc_b_BC_rule
        #if order < 2 and prod['priority'] > 5 and rotation_count < 25:
        #    continue
        # nmc_b_rule
        #if order < 4 and prod['priority'] > 7:
        #    continue
        if prod['remain'] > 0 and prod['weight'] > 0.0:
            id_list.append(prod_id)
            weight_list.append(prod['weight'] * prod['remain'] ** 5)

    #pprint(profile['prod_pool'])
    weight_sum = sum(weight_list)
    if weight_sum <= 0:
        #pprint(profile['prod_pool'])
        #pprint(profile['conflict_list'])
        raise Exception('END')
    weight_list = list(map(lambda w: w/weight_sum, weight_list))

    id_draw = choice(id_list, p=weight_list)
    pr_draw = profile['prod_pool'][id_draw]['priority']

    profile['prod_pool'][id_draw]['weight'] = 0.0
    profile['prod_pool'][id_draw]['remain'] -= 1

    for c in profile['conflict_list']:
        if id_draw in c:
            for p in c:
                profile['prod_pool'][p]['weight'] = 0.0

    for p, v in profile['prod_pool'].items():
        if v['priority'] < pr_draw:
            v['weight'] = 0.0
    # for p, v in filter(lambda p, v: v['priority'] < pr_draw, profile['prod_pool'].items()):
    #     v['weight'] = 0.0

    return id_draw


def print_product(prod):
    print('%s, %s, %s' % (prod['id'], prod['name'], prod['priority']))
    return

def draw_rotation(profile):
    rotation = []
    for (prod_id, prod) in profile['prod_pool'].items():
        prod['weight'] = math.exp(-0.3 * prod['priority'])

    if DEBUG:
        print('rotation %s:' % len(profile['rotations']))
    for i in range(ROTATION_LEN):
        id_draw = draw_rotation_order(profile, i)
        rotation.append(id_draw)
        if DEBUG:
            print_product(profile['prod_list'][id_draw])
    profile['rotations'].append(rotation)


def draw(profile, max_rotation):
    # print(profile['prod_pool'].items())
    total_product_num = int(sum(p['remain'] for k, p in profile['prod_pool'].items()))
    # total_product_num = sum(map(lambda k, p: p['remain'], profile['prod_pool'].items()))
    total_rotation_num = int(total_product_num / ROTATION_LEN)
    print('total_rotation_num %s' % total_rotation_num)

    profile['rotations'] = []
    try:
        for i in range(total_rotation_num):
            draw_rotation(profile)
    except KeyboardInterrupt:
        raise
    except:
        print('rotation %s:' % len(profile['rotations']))
        if i > max_rotation[-1]:
            max_rotation.append(i)
            pprint(profile['prod_pool'])
        elif DEBUG:
            pprint(profile['prod_pool'])
        reset_product(profile)
        return None

    return True


def generate_rotation(profile):
    trial = 2000
    max_rotation = [100]
    if DEBUG:
        trial = 1
    for i in range(trial):
        print('Trial %s' % i)
        if draw(profile, max_rotation):
            save_profile_rotation(profile)
            break


def check_rotation(profile):
    load_profile_rotation(profile)

    has_nb = False
    has_np = False
    has_nc = False
    has_ns = False

    order = {}

    for r in profile['rotations']:
        nb = True
        np = True
        nc = True
        ns = True
        for i, p in enumerate(r):
            if p not in order:
                order[p] = set()
            order[p].add(i)
            protein = profile['prod_list'][int(p)]['protein']
            if not protein:
                continue
            elif protein == 'beef':
                nb = False
            elif protein == 'pork':
                np = False
            elif protein == 'chicken':
                nc = False
            elif protein == 'seafood':
                ns = False
        has_nb = has_nb or nb
        has_np = has_np or np
        has_nc = has_nc or nc
        has_ns = has_ns or ns
        # pprint(order)
        # print '%s, %s, %s, %s' % (nb, np, nc, ns)
    print('%s, %s, %s, %s' % (has_nb, has_np, has_nc, has_ns))
    single_order = {p: i for p, i in order.items() if len(i) == 1}
    pprint(single_order)


if __name__ == '__main__':
    #prod_groups = load_profile('nmac_b_A_prod_group')
    #prod_groups = load_profile('mac_b_B_prod_group')
    #prod_groups = load_profile('mac_d_A_prod_group')
    #prod_groups = load_profile('mac_d_B_prod_group')
    #prod_groups = load_profile('nmac_b_C_prod_group')
    #prod_groups = load_profile('mac_d_B_prod_group')

    profile = {'name': sys.argv[1]}
    load_profile(profile)
    load_product(profile)
    load_conflict(profile)

    # rotation generate
    # generate_rotation(profile)

    # rotation check
    check_rotation(profile)

