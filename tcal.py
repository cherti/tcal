#!/usr/bin/env python3

import datetime, calendar

m = 12

def print_month(y, m):
	cal = calendar.Calendar()
	print("Mo Di Mi Do Fr Sa So")
	line = ""
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
			line = ""




if __name__ == "__main__":
	print_month(2016, 12)
