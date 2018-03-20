#!/usr/bin/python

# open template and replace with title and header with string appropriate to the desired subject number
file = open('/home/cphaneuf/Projects/local/share/templates/html/bet_slices_template.html', 'r')
title_string = 'Slices for Subject {}'
header_string = 'Anatomical slices for Subject {}'
title_string.format(001)
header_string.format(001)
print title_string
print header_string
file.close()

# copy file to path
html_file_str = 'sub{}_bet_slices.html'
html_file_str.format(001)
file2 = open('/home/cphaneuf/Projects/output/html/html_file_str', 'w')
print file
file.close()

