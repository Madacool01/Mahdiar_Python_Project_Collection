from math import sqrt, inf
from special_functions import split_at_first

user_input = input("Calculation: ")
operators = ["+", "-", "*", "/"]

def addition(n):
    add = 0
    for i in n:
        add += float(i)
    return add

def subtraction(n):
    sub = float(n[0])
    for i in n[1:]:
        sub -= float(i)
    return sub

def multiplication(n):
    mult = n[0]
    for i in n[1:]:

        mult = float(mult) * float(i)
    return mult

def division(n):
    try:
        div = n[0]
        for i in n[1:]:

            div = float(div) / float(i)
        return div
    except ZeroDivisionError:
        return "DIVISION BY 0"
    
def positioning(n, operator):
    n_new = n
    for number in n_new[1:]:
        position = (n_new[1:]).find(number)
        position += 1
        operator_position = n_new.find(operator)
        if number == operator:
            continue
        elif number in operators:
            if n_new[position-1] == operator:
                continue
            elif position < operator_position:
                n_new = n_new[position+1:]
            else:
                n_new = n_new[:position]

    operator_split = split_at_first(n_new, operator)
    return operator_split, n_new
       
def evaluate(n, operator):
    operator_split, n_new = positioning(n, operator)
    if operator == "/":
        result = division(operator_split)
    elif operator == "*":
        result = multiplication(operator_split)
    elif operator == "-":
        result = subtraction(operator_split)
    elif operator == "+":
        result = addition(operator_split)

    n = n.replace(n_new, str(result))
    return n
    
def evaluate_brackets(n):
    for check in n:
        if check == ")":
            closed = n.find(")")
            try:
                if n[closed+1] == "(":
                    n = f"{n[:closed+1]}*{n[closed+1:]}"
            except IndexError:
                break
    n_bracket = n
    while "(" in n_bracket:
        for bracket in n_bracket:
            if bracket == "(":
                first_bracket = n_bracket.rfind(bracket)
                last_bracket = (n_bracket[first_bracket:]).find(")")
                last_bracket += first_bracket
                n_bracket = n_bracket[first_bracket+1:last_bracket]
                break
    n_result = n_bracket
    while True:
        if "/" in n_result:
            n_result = evaluate(n_result, "/")
        elif "*" in n_result:
            n_result = evaluate(n_result, "*")
        elif "-" in n_result[1:]:
            n_result = evaluate(n_result, "-")
        elif "+" in n_result:
            n_result = evaluate(n_result, "+")
        else:
            n = n.replace(f"({n_bracket})", str(n_result))
            return n


def core(n):
    while True:
        if "(" in n:
            n = evaluate_brackets(n)
        elif "/" in n:
            n = evaluate(n, "/")
        elif "*" in n:
            n = evaluate(n, "*")
        elif "-" in n[1:]:
            n = evaluate(n, "-")
        elif "+" in n[1:]:
            n = evaluate(n, "+")
        else:
            return n
        
print(core(user_input))
# print(evaluate_brackets(user_input))