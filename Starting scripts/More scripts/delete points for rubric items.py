assignment=chooseAssignment()
for criteria in assignment.rubric:
	if confirm(f"Ok to delete information on {criteria['description']} from {assignment.name}"):
		del params.multiplier[criteria['id']]
saveData()