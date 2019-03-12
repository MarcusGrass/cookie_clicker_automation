def translate_text_to_number(number, text):
    number = float(number)
    multiplier = translate_word_to_multiplier(text)
    return number*multiplier


def translate_word_to_multiplier(text):
    multiplier = 1
    if text == "million":
        multiplier = 1e+6
    elif text == "billion":
        multiplier = 1e+9
    elif text == "trillion":
        multiplier = 1e+12
    elif text == "quadrillion":
        multiplier = 1e+15
    elif text == "quintillion":
        multiplier = 1e+18
    elif text == "sextillion":
        multiplier = 1e+21
    elif text == "septillion":
        multiplier = 1e+24
    elif text == "octillion":
        multiplier = 1e+27
    elif text == "nonillion":
        multiplier = 1e+30
    elif text == "decillion":
        multiplier = 1e+33
    elif text == "undecillion":
        multiplier = 1e+36
    elif text == "duodecillion":
        multiplier = 1e+39
    elif text == "tredecillion":
        multiplier = 1e+42
    elif text == "quattuordecillion":
        multiplier = 1e+45
    elif text == "quindecillion":
        multiplier = 1e+48
    elif text == "sexdecillion":
        multiplier = 1e+51

    return multiplier


def parse_product_cost(cost_string):
    try:
        raw_cost_list = cost_string.split(" ")
        num_cost = translate_text_to_number(raw_cost_list[0], raw_cost_list[1])
    except IndexError:
        num_cost = float(cost_string.replace(",", "").replace(" ", ""))
    return num_cost


def parse_product_cps(cps_string):
    reproduced = repr(cps_string)
    interesting_string = reproduced.split("\\n")[0]
    start_ind = interesting_string.find("produces") + len("produces")
    end_ind = interesting_string.find("cookies")
    cps = interesting_string[start_ind+1: end_ind-1]
    split_cps = cps.split(" ")
    num_cps = translate_text_to_number(split_cps[0], split_cps[1])
    return num_cps


def parse_product_name(name_string):
    reproduced = repr(name_string)
    reproduced = reproduced.replace("'", "")
    reproduced = reproduced.lower()
    return reproduced


def parse_upgrade_description(description_string):
    cleaner = repr(description_string).replace("'", "").split("\\n")[0].lower().replace('"', "")
    if "twice" in cleaner:
        end_index = cleaner.find("are") - 1
        return cleaner[:end_index]
    elif "cookie production multiplier" in cleaner:
        start_index = cleaner.find("+") + 1
        end_index = cleaner.find(".") - 1
        return float("0.0" + cleaner[start_index: end_index])
    elif "the more milk you have" in cleaner:
        return "kitten"
    else:
        return "unknown upgrade"


def parse_mana_string(mana_string):
    return int(mana_string[0])


def parse_buff_text(buff_text):
    if "Frenzy" in buff_text and "x7" in buff_text:
        return "frenzy"
    elif "click frenzy" in buff_text.lower():
        return "click frenzy"
    elif "clot" in buff_text.lower():
        return "clot"
    else:
        return "unknown buff"
