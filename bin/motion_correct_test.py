#!/usr/bin/python

html_text = [
    '<html>',
    '<head>',
    '<title>Subject {:03d}: center slices</title>',
    '</head>',
    '<body>'
]

subj_id = 1

# erroneous - previous week's attempt
# print(html_text.format(subj_id))

# this week's solution
for line in html_text:
	# find is a method of a string
	if line.find('{:03d}'):
		print(line.format(subj_id))
	else:
		print(line)

# join is another STRING method, not a list method
html_text = "\n".join(html_text)
print(html_text).format(subj_id)
