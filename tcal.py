#!/usr/bin/env python3

import datetime, calendar

print_weeks = True
m = 12
appointments = {}

def print_month(y, m):
	cal = calendar.Calendar()
	d = datetime.date(y, m, 1)
	monthyearline = d.strftime("%B {}".format(y))
	weekdaysline = "Mo Di Mi Do Fr Sa So"
	if print_weeks:
		weekdaysline = "    " + weekdaysline
		# get week number
		monthstart = datetime.date(y, m, 1)
		weekno = monthstart.isocalendar()[1]
		line = "{:2}  ".format(weekno)
	else:
		line = ""
		weekno = None

	offset_monthyearline = max(int((len(weekdaysline) - len(monthyearline))/2), 0)
	print(offset_monthyearline*" " + monthyearline)

	print(weekdaysline)

	linelength = 0
	for day, weekday in cal.itermonthdays2(y, m):
		if day == 0:
			line += " "*3
		else:
			line += "{:2} ".format(day)

		linelength += 1
		if linelength == 7:
			print(line)
			linelength = 0

			if weekno:
				weekno = (weekno + 1)%52
				line = "{:2}  ".format(weekno)
			else:
				line = ""




if __name__ == "__main__":
	print_month(2016, 12)

