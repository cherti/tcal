# tcal

cal-style terminal calender with appointment management.

Work in progress, backwards-incompatible breakage might occur.


## Dependencies

This script depends on `python-termcolor` and `python-dateutil`.
It is written for Python version 3 and upwards, lowest version it has been tested with is Python 3.5.2. (If you have an older version of Python and things work for you, feel free to drop me a line.)


## Usage

Just use the tcal.py-script:

	>> tcal.py
	    January 2017
	Mo Di Mi Do Fr Sa So
	                          1 
	  2   3   4   5   6   7   8 
	  9  10  11  12  13  14  15 
	 16  17  18  19  20  21  22 
	 23  24  25  26  27  28  29 
	 30  31                     
	
	 2017-01-03: foo
	 2017-01-13: bar
	 2017-01-15: baz
	 2017-01-28: foobarbatutraine

### commandline-options:

	usage: tcal.py [-h] [-s APPOINTMENT_FILE] [-y YEAR] [-m MONTH] [-r MONTHRANGE]
	               [-f DATE_FORMAT] [-w] [-t] [-l] [-n | -e]
	
	tcal - terminal calendar
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -s APPOINTMENT_FILE, --store APPOINTMENT_FILE
	                        file storing appointments, defaults to ~/.tcal-appointments
	  -y YEAR, --year YEAR  year of the first month to display
	  -m MONTH, --month MONTH
	                        first month to display
	  -r MONTHRANGE, --range MONTHRANGE
	                        number of months to display
	  -f DATE_FORMAT, --format DATE_FORMAT
	                        format of printed dates, must be valid python-date-
	                        template
	  -w, --weeks           show weeks when printing calendar
	  -t, --time            show time (if set) when printing appointments
	  -l, --location        show location (if set) when printing appointments
	  -n, --new             add new appointment
	  -e, --edit            edit appointments for specific date

### Multi-day-appointments:

To set an appointment for more than one day, just give a spread like `16-19` when asked for year, month or date upon creation of a new appointment.

The spread will be applied to the field you specified in only, i.e. a spread in the month field will create one appointment at the specified day per month included in the spread.


## Configuration

Configuration is done soley via commandline options for now.


## License

This works is released under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.txt). You can find a copy of this license at https://www.gnu.org/licenses/gpl-3.0.txt.

