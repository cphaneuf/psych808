# psych808

This repo contains content from the Psych808 course at the University of Michigan (Ann Arbor) during Winter 2018. 
The class was taught by Professor Cindy Lustig and Bennet Fauber. During this course, students (including myself)
worked through writing an FSL analytic pipeline for an fMRI dataset. 

The dataset used for this course was 'ds008' from Open fMRI. Note that Subject008 was erroneous, and much of the 
error checking and quality control reflects that. 

To summarize the contents of this repo:
- etc: contains slices.html
- lib: currently empty
- share: contains all of the templatized files
- bin: contains all of the scripts

In order to navigate this repo, start by running project_scripts ($ ./project_scripts) from bin. This will print 
out a summary of all of the scripts' inputs, outputs, and manipulations. For more information, see the text file
'Psych808_FSLscripts_summary', which contains summary notes from our final class period. This file also explains 
how to obtain and unzip your raw fMRI data.

These scripts are based off of FEAT*, which is part of FSL. They automate the GUI process, allowing more efficient 
data analysis. You will also find some forays into MVPA in this repo, though those were not used to process the 
ds008 dataset for the majority of the course.

*FEAT uses GLM (general linear modeling), aka multiple regression. See FEAT documentation for more information.
