import sys, os
sys.path.insert(0, "/Volumes/T7/peteman/Documents/GitHub/CanvasPeerReviews")
sys.path.insert(0, "/Users/peteman/Documents/GitHub/CanvasPeerReviews")
from CanvasPeerReviews import *

students, graded_assignments, lastAssignment = initialize()

#Note names can be in either "Sammy Spartan" or "Spartan, Sammy" format
fileName=input("Choose a CSV file with a column for student names, an optional colum for student grades, and an optional colun for comments: ").strip().replace("\\","")
postFromCSV(fileName)