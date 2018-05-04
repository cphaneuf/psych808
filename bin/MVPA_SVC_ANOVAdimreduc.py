#!/usr/bin/python

#### This script runs Support Vector Classification MVPA analysis using Nilearn package
#### Prior to SVC, it runs an ANOVA-based dimension reduction as a feature selection step

# This script is optimized for use with ds008 file structure
# If directory structures change, please go to sections in the
#       script below that say "note: this is optimized for ds008 file structure"
#       and edit those portions of the code

# Define function to obtain date and time
def print_now(pre_text=''):
        from datetime import datetime as dt
        now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        print("{text}{cur_datetime}".format(text=pre_text, cur_datetime=now))
# Print message at script execution
print_now('\nBegin processing dimension reduction plus SVC MVPA at ')

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
print("\nSVC will compare '{}' and '{}' in '{}' dataset" \
	.format(labelgrp1, labelgrp2, dataset))

##### Import necessary library functions
# subprocess is imported to be able to use fsl functions
import subprocess
from subprocess import check_output
from subprocess import CalledProcessError
# Used to read Bash environment variables
import os
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
# Mask file to conduct preliminary analysis within
#	whole-brain (wb) mask in this case
#	after dimension reduction, smaller mask will be used
mask_file = nib.load('/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain_mask.nii.gz')

# "grp1dir" and "grp2dir" specifies the wildcard expression to 
#        grab the second level COPE files for all subjects
# note: this is optimized for ds008 file structure 
grp1dir=pathjoin(data_dir,'sub???','model','task001.gfeat',cond[labelgrp1]+'.feat','stats','cope1.nii.gz')
grp2dir=pathjoin(data_dir,'sub???','model','task001.gfeat',cond[labelgrp2]+'.feat','stats','cope1.nii.gz')
# subject_list uses glob to get a list of all the present files
#       and concatenates both grp1dir and grp2dir lists
# note: you need to have all the second level COPE files to have run
# Print message before grabbing files
print("\nGrabbing list of image files..." )
subject_list=glob(grp1dir)+glob(grp2dir)
# .sort() sorts all the files to make sure they are in proper order
subject_list.sort()

# nib.concat uses nibabel to concatenate images
# Single image can be loaded using nib.load(subject_list[0])
print("\nConcatenating images into a 4D file..." )
subjects_concat = nib.concat_images(subject_list, check_affines=False)

# fmri_label is an empty array to store labels of 
#       fmri runs, COPE files in this case (e.g., stop, go)
# subj_label is an empty array to store subject ids
# note: fmri_label and subj_label should have the same dimensions
#       let's say fmri_label is ['stop', 'go']
#       subj_label should be ['sub001', 'sub001']
#       in other words, each item in fmri_label should have a
#       subject identifier
fmri_label=[]
subj_label=[]
# cond_inv reverses the dictionary 
# lets say a dictionary is {'A':'B'}, it will be
# reversed to {'B':'A'}
cond_inv = {v: k for k, v in cond.iteritems()}

# the following for loop will go through each item in the subject_list
# and create an array of identifiers and store into arrays: fmri_label and subj_label
# subject.split will look at the name of the file and split the name of the file
#       to obtain subject identifiers (subj_label) and condition identifiers (fmri_la$
# note: this is optimized for ds008 file structure
print("\nObtaining labels for subjects and labels for conditions..." )
for subject in subject_list:
        copenum = subject.split('/')[8].split('.')[0]
        fmri_label=np.append(fmri_label, cond_inv[copenum])
        subjectnum = subject.split('/')[5]
        subj_label = np.append(subj_label, subjectnum)

# Prepare the fMRI data: apply the mask
# NiftiMasker is a function from nilearn that creates a mask image
# then, in order to apply the mask image on actual image files
#	use .fit_transform on the files
#	this will reduce the number of voxels to the specified mask
from nilearn.input_data import NiftiMasker
print("\nMasking 4D concatenated image with mask file..." )
nifti_masker = NiftiMasker(mask_img=mask_file,
                           standardize=True, memory='nilearn_cache',
                           memory_level=1)
fmri_masked = nifti_masker.fit_transform(subjects_concat)

# We will perform Support Vector Classification (SVC)
print("\nPreparing for SVC linear classification..." )
from sklearn.svm import SVC
svc = SVC(kernel = 'linear')

# Define the dimension reduction to be used.
# Here we use a classical univariate feature selection based on F-test,
# namely Anova. When doing full-brain analysis, it is better to use
# SelectPercentile, keeping 5% of voxels
# (because it is independent of the resolution of the data).
print("\nPreparing for feature selection with top 5% voxels..." )
from sklearn.feature_selection import SelectPercentile, f_classif
feature_selection = SelectPercentile(f_classif, percentile=5)

# We have our classifier (SVC), our feature selection (SelectPercentile),and now,
# we can plug them together in a *pipeline* that performs the two operations
from sklearn.pipeline import Pipeline
print("\nExecuting feature selection followed by SVC..." )
anova_svc = Pipeline([('anova', feature_selection), ('svc', svc)])

# Fit decoder and predict
# fmri_masked contains features
# fmri_label contains labels
anova_svc.fit(fmri_masked, fmri_label)
prediction = anova_svc.predict(fmri_masked)

#### Obtain prediction scores via cross validation
from sklearn.cross_validation import LeaveOneLabelOut, cross_val_score

# Define the cross-validation scheme used for validation.
# Here we use a LeaveOneLabelOut cross-validation on the subject label
# which corresponds to a leave-one-subject-out
print("\nPreparing and executing Leave-One-Out Cross Validation..." )
cv = LeaveOneLabelOut(subj_label)
# To look at the cross validation scheme, use the following
# >>> for train_index, test_index in cv:
# >>>    print("TRAIN:", list(train_index), "TEST:", list(test_index))
# or you can use the following to get exact subject ids
# >>> for train_index, test_index in cv:
# >>>    print("TRAIN:", list(subj_label[train_index]), "TEST:", list(subj_label[test_index]))

# Compute the prediction accuracy for the different folds (i.e. subject)
cv_scores = cross_val_score(anova_svc, fmri_masked, fmri_label, cv=cv)

# Return the corresponding mean prediction accuracy
classification_accuracy = cv_scores.mean()

# Print the results
print("Classification accuracy: {}").format(classification_accuracy)

print("\nSaving discriminating weights into a nifti file..." )
# Look at the SVCs discriminating weights
coef = svc.coef_
# reverse feature selection
# with columns of zeros inserted where features would have
#        been removed by `transform`.
coef = feature_selection.inverse_transform(coef)
# reverse masking into an actual image
# that can be recognized by nibabel
weight_img = nifti_masker.inverse_transform(coef)

#saving the image files into nifti format for visualization
nib.save(weight_img, pathjoin(project_dir, dataset, 'MVPA_SVC_orig.nii.gz'))

# use fslmaths to scale the MVPA_SVC_orig image
# scaling is done because values are very small in image
# the image is basically multiplied by 100000
print("\nScaling weights image..." )
# Get program locations from system
fslmaths = check_output(['which', 'fslmaths']).strip()
fsldir = os.getenv('FSLDIR')
# change the present directory to the dataset directory 
pdir = pathjoin(project_dir, dataset)
os.chdir(pdir)
# create a command using fslmaths to multiply image
img_scale_cmd = [ fslmaths, 'MVPA_SVC_orig.nii.gz', '-mul', '100000',
                   'MVPA_SVC.nii.gz' ]
# execute the fslmaths command
fslmaths_out = check_output(img_scale_cmd)

# end of script print message
print_now('\nEnd processing SVC MVPA at ')
