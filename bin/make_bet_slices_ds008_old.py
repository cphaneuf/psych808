#!/usr/bin/python

projects_dir = '/home/cphaneuf/Projects'

# open template and replace with title and header with string appropriate to the desired subject number
sub_num = 001
file = open(projects_dir + '/local/share/templates/html/bet_slices_template.html', 'r')
file_string = file.read()
file.close()

# copy file to path
html_file_str = 'sub{:03d}_bet_slices.html'
anatomy = projects_dir + '/ds008/sub{:03d}/anatomy'.format(sub_num)
file2 = open(projects_dir + '/output/html/' + html_file_str.format(sub_num), 'w')
file2.write(file_string.format(sub_num = sub_num, anatomy = anatomy))
file2.close()

