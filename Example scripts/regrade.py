import sys, os
sys.path.insert(0, "/Volumes/T7/peteman/Documents/GitHub/CanvasPeerReviews")
sys.path.insert(0, "/Users/peteman/Documents/GitHub/CanvasPeerReviews")
from cpr import *

#################  course info  #################
students, graded_assignments, lastAssignment = initialize()

#################  Get relevant parameters assignment  #################
params=getParameters()

# Get creations and reviews
#getStudentWork()
regrade()
print("Done!")