#!/usr/bin/python

#### This script runs Searchlight MVPA analysis using Nilearn package

# This script is optimized for use with ds008 file structure
# If directory structures change, please go to sections in the
# 	script below that say "note: this is optimized for ds008 file structure"
# 	and edit those portions of the code

# Define function to obtain date and time
def print_now(pre_text=''):
        from datetime import datetime as dt
        now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        print("{text}{cur_datetime}".format(text=pre_text, cur_datetime=now))
# Print message at script execution
print_now('\nBegin processing searchlight MVPA at ')

##### Initialize variables here
# dataset is the name of the dataset
# cond is a dictionary consisting of contrast names corresponding to copes
#	from second lvl analysis. cond is in the format {condition:copename}
# labelgrp1 and labelgrp2 are two groups for classification 
dataset = 'ds008'
cond = {'go':'cope1', 'stop':'cope2', 'fail stop':'cope3', 'stop-go':'cope4'}
labelgrp1='go'
labelgrp2='stop'
# Print message after script initialization
print("\nSearchlight will compare '{}' and '{}' in '{}' dataset" \
	.format(labelgrp1, labelgrp2, dataset))

##### Import necessary library functions
# Used to read Bash environment variables
from os import getenv
# Used to get the correct expansion of ~, last element of path
from os.path import expanduser, basename
# Used to join directory names into a path with appropriate separator
# characters, even on Windows.
from os.path import join as pathjoin
# Import glob for easy wildcard use
from glob import glob
# Import nibabel for neuroimaging data manipulation
import nibabel as nib
# Import nilearn for MVPA analysis
import nilearn
from nilearn.input_data import NiftiMasker
# Import numpy for array and matrix operations
import numpy as np

# Set the project directory
project_dir = pathjoin(expanduser('~'), 'Projects')
# Set the data directory
data_dir = pathjoin(project_dir, dataset)
# Mask file to conduct searchlight analysis within
#	whole-brain (wb) mask in this case
mask_file = nib.load('/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain_mask.nii.gz')

# "grp1dir" and "grp2dir" specifies the wildcard expression to
#        grab the second level COPE files for all subjects
# note: this is optimized for ds008 file structure
grp1dir=pathjoin(data_dir,'sub???','model','task001.gfeat',cond[labelgrp1]+'.feat','stats','cope1.nii.gz')
grp2dir=pathjoin(data_dir,'sub???','model','task001.gfeat',cond[labelgrp2]+'.feat','stats','cope1.nii.gz')
# subject_list uses glob to get a list of all the present files
#	and concatenates both grp1dir and grp2dir lists
# note: you need to have all the second level COPE files to have run
# note: glob is like 'ls' in bash
# Print message before grabbing files
print("\nGrabbing list of image files..." )
subject_list=glob(grp1dir)+glob(grp2dir)
# .sort() sorts all the files to make sure they are in proper order
subject_list.sort()

# nib.concat uses nibabel to concatenate images (join list of 3D images into a 4D image)
# Single image can be loaded using nib.load(subject_list[0])
print("\nConcatenating images into a 4D file..." )
subjects_concat = nib.concat_images(subject_list, check_affines=False)

# fmri_label is an empty array to store labels of
#	fmri runs, COPE files in this case (e.g., stop, go)
# subj_label is an empty array to store subject ids
# note: fmri_label and subj_label should have the same dimensions
#	let's say fmri_label is ['stop', 'go']
#	subj_label should be ['sub001', 'sub001']
#	in other words, each item in fmri_label should have a
#	subject identifier
fmri_label=[]
subj_label=[]
# cond_inv reverses the dictionary
# lets say a dictionary is {'A':'B'}, it will be
# reversed to {'B':'A'}
cond_inv = {v: k for k, v in cond.iteritems()}

# the following for loop will go through each item in the subject_list
# and create an array of identifiers and store into arrays: fmri_label and subj_label
# subject.split will look at the name of the file and split the name of the file
#	to obtain subject identifiers (subj_label) and condition identifiers (fmri_label)
# note: this is optimized for ds008 file structure
print("\nObtaining labels for subjects and labels for conditions..." )
for subject in subject_list:
	copenum = subject.split('/')[8].split('.')[0]
	fmri_label = np.append(fmri_label, cond_inv[copenum])
	subjectnum = subject.split('/')[5]
	subj_label = np.append(subj_label, subjectnum)

# Define the cross-validation scheme used for validation.
# Here we use a KFold cross-validation on the session, which corresponds to
# splitting the samples in 4 folds and make 4 runs using each fold as a test
# set once and the others as learning sets
from sklearn.cross_validation import StratifiedKFold
folds=4
print("\nDefining cross-validation scheme using {} Folds..." ).format(folds)
skf = StratifiedKFold(fmri_label, n_folds=folds)
# To look at the Stratified K-Folds scheme, use the following
# >>> for train_index, test_index in kf:
# >>>    print("TRAIN:", list(train_index), "TEST:", list(test_index))
# or you can use the following to get exact subject ids
# >>> for train_index, test_index in kf:
# >>>    print("TRAIN:", list(subj_label[train_index]), "TEST:", list(subj_label[test_index]))

# nilearn.decoding has the SearchLight function for SearchLight analysis
# mask_file, radius, and cross-validation schemes are main things to be specified
# next, .fit has to be run in the format of (features, labels)
import nilearn.decoding
rad=5.6
print("\nRunning searchlight across the brain with radius {}..." ).format(rad)
# The radius is the one of the Searchlight sphere that will scan the volume
searchlight = nilearn.decoding.SearchLight(
    mask_file,
    radius=rad, n_jobs=1,
    verbose=1, cv=skf)
searchlight.fit(subjects_concat, fmri_label)

# Now save the image into a nifti-format using new_img_like
# new_img_like uses the mask_file as reference to specify the type of image
# 	and the matrix of searchlight.scores plot the searchlight values 
print("\nSearchlight complete, saving image..." ).format(rad)
#saving the image files for visualization
from nilearn.image import new_img_like
searchlight_img=new_img_like(mask_file, searchlight.scores_)
nib.save(searchlight_img, pathjoin(project_dir, dataset, 'MVPA_searchlight.nii.gz'))

# end of script print message
print_now('\nEnd processing searchlight MVPA at ')
