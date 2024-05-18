import mytools

temp_f=mytools.c_to_f(32)
print(f"華氏温度 = {temp_f:.2f}")

bmi=mytools.calc_bmi(170,80)
eval=mytools.eval_bmi(bmi)
print(f"bmi = {bmi:.2f}")
print(f"評估結果 : {eval}")
