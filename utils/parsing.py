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

    return multiplier


def parse_product_cps(hover_string):
    interesting_string = hover_string.split("\\n")[0]
    start_ind = interesting_string.find("produces") + len("produces")
    end_ind = interesting_string.find("cookies")
    return interesting_string[start_ind+1: end_ind-1]


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
