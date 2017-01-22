#!/usr/bin/env python3

import datetime, calendar, os, sys, argparse, tempfile, subprocess, shutil, time
from collections import namedtuple

def errprint(msg, code):
	print(msg, file=sys.stderr)
	exit(code)

try:
	from termcolor import colored
	from dateutil.relativedelta import relativedelta
except ModuleNotFoundError as e:
	errprint("Could not find module {}, maybe it is not installed?".format(e.name), 404)



Appointment = namedtuple('Appointment', ['date', 'time', 'location', 'description'])
appointmentdaycolor = 'cyan'
appointments = {}
appt2str = lambda a: "{} {} {} {}".format(date2str(a.date), a.time or '-', a.location or '-', a.description)

def str2appt(s):
	try:
		datestr, t, location, description = s.split(" ", 3)
	except ValueError:
		errprint("Error: malformed line: {}".format(s), 7)

	date = str2date(datestr)

	if t == '-':
		t = None
	else:
		try:
			t = time.strptime(t, "%H:%M")
			t = "{:02}:{:02}".format(t.tm_hour, t.tm_min)
		except ValueError as e:
			errprint("Error: malformed line: {}\n{}".format(s, str(e)), 6)

	location = location if location != '-' else None
	return Appointment(str2date(datestr), t, location, description)


today = datetime.date.today()
cal = calendar.Calendar()

parser = argparse.ArgumentParser(description='tcal - terminal calendar')
parser.add_argument('-s', '--store', action='store', dest='appointment_file', type=str, default=os.path.expanduser('~/.tcal-appointments'), help='file storing appointments')

# range of interest
parser.add_argument('-y', '--year', action='store', dest='year', type=int, default=today.year, help='year of the first month to display')
parser.add_argument('-m', '--month', action='store', dest='month', type=int, default=today.month, help='first month to display')
parser.add_argument('-r', '--range', action='store', dest='monthrange', type=int, default=1, help='number of months to display')

# display properties
parser.add_argument('-f', '--format', action='store', default="%d.%m.%Y", dest='date_format', help='format of printed dates, must be valid python-date-template')
parser.add_argument('-w', '--weeks', action='store_true', default=False, dest='weeks', help='show weeks when printing calendar')
parser.add_argument('-t', '--time', action='store_true', default=False, dest='time', help='show time (if set) when printing appointments')
parser.add_argument('-l', '--location', action='store_true', default=False, dest='location', help='show location (if set) when printing appointments')

# changing stored state
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-n', '--new', action='store_true', default=False, dest='new', help='add new appointment')
group.add_argument('-e', '--edit', action='store_true', default=False, dest='edit', help='edit appointments for specific date')

args = parser.parse_args()


# templates for display mechanism
baseweekdaysline = " Mo  Di  Mi  Do  Fr  Sa  So"
blank_day = " "*4
date_id = lambda y, m, d: "{}-{:02}-{:02}".format(y, m, d)
fmt_day = lambda day, color=None, attrs=None: " {} ".format(colored("{:2}".format(day), color, attrs=attrs or []))
fmt_monthyear = lambda y, m: datetime.date(y, m, 1).strftime("%B {}".format(y))
fmt_week_prefix = lambda weekno: "{:2}  ".format(weekno)

# helperfunctions for str <-> date
def date2str(d, localized=False):
	try:
		if localized:
			return d.strftime(args.date_format)
		else:
			return d.strftime("%Y-%m-%d")
	except AttributeError:
		errprint("Error: called date2str with something that does not seem to be a dateobject", 4)

def str2date(s):
	try:
		return datetime.datetime.strptime(s, "%Y-%m-%d").date()
	except:
		errprint("Error: unparsable datestring: {}".format(s), 4)


# compute the offset as half of the whitespaces the weekdaysline is longer than the monthyearline
centering_whitespaces = lambda len_centered_string, len_full_line_string: max(int((len_full_line_string - len_centered_string)/2), 0)*" "


def print_month(y, m):
	month_appointment_identifier = []    # collecting the appointments to be printed below this month
	monthyearline = fmt_monthyear(y, m)  # headerline of the month
	weekdaysline  = baseweekdaysline     # use weekdaysline that was defined in the templates

	if args.weeks:
		# prepare prefix for the weeks
		weekdaysline = len(fmt_week_prefix(00))*" " + weekdaysline  # extend weekdaysline to be properly aligned with weeknumbers in front
		_, isoweek, _ = datetime.date(y, m, 1).isocalendar()  # returns year, weekno and dayno of the year, we want the first weekno relevant
		line = fmt_week_prefix(isoweek)
	else:
		line = ""
		isoweek = None

	# print headers
	print(centering_whitespaces(len(monthyearline), len(weekdaysline)) + monthyearline)
	print(weekdaysline)

	# now print calendar-view
	lineblocks = 0
	for day, weekday in cal.itermonthdays2(y, m):
		if day == 0:
			line += blank_day
		else:
			date = datetime.date(y, m, day)
			identifier = date2str(date)

			if date == today:
				attrs = ["reverse"]
			else:
				attrs = []

			if identifier in appointments:
				month_appointment_identifier.append(identifier)  # remember that identifier to print appointments in the end
				color = appointmentdaycolor
				attrs += ["bold"]
			else:
				color = None

			line += fmt_day(day, color, attrs=attrs)


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
		prefix = " {}: ".format(date2str(str2date(date), localized=True))
		for a in sorted(appointments[date], key=lambda x: x.time):
			line = prefix
			if a.time and args.time:
				# strip potential leading zero and replace them with whitespace
				t = " "+a.time[1:] if a.time.startswith('0') else a.time
				line += "[{}] ".format(t)
			line += a.description
			if a.location and args.location:
				line += " ({})".format(a.location)
			print(line)

			prefix = " "*len(prefix)  # blank out date to not print it on each line

	print('\n')


def load_appointments(filepath):
	with open(filepath, 'r') as f:
		for line in f:
			line = line.strip()
			datestr, _ = line.split(" ", 1)

			if datestr not in appointments:
				appointments[datestr] = []
			appointments[datestr].append(str2appt(line))


def read_date(basedate):
	try:
		print('Which date are we speaking about?')
		in_y = input(    "year[{}]: ".format(basedate.year))
		in_m = input(" month[{:2}]: ".format(basedate.month))
		in_d = input("   day[{:2}]: ".format(basedate.day))
	except KeyboardInterrupt:
		print("\nTermination by user, no appointment has been added")

	if '-' in in_y or '-' in in_m or '-' in in_d:
		dates = []
		# multi-day
		if '-' in in_d:
			d_start, d_stop = in_d.split('-')
			d_start, d_stop = int(d_start), int(d_stop)
		else:
			d_start = d_stop = int(in_d or basedate.day)

		if '-' in in_m:
			m_start, m_stop = in_m.split('-')
			m_start, m_stop = int(m_start), int(m_stop)
		else:
			m_start = m_stop = int(in_m or basedate.month)

		if '-' in in_y:
			y_start, y_stop = in_y.split('-')
			y_start, y_stop = int(y_start), int(y_stop)
		else:
			y_start = y_stop = int(in_y or basedate.year)

		for d in range(d_start, d_stop+1):
			for m in range(m_start, m_stop+1):
				for y in range(y_start, y_stop+1):

					try:
						date = datetime.date(y, m, d)
					except ValueError as e:
						errprint("invalid input: " + str(e), 2)

					dates.append(date)

		return dates

	else:
		# only a single-date, let's go for the simple variant
		y = int(in_y or basedate.year)
		m = int(in_m or basedate.month)
		d = int(in_d or basedate.day)

		try:
			date = datetime.date(y, m, d)
		except ValueError as e:
			errprint("invalid input: " + str(e), 2)

		return [date]


def read_time():

	t = input("Time [-]: ") or "-"

	if t == "-":
		return t

	try:
		t = time.strptime(t, "%H:%M")
		return "{:02}:{:02}".format(t.tm_hour, t.tm_min)
	except ValueError as e:
		errprint("Error: " + str(e), 6)


def create_appointment(appt):

	try:
		with open(args.appointment_file, 'a') as f:
			print(appt2str(appt), file=f)
	except KeyboardInterrupt:
		print("\nTermination by user, no appointment has been added")


def edit_appointments(basedate):
	identifier = date2str(date)

	if identifier not in appointments:
		print(':: no editable appointments on that date')
		return

	tmpfile = tempfile.NamedTemporaryFile()

	with open(tmpfile.name, 'w') as f:
		print("# Appointments on {}, edit or delete as you see fit.".format(identifier), file=f)
		print("# Format is: 'YYYY-MM-DD time location description'", file=f)
		print("# Time must be HH:MM or '-' if no time is specified. ", file=f)
		print("# location may not have whitespaces in it and be '-' if no location is specified.", file=f)
		f.write('\n'.join([appt2str(a) for a in appointments[identifier]]))

	retval = subprocess.call([os.environ.get('EDITOR') or 'nano', tmpfile.name])
	if retval != 0:
		errprint("Your editor {0} exited nonzero with {1}, removing stale tmpfile and aborting".format(os.environ['EDITOR'], retval), 1)

	print(":: parsing appointments")
	with open(tmpfile.name, 'r') as f:
		changed_appts = [line for line in f.read().strip().split('\n') if not line.startswith('#') and not line == ""]

	# validate that we got proper input
	validated_changed_appts = []
	for astr in changed_appts:
		# no need to catch errors, errorhandling is done in str2appt already, we just want to see if it parses
		validated_changed_appts.append(appt2str(str2appt(astr)))

	new_appointment_file = tempfile.NamedTemporaryFile()

	with open(args.appointment_file, 'r') as oaf, open(new_appointment_file.name, 'w') as naf:
		unchanged_appts = [line for line in oaf.read().strip().split('\n') if not line.startswith(identifier)]
		all_appts       = sorted(unchanged_appts + validated_changed_appts)
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
			for i in range(1, args.monthrange):
				dummydate = dummydate + relativedelta(months=1)
				print_month(dummydate.year, dummydate.month)

	elif args.new:
		dates = read_date(today)
		desc = input("Appointment description: ")
		t = read_time()
		location = input("Location [-]: ") or "-"

		for date in dates:
			a = Appointment(date, t, location, desc)
			create_appointment(a)

	elif args.edit:
		dates = read_date(today)
		for date in dates:
			edit_appointments(date)

