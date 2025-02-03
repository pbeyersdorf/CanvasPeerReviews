import sys, os
from cpr import *

students, graded_assignments, lastAssignment = initialize()

DATADIRECTORY=os.path.dirname(os.path.realpath(__file__)) + "/Data/"
fileName=DATADIRECTORY + "gradesheet.csv"
exportGrades(fileName=fileName)
if confirm("Edit the grades in the Data folder, and then click OK.  You will be prompted for an assignment to post them to (this part is untested)."):
	postFromCSV(fileName)
print("Done!")