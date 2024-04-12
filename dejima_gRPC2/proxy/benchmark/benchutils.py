import string
import random
from dejima import utils

# generate random string with length n
def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


# zipf generator
# generate integers between [1, n] with zipf distribution

# n is the number of items
# theta (where 0 < theta < 1) is the skew parameter
# ex) if theta = 0.01, uniform distribution: weights = 1/n, 1/n, 1/n, ..., 1/n
# ex) if theta = 0.99, skewed distribution: weights = 1, 1/2, 1/3, ..., 1/n

# refer "Quickly generating billion-record synthetic databases"
# https://dl.acm.org/doi/pdf/10.1145/191839.191886
class ZipfGenerator:
    def __init__(self, n, theta):
        self.n = n
        self.theta = theta
        self.alpha = 1 / (1-theta)
        self.zetan = self.zeta(n, theta)
        self.eta = (1 - pow(2.0/n, 1-theta)) / (1 - self.zeta(2, theta) / self.zetan)

    def __next__(self):
        u = random.random()
        uz = u * self.zetan
        if uz < 1:
            return 1
        elif uz < 1 + pow(0.5, self.theta):
            return 2
        else:
            return 1 + int(self.n * pow(self.eta * u - self.eta + 1, self.alpha))

    def zeta(self, n, theta):
        sum = 0
        for i in range(1,n+1):
            sum += 1 / pow(i, theta)
        return sum


# divide items with item_size into batches
def divide_into_batch(item_size, batch_size, offset=0):
    batch_offset_list = list(range(offset, item_size+offset, batch_size))
    batch_size_list = [batch_size] * (item_size // batch_size)
    if item_size % batch_size:
        batch_size_list += [item_size % batch_size]
    return batch_offset_list, batch_size_list

# divide items with N size into K, and select item size of k
def divide_into_k(N, K, k):
    k_divider = utils.BaseDivider(N, K)
    k_size = k_divider.get_range_size(k)
    return k_size
