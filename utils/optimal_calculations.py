def get_min_amount_to_cps(cps):
    optimal = cps*1800/0.15*7
    return optimal


def get_best_value_product(product_list):
    best_value = 0
    best_ind = 0
    for ind in range(len(product_list)):
        if product_list[ind].cps / product_list[ind].cost > best_value:
            best_value = product_list[ind].cps / product_list[ind].cost
            best_ind = ind
    return product_list[best_ind]


def calculate_min_value_for_purchase(current_cps, purchase_cost):
    return purchase_cost + get_min_amount_to_cps(current_cps)


if __name__ == "__main__":
    pass
