# Criminal Analysis & Geoprocessing

In law enforcement understanding how, where, and when crime happens goes a 
long way to helping prevent similar crimes from happening in the future.

Given that old school manual criminal analysis with Excel tables is very 
boring, and the patterns and repetition present in this task, 
criminal analysis is a great candidate for automation.

By adding geoprocessing to the equation we get a very user friendly system,
as we can crunch an arbitrary chunk of data for the user with only a few inputs

With that we can give him a detailed summary with the statistics he needs 
coupled with a visual representation of those statistics, greatly improving 
his comprehension and decision making.


## Features

+ Report generation
	+ crime comparison between two distinct periods
	+ target specific crimes
	+ target specific neighborhoods or venues
	+ breakdown by each day of the week
	+ breakdown by hour of the day
+ Geoprocessing
	+ sync the crime's location with Google Maps' API based, based on its address
	+ visually represent crimes type and location
	+ visual representation as marker or heatmap
	+ filter by: crime, date, or/and time

## Prerequisites

+ Python 3
+ Django >= 1.10.1


## Running in development

Create and activate a virtualenv:

```
$ pip3 install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

Install the requirements:

```
$ pip3 install -r requirements.txt
```

Set the `settings.py` and `local settings.py` to your liking, and run the migratrions.

```
$ python manage.py migrate
```

Start the local server:

```
$ python manage.py runserver
```

*Note: `PMMT` stands to `Polícia Militar do Estado de Mato Grosso`*