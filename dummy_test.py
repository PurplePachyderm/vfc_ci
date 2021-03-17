# Emulates tests results generation for experimentations purpose

import numpy as np
import time
import calendar


# Samples are drawn from a normal distribution and saved in a file named
# after the current timestamp

mu, sigma = 0, 1
samples = np.random.normal(mu, sigma, 20)

timestamp = str(calendar.timegm(time.gmtime()))

np.savetxt(timestamp + ".vfc.txt", samples, delimiter='.', newline='\n')
