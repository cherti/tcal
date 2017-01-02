#!/usr/bin/env python3

import datetime, calendar, os, sys, argparse, tempfile, subprocess, shutil
from termcolor import colored
from dateutil.relativedelta import relativedelta

appointments = {}
appointmentdaycolor = 'cyan'

today = datetime.date.today()
cal = calendar.Calendar()

def errprint(msg, code):
	print(msg, file=sys.stderr)
	exit(code)

def validate_date_input(y, m, d):
	try:
		datetime.date(y, m, d)
	except ValueError as e:
		errprint("invalid input: " + str(e), 2)

parser = argparse.ArgumentParser(description='tcal - terminal calendar')
parser.add_argument('-s', '--store', action='store', dest='appointment_file', type=str, default=os.path.expanduser('~/.tcal-appointments'), help='file storing appointments')
parser.add_argument('-m', '--month', action='store', dest='month', type=int, default=today.month, help='first month to display')
parser.add_argument('-r', '--range', action='store', dest='monthrange', type=int, default=1, help='number of months to display')
parser.add_argument('-y', '--year', action='store', dest='year', type=int, default=today.year, help='year of the first month to display')
parser.add_argument('-w', '--weeks', action='store_true', default=False, dest='print_weeks', help='show weeks when printing calendar')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-n', '--new', action='store_true', default=False, dest='new', help='add new appointment')
group.add_argument('-e', '--edit', action='store_true', default=False, dest='edit', help='edit appointments for specific date')

args = parser.parse_args()


# templates for display mechanism
weekdaysline = " Mo  Di  Mi  Do  Fr  Sa  So"
blank_day = " "*4
date_id = lambda y, m, d: "{}-{:02}-{:02}".format(y, m, d)
fmt_day_col = lambda day: " {} ".format(colored("{:2}".format(day), appointmentdaycolor))
fmt_day = lambda day: " {:2} ".format(day)
fmt_monthyear = lambda y, m: datetime.date(y, m, 1).strftime("%B {}".format(y))
fmt_week_prefix = lambda weekno: "{:2}  ".format(weekno)

# compute the offset as half of the whitespaces the weekdaysline is longer than the monthyearline
centering_whitespaces = lambda len_centered_string, len_full_line_string: max(int((len_full_line_string - len_centered_string)/2), 0)*" "


def print_month(y, m):
	month_appointment_identifier = []    # collecting the appointments to be printed below this month
	monthyearline = fmt_monthyear(y, m)  # headerline of the month
	global weekdaysline                  # use weekdaysline that was defined in the templates

	if args.print_weeks:
		# prepare prefix for the weeks
		weekdaysline = len(fmt_week_prefix(00))*" " + weekdaysline  # extend weekdaysline to be properly aligned with weeknumbers in front
		_, isoweek, _ = datetime.date(y, m, 1).isocalendar()  # returns year, weekno and dayno of the year, we want the first weekno relevant
		line = fmt_week_prefix(isoweek)
	else:
		line = ""
		isoweek = None

	print(centering_whitespaces(len(monthyearline), len(weekdaysline)) + monthyearline)
	print(weekdaysline)


	lineblocks = 0
	for day, weekday in cal.itermonthdays2(y, m):
		if day == 0:
			line += blank_day
		else:
			identifier = date_id(y, m, day)
			if identifier in appointments:
				month_appointment_identifier.append(identifier)  # remember that identifier to print appointments in the end
				line += fmt_day_col(day)  # color that day
			else:
				line += fmt_day(day) # print without color



		lineblocks += 1
		if lineblocks == 7:  # line is full, week is complete
			print(line)
			lineblocks = 0

			# reinitialize line with or without week-prefix
			if isoweek:
				isoweek = (isoweek + 1)%52
				line = fmt_week_prefix(isoweek)
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


def read_date_info(y, m, d):
	print('Which date are we speaking about?')
	y = int(input(    "year[{}]: ".format(y)) or y)
	m = int(input(" month[{:2}]: ".format(m)) or m)
	d = int(input("   day[{:2}]: ".format(d)) or d)

	validate_date_input(y, m, d)

	return y, m, d



def create_appointment(y, m, d):

	try:
		y, m, d = read_date_info(y, m, d)
		desc = input("Appointment description: ")

		with open(args.appointment_file, 'a') as f:
			print("{}-{:02}-{:02} {}".format(y, m, d, desc), file=f)

	except KeyboardInterrupt:
		print("\nTermination by user, no appointment has been added")


def edit_appointments(y, m, d):
	y, m, d = read_date_info(y, m, d)

	identifier = date_id(y, m, d)

	if identifier not in appointments:
		print(':: no editable appointments on that date')
		return

	tmpfile = tempfile.NamedTemporaryFile()

	with open(tmpfile.name, 'w') as f:
		print("# Appointments on {}, edit or delete as you see fit:", file=f)
		f.write('\n'.join(['{} {}'.format(identifier, description) for dateobj, description in appointments[identifier]]))

	retval = subprocess.call([os.environ.get('EDITOR') or 'nano', tmpfile.name])
	if retval != 0:
		errprint("Your editor {0} exited nonzero with {1}, removing stale tmpfile and aborting".format(os.environ['EDITOR'], retval), 1)

	print(":: parsing appointments")
	with open(tmpfile.name, 'r') as f:
		changed_appts = [line for line in f.read().strip().split('\n') if not line.startswith('#') and not line == ""]

	# validate that we got proper input
	for a in changed_appts:
		try:
			datestr, description = a.split(' ', 1)
			y, m, d = datestr.split('-')
			y, m, d = int(y), int(m), int(d)
		except ValueError:
			errprint("invalid file content: couldn't parse line: {}".format(a), 3)
		validate_date_input(y, m, d)

	new_appointment_file = tempfile.NamedTemporaryFile()

	with open(args.appointment_file, 'r') as oaf, open(new_appointment_file.name, 'w') as naf:
		unchanged_appts = [line for line in oaf.read().strip().split('\n') if not line.startswith(identifier)]
		all_appts       = sorted(unchanged_appts + changed_appts)
		naf.write('\n'.join(all_appts))

	shutil.copy(new_appointment_file.name, args.appointment_file)


if __name__ == "__main__":
	if not os.path.isfile(args.appointment_file):
		errprint('Cannot find appointment file. Please do "touch {}" first.'.format(args.appointment_file), 1)

	load_appointments(args.appointment_file)

	if not args.edit and not args.new:  # the default, which is just printing the current state of appointments
		print_month(args.year, args.month)

		if args.monthrange > 1:
			# we need a date we can increment by one month and still be guaranteed to land in a correct next month
			# promlematic are 31sts in general, the ends of January, because February is especially short, etc.
			# to avoid all that hassle, we just take the first of our currently selected month, this way we get
			# rid of all the hassle and can use that for computation of the next months
			# Why not incrementing years and month manually? because this way yearbreaks and stuff are handled
			# by python-datetime, which might be overhead, but is sufficiently cheap to avoid cornercases by relying
			# on a reference implementation that has already dealt with possible date-cornercases
			dummydate = datetime.date(args.year, args.month, 1)
			for i in range(args.monthrange):
				dummydate = dummydate + relativedelta(months=1)
				print_month(dummydate.year, dummydate.month)

	elif args.new:
		create_appointment(today.year, today.month, today.day)

	elif args.edit:
		edit_appointments(today.year, today.month, today.day)
