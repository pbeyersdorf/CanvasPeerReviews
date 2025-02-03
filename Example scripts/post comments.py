import sys, os
from cpr import *

students, graded_assignments, lastAssignment = initialize()

#Note names can be in either "Sammy Spartan" or "Spartan, Sammy" format
fileName=input("Choose a CSV file with a column for student names, an optional colum for student grades, and an optional colun for comments: ").strip().replace("\\","")
postFromCSV(fileName)