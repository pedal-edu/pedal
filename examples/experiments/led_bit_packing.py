# 4 bits, 25 nibbles

def pack(bit_string):
    result = 0
    for i, c in enumerate(bit_string):
        result = result | int(c) << WIDTH*i
    return result

WIDTH = 4
MASK_4_DIGITS = 15

def unpack(value):
    for i in range(25):
        yield value & MASK_4_DIGITS
        value >>= WIDTH

def render(led_str):
    print("\n".join(led_str[y*5:5*y+5] for y in range(5)))

#original = "99010"+"00000"+"09900"+"90009"+"99990"
original = "99999"
led_integer = sum(int(c) * 10**i for i, c in enumerate(original))
print("LED INTEGER:", led_integer)
print("LED INTEGER BIN:", bin(led_integer))
render(original)
led = pack(original)
print(led)
print(bin(led), len(bin(led)))
back = list(unpack(led))
print(back)
render("".join(map(str, back)))
print(led.bit_length())

import sys
print("String", sys.getsizeof(original))
print("Bit packed integer", sys.getsizeof(led))
print("Simple integer", sys.getsizeof(led_integer))