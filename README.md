# tcal

cal-style terminal calender with appointment management.

Work in progress, backwards-incompatible breakage might occur.


## usage

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

commandline-options:

	usage: tcal.py [-h] [-s APPOINTMENT_FILE] [-m MONTH] [-r MONTHRANGE] [-y YEAR]
	               [-w] [-n | -e]
	
	tcal - terminal calendar
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -s APPOINTMENT_FILE, --store APPOINTMENT_FILE
	                        file storing appointments, defaults to ~/.tcal-appointments
	  -m MONTH, --month MONTH
	                        first month to display
	  -r MONTHRANGE, --range MONTHRANGE
	                        number of months to display
	  -y YEAR, --year YEAR  year of the first month to display
	  -w, --weeks           show weeks when printing calendar
	  -n, --new             add new appointment
	  -e, --edit            edit appointments for specific date


## Configuration

Configuration is done soley via commandline options for now.


## License

This works is released under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.txt). You can find a copy of this license at https://www.gnu.org/licenses/gpl-3.0.txt.

