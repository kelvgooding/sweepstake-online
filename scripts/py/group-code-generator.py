import random
import string

gc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

print(gc)