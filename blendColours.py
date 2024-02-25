from math import *
from sys import *

a = int(argv[1], 16) / 255
b = int(argv[2], 16) / 255

result = sqrt(0.5 * a * a + 0.5 * b * b)

print(hex(int(result*255)))
