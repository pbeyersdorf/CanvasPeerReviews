import sys, os
from cpr import *

#################  course info  #################
students, graded_assignments, lastAssignment = initialize()

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
#getStudentWork()
regrade()
print("Done!")