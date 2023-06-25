from itertools import islice
import random


for i in range(2, 20):
    random_data = random.choice([True, False])
    if random_data:
        slice = next(islice(range(10), i, i+1))
    else:
        slice = next(islice(range(10), i-1, i))
    print(slice)
    print(random_data)

