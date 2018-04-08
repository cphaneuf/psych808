#!/usr/bin/python

dataset = 'ds008'

##### Import necessary library functions

# Used to read Bash environment variables
from os import getenv

# Used to get the correct expansion of ~
from os.path import expanduser

# Used to join directory names into a path with appropriate separator
# characters, even on Windows.
from os.path import join as pathjoin

# Set the project directory
project_dir = pathjoin(expanduser('~'), 'Projects')

# Set the data directory
data_dir = pathjoin(project_dir, dataset)

# Set the template directory
html_template_dir = pathjoin(project_dir, 'local', 'share', 'templates', 'html')

# Set the output directory
html_output_dir = pathjoin(project_dir, 'output', 'html')

##### End variable declarations

##### Begin processing

# Generate single subject, bet_slices HTML file from the template
# and put it into the output/html folder.

# set the subject variable by reading the environment variable
subject = getenv('subject')

# set the path to the subject's anatomy files
anat_path = pathjoin(data_dir, subject, 'anatomy')

# Open, read, and close the template file
templ_file = open(pathjoin(html_template_dir, 'bet_slices.html'), 'r')
html_text = templ_file.read()
templ_file.close()

# write the subject HTML file
this_html_file = pathjoin(html_output_dir, subject + '_bet_slices.html')
print("Writing HTML file {:s}\n".format(this_html_file))
html_file = open(this_html_file, 'w')
html_file.write(html_text.format(subject=subject, anat_path=anat_path))
html_file.close()

##### End processing
