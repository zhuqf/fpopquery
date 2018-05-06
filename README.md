# fpopquery
==========

A python based freedompop account query

print the summary information for each account

## Usage
copy freedompop.cfg.example as freedompop.cfg, modify it to included your accounts and password

```
$ python3 fpopquery.py
mail1@domain.com(1xxxxxxxxxx):	plan-zmp-free	  3/200 minutes  0/500 text messages,  0/100 intl' minutes, 166.27MB/642.0MB mobile data, next bill due date 2018-04-21 amount US$0.00 16 days left
mail2@domain.com(1xxxxxxxxxx)):	plan-free-ww	  0/200 minutes  0/500 text messages,  1/100 intl' minutes,   5.22MB/700.0MB mobile data, next bill due date 2018-05-04 amount US$0.00 a month left

```

## Feature updated
2018-05-05: Add warning and limit in Configure, when data usage is above warning, the report will show usage in blue, when over limit it will show in read. warning and limit can be percentage from 0 to 1 or integer large than 1 as MB.

## License
Licensed under the MIT license.
