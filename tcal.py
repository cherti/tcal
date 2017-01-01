#!/usr/bin/env python3

import datetime, calendar, os, sys, argparse
from termcolor import colored
from dateutil.relativedelta import relativedelta

appointments = {}
appointmentdaycolor = 'cyan'

today = datetime.date.today()

def errprint(msg, code):
	print(msg, file=sys.stderr)
	exit(code)

parser = argparse.ArgumentParser(description='tcal - terminal calendar')
parser.add_argument('-s', '--store', action='store', dest='appointment_file', type=str, default=os.path.expanduser('~/.tcal-appointments'), help='file storing appointments')
parser.add_argument('-m', '--month', action='store', dest='month', type=int, default=today.month, help='first month to display')
parser.add_argument('-r', '--range', action='store', dest='monthrange', type=int, default=1, help='number of months to display')
parser.add_argument('-y', '--year', action='store', dest='year', type=int, default=today.year, help='year of the first month to display')
parser.add_argument('-w', '--weeks', action='store_true', default=False, dest='print_weeks', help='show weeks when printing calendar')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-n', '--new', action='store_true', default=False, dest='new', help='add new appointment')
group.add_argument('-e', '--edit', action='store_true', default=False, dest='edit', help='edit appointments for specific date')

#args = parser.parse_args(sys.argv[1:])
args = parser.parse_args()



def print_month(y, m):
	cal = calendar.Calendar()
	month_appointment_identifier = []


	d = datetime.date(y, m, 1)
	monthyearline = d.strftime("%B {}".format(y))
	weekdaysline = "Mo Di Mi Do Fr Sa So"
	if args.print_weeks:
		weekdaysline = "    " + weekdaysline
		# get week number
		monthstart = datetime.date(y, m, 1)
		weekno = monthstart.isocalendar()[1]
		line = "{:2}  ".format(weekno)
	else:
		line = ""
		weekno = None

	# compute the offset as half of the whitespaces the weekdaysline is longer than the monthyearline
	offset_monthyearline = max(int((len(weekdaysline) - len(monthyearline))/2), 0)
	print(offset_monthyearline*" " + monthyearline)

	print(weekdaysline)

	linelength = 0
	for day, weekday in cal.itermonthdays2(y, m):
		if day == 0:
			line += " "*4
		else:
			identifier = "{}-{:02}-{:02}".format(y, m, day)
			if identifier in appointments:
				month_appointment_identifier.append(identifier)  # remember that identifier to print appointments in the end
				line += " {} ".format(colored("{:2}".format(day), appointmentdaycolor))  # color that day
			else:
				line += " {:2} ".format(day)  # print without color



		linelength += 1
		if linelength == 7:
			print(line)
			linelength = 0

			if weekno:
				weekno = (weekno + 1)%52
				line = "{:2}  ".format(weekno)
			else:
				line = ""
	print()


	# now print appointments of that month
	for date in month_appointment_identifier:
		prefix = " {}:".format(date)
		for a_date, a_desc in appointments[date]:
			print("{} {}".format(prefix, a_desc))
			prefix = " "*len(prefix)
	print()


def load_appointments(filepath):
	with open(filepath, 'r') as f:
		for line in f:
			datestr, description = line.strip().split(" ", 1)
			date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()

			if datestr not in appointments:
				appointments[datestr] = []

			appointments[datestr].append((date, description))


def create_appointment(y, m, d):

	y = int(input("year[{}]:  ".format(y)) or y)
	m = int(input("month[{}]: ".format(m)) or m)
	d = int(input("day[{}]:   ".format(d)) or d)

	desc = input("Appointment description: ")

	with open(args.appointment_file, 'a') as f:
		print("{}-{:02}-{:02} {}".format(y, m, d, desc), file=f)


if __name__ == "__main__":
	if not os.path.isfile(args.appointment_file):
		errprint('Cannot find appointment file. Please do "touch {}" first.'.format(args.appointment_file), 1)

	load_appointments(args.appointment_file)

	if not args.edit and not args.new:
		print_month(args.year, args.month)
		if args.monthrange > 1:
			d = datetime.date(args.year, args.month, 1)

			for i in range(args.monthrange):
				d = d + relativedelta(months=1)
				print_month(d.year, d.month)

	elif args.new:
		create_appointment(today.year, today.month, today.day)
	elif args.edit:
		print("ahm, editing is not yet supported")

