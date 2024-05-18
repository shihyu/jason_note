# bmi.py

def calc_bmi(height, weight):
    height=height/100
    return weight / height**2

def eval_bmi(bmi):
    if 18.5 <= bmi <= 24.9:
        return '健康'
    
    if bmi >= 25:
        return '過重'
    
    return '過輕'
