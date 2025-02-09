#################  Set up where to the environment  #################
from path_info import *
from cpr import *		# the main module for managing peer reviews

#################  Get the data for the course  #################
students, graded_assignments, lastAssignment = initialize(CANVAS_URL, TOKEN, COURSE_ID, DATADIRECTORY)

users = utilities.course.get_users(enrollment_type=['student'])
from html import escape
fileName=status['dataDir'] +  "roster.html"
f = open(fileName, "w")
f.write("<html><head><title>Roster for " + utilities.course.name + " </title><style>\n")
f.write("a {text-decoration:none}\n")
f.write("</style><meta http-equiv='Content-Type' content='text/html; charset=utf-16'></head><body>\n")
f.write("<h3>Roster for  "+utilities.course.name +"</h3>\n<table>\n")

for u in users:
	name=u.name
	url= u.get_profile()['avatar_url']
	printLine("getting avatar for " + name, False)
	f.write("<tr><td>" + " <img src='" +url+ "'>\n" + name +"</td></tr>")
f.write("</table></body></html>\n")
f.close()
subprocess.call(('open', fileName))
