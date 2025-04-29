# dice.py
import random
import math

def roll_d6(num=1):
    return [random.randint(1, 6) for _ in range(num)]

def roll_nd6(num=1):
    return sum(roll_d6(num))

def roll_d3(num=1):
    return [math.ceil(random.randint(1, 6) / 2) for _ in range(num)]