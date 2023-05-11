# -*- coding: utf-8 -*-
"""
Created in 2022

Script to analyze the fiber photometry data with copulation test for SCARF004.
Based on Python 3.9, installed via anaconda.

Steps to take:
    1) Make a folder that contains all recorded TDT data
    2) Make a folder for your experiment data, and save the TDT metafile and Noldus excel output of the raw data in it
    3) Save a copy of the python script in this folder as well (otherwise you loose your master script due to automatic saving when running)
    4) Make an "Output" folder in the folder for the results
    5) Make all folders in which you want to store the figures (see list with directory_TDT)
    6) Fill in test times
    7) Fill in baseline correction time for snips
    8) Check behaviors and behavioral parameters that were calculated
    9) Check whether your observer sheets have similar names (plus observation column)
    10) Fill in list with excluded animals

Information on conditions built in:
    - Start lordosis is scored as lordosis, End lordosis as the copulation the female received

reminder for Eelke figsize = width-length 6,10 was original


NOTE -> in case you see an error in the uncorrected version: check:             
dFF_snips_pre1=(dFF[int(pre_stim[-1]):int(light_stim[-1])]) -> should become dFF_snips_pre1.append(dFF[int(pre_stim[-1]):int(light_stim[-1])])


@author: Eelke Snoeren
"""

import tdt
import trompy as tp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from itertools import chain
sns.set()
from PIL import Image
import glob
import os
from matplotlib.backends.backend_pdf import PdfPages
import multiprocessing as mp
from pandas import ExcelWriter
import openpyxl
from sklearn.metrics import auc
import scipy.stats as stats
pd.set_option('use_inf_as_na', True)
from pandas import option_context
from tdt import epoc_filter
from numpy import trapz
from numpy import NaN
import os.path
from os import path
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math
from math import isnan
from matplotlib import rcParams
import pickle

# Define the directory folders (use / instead of \)
directory= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA" # Of the metafile and behavioral data
directory_tdt="D:/TDT SCARF004/" # Of the TDT recordings
directory_output= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Output" # Of the output folder for your excel results
directory_results= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Results tdt" # Of the output folder for your results
directory_results_cor= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Results tdt cor" # Of the output folder for your results corrected for outliers
directory_results_beh= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Results behavior" # Of the output folder for your results

if not os.path.isdir(directory_output):
    os.mkdir(directory_output)

if not os.path.isdir(directory_results):
    os.mkdir(directory_results)

if not os.path.isdir(directory_results_cor):
    os.mkdir(directory_results_cor)

if not os.path.isdir(directory_results_beh):
    os.mkdir(directory_results_beh)

directory_TDT_lightdoor = "/Pictures Results TDT lightdoor"
directory_TDT_lightdoor_perrat="/Pictures Results TDT lightdoor per rat"
directory_TDT_lightdoor_AUC = "/Pictures Results TDT AUC lightdoor"
directory_TDT_behavior = "/Pictures Results TDT behavior"
directory_TDT_behavior_perrat="/Pictures Results TDT behavior per rat"
directory_TDT_behavior_AUC = "/Pictures Results TDT AUC behavior"
directory_behavior_AUC = "/Pictures Results AUC behavior"
directory_behavior_perrat = "/Pictures Results behavior per rat"
directory_behavior_pertest = "/Pictures Results behavior per test"
directory_behavior_total = "/Pictures Results behavior total"
directory_pickle = "D:/TDT SCARF004/Pickle files"

################ ################ ################ ################  
################ OPEN PICKLE #####################
################ ################ ################ ################  

# Change directory to output folder
os.chdir(directory_pickle)

# to load
# with open("my_dict_process.pickle", "rb") as file: # signals with outlier modifications
#     my_dict_process= pickle.load(file)

with open("my_dict_process_cor.pickle", "rb") as file: # signals with manual adjustments to outlier modifications
    my_dict_process= pickle.load(file)

with open("my_dict_behavior.pickle", "rb") as file:
    my_dict_behavior= pickle.load(file)

# Change directory back
os.chdir(directory)

print("analyzed data loaded")

# Assign TDT metafile name to `file`
file_TDT = 'Metafile TDT SCARF004.xlsx' # Metafile
file_beh1 = 'SCARF004_F1_EventLogs.xlsx' # Noldus raw data
file_beh2 = 'SCARF004_F3_EventLogs.xlsx' # Noldus raw data
file_beh3 = 'SCARF004_F5_EventLogs.xlsx' # Noldus raw data
file_beh4 = 'SCARF004_RF1_EventLogs.xlsx' # Noldus raw data
file_beh5 = 'SCARF004_RF3_EventLogs.xlsx' # Noldus raw data
file_beh6 = 'SCARF004_RS1_EventLogs.xlsx' # Noldus raw data
file_beh7 = 'SCARF004_S1_EventLogs.xlsx' # Noldus raw data
file_beh8 = 'SCARF004_S2_EventLogs.xlsx' # Noldus raw data
file_beh9 = 'SCARF004_S3_EventLogs.xlsx' # Noldus raw data
file_beh10 = 'SCARF004_D1_EventLogs.xlsx' # Noldus raw data
file_stat = "%s/SCARF004_statistics.xlsx" % directory_output # Later statistics file name

# Define the directory from which the files should come
os.chdir(directory)

# Define output file names
out_path1 = "%s/Output/SCARF004_detailed_results.xlsx" % directory # Filename & location of detailed results
out_path2 = "%s/Output/SCARF004_general_results.xlsx" % directory # Filename & location of general simplified results
out_path3 = "%s/Output/SCARF004_statistics.xlsx" % directory # Filename & location of Statistics results
out_path4 = "%s/Output/SCARF004_dataprep_test.xlsx" % directory # Filename & location of dataframe raw data test
out_path5 = "%s/Output/SCARF004_results_test.xlsx" % directory # Filename & location of dataframe raw results test
out_path6 = "%s/Output/SCARF004_python_dictionaries.xlsx" % directory # Filename & location of dataframe of dictionaries for python use
out_path7 = "%s/Output/SCARF004_python_processdata.xlsx" % directory # Filename & location of dataframe of the TDT processdata for python use

# Fill in time test
Timetest_baseline = 180
Timetest_introduction = 180
Timetest_anticipatory = 10
Timetest_prereward = Timetest_introduction+Timetest_anticipatory
Timetest_reward = 900
Timetest_total = Timetest_baseline+Timetest_introduction+Timetest_anticipatory +Timetest_reward

# Fill the list with rats that need to be excluded for analysis
list_excl=['311','313','315']
list_excl_sex=[]
# list_excl_sex=['301','329','328','335']

list_excltdt=[311,313,315,303,306,314,324,327,318,327]
list_excltdt_sex=[]
# list_excltdt_sex=[301,329,328,335]

# Fill in list with TestID that needs exclusion due to too many signal artifacts
list_signal_artifact_excl=['304SECREWARD_rev1','307DISREWARD1','307SECREWARD2','308SECREWARD1','308SECREWARD2','308SECREWARD3',
                            '320SECREWARD1','323SECREWARD2','323SECREWARD3']

# Set your baseline correction times before snips
baseline_start=-7
baseline_end=-2

# Load in the Metafile sheet from the Metafile TDT
xlsx_TDT = pd.ExcelFile(file_TDT)
metafile = pd.read_excel(xlsx_TDT, "Metafile")

# Create a directory for the tank
metafile['directory_tank']= directory_tdt + metafile['tdtfolder']

# Create an identical rat-test-session code
metafile['ID']=metafile['RatID'].map(str)+metafile['Test']
metafile['ID']=metafile['ID']+metafile['Testsession'].map(str)

# Create a dictionary from the metafile
dict_metafile = metafile.to_dict()

# Create lists of the metafile
list_directory_tank=metafile['directory_tank'].tolist()
list_ratid=metafile['RatID'].tolist()
list_ID=metafile['ID'].tolist()
list_blue=metafile['blue'].tolist()
list_uv=metafile['uv'].tolist()
list_virus=metafile['Virus'].tolist()
list_diet=metafile['Diet'].tolist()
list_test=metafile['Test'].tolist()
list_reward=metafile['Reward'].tolist()
list_testsession=metafile['Testsession'].tolist()
list_startbox=metafile['Startbox'].tolist()
list_light=metafile['Light'].tolist()
list_BW=metafile['BW_test'].tolist()
list_BW_gain=metafile['BW_gain'].tolist()

# Make dictionary for diet and virus
dict_diet = dict(zip(list_ratid,list_diet))
dict_virus = dict(zip(list_ratid,list_virus))
dict_id= dict(zip(list_ID,list_ratid))
dict_test=dict(zip(list_ID,list_test))
dict_testsession=dict(zip(list_ID,list_testsession))
dict_BW=dict(zip(list_ID,list_BW))
dict_BW_gain=dict(zip(list_ID,list_BW_gain))

# Analysis of the behavioral part
# Load and clean up of the data file of the rawdata for DataFrames
xlsx_beh1 = pd.ExcelFile(file_beh1)
xlsx_beh2 = pd.ExcelFile(file_beh2)
xlsx_beh3 = pd.ExcelFile(file_beh3)
xlsx_beh4 = pd.ExcelFile(file_beh4)
xlsx_beh5 = pd.ExcelFile(file_beh5)
xlsx_beh6 = pd.ExcelFile(file_beh6)
xlsx_beh7 = pd.ExcelFile(file_beh7)
xlsx_beh8 = pd.ExcelFile(file_beh8)
xlsx_beh9 = pd.ExcelFile(file_beh9)
xlsx_beh10 = pd.ExcelFile(file_beh10)

file_sheets_beh = []
for sheet in xlsx_beh1.sheet_names:
    file_sheets_beh.append(xlsx_beh1.parse(sheet))
for sheet in xlsx_beh2.sheet_names:
    file_sheets_beh.append(xlsx_beh2.parse(sheet))
for sheet in xlsx_beh3.sheet_names:
    file_sheets_beh.append(xlsx_beh3.parse(sheet))
for sheet in xlsx_beh4.sheet_names:
    file_sheets_beh.append(xlsx_beh4.parse(sheet))
for sheet in xlsx_beh5.sheet_names:
    file_sheets_beh.append(xlsx_beh5.parse(sheet))
for sheet in xlsx_beh6.sheet_names:
    file_sheets_beh.append(xlsx_beh6.parse(sheet))
for sheet in xlsx_beh7.sheet_names:
    file_sheets_beh.append(xlsx_beh7.parse(sheet))
for sheet in xlsx_beh8.sheet_names:
    file_sheets_beh.append(xlsx_beh8.parse(sheet))
for sheet in xlsx_beh9.sheet_names:
    file_sheets_beh.append(xlsx_beh9.parse(sheet))
for sheet in xlsx_beh10.sheet_names:
    file_sheets_beh.append(xlsx_beh10.parse(sheet))

dataraw = pd.concat(file_sheets_beh)
dataraw = dataraw.dropna(axis=0, how='all')


print("data loading finished")

# Fill out your short column names behind the definition a-z
A='Date_Time_Absolute_dmy_hmsf'
B='Date_dmy'
C='Time_Absolute_hms'
D='Time_Absolute_f'
E='Time_Relative_hmsf'
F='Time_Relative_hms'
G='Time_Relative_f'
H='Time_Relative_sf' # Time
I='Duration_sf'
J='Observation'
K='Event_Log'
L='Behavior'
M='Event_Type'
N='Comment'

# For the rest of the document we will use these new terms for the "important behaviors"
TIME='Time'
OBS='Observation'
BEH='Behavior'
EVENT='Event_Type'
RATID='RatID' # RatID number with virus code
RATIDRAW='RatID_raw' # number during experiment for blinding
TREAT='Treatment'
DIET='Diet'
VIRUS='Virus'
REWARD='Reward'
TEST='Test'
EXP='Experiment'
TESTREWARD='Test_Reward'

# Fill out your treatment/stimulus behind definition SA-SZ
FA='CTR-FOOD1'
FB='CTR-FOOD2'
FC='CTR-FOOD3'
FD='CTR-FOOD4'
FE='CTR-FOOD5'
FF='CAF-FOOD1'
FG='CAF-FOOD2'
FH='CAF-FOOD3'
FI='CAF-FOOD4'
FJ='CAF-FOOD5'
FK='HFHS-FOOD1'
FL='HFHS-FOOD2'
FM='HFHS-FOOD3'
FN='HFHS-FOOD4'
FO='HFHS-FOOD5'
SA='CTR-SEX1'
SB='CTR-SEX2' 
SC='CTR-SEX3'
SD='CAF-SEX1'
SE='CAF-SEX2'
SF='CAF-SEX3'
SG='HFHS-SEX1'
SH='HFHS-SEX2'
SI='HFHS-SEX3'
DA='CTR-DF1'
DB='CAF-DF1'
DC='HFHS-DF1'
RFA='CTR-REVFOOD1'
RFB='CTR-REVFOOD2'
RFC='CTR-REVFOOD3'
RFD='CAF-REVFOOD1'
RFE='CAF-REVFOOD2'
RFF='CAF-REVFOOD3'
RFG='HFHS-REVFOOD1'
RFH='HFHS-REVFOOD2'
RFI='HFHS-REVFOOD3'
RSA='CTR-REVSEX1'
RSB='CAF-REVSEX1'
RSC='HFHS-REVSEX1'
RDA='CTR-REVDF1'
RDB='CAF-REVDF1'
RDC='HFHS-REVDF1'

Stimuli_values_food = (FA,FB,FC,FD,FE,FF,FG,FH,FI,FJ,FK,FL,FM,FN,FO)
Stimuli_values_sex = (SA,SB,SC,SD,SE,SF,SG,SH,SI)
Stimuli_values_ds = (DA,DB,DC)
Stimuli_values_food_rev = (RFA,RFB,RFC,RFD,RFE,RFF,RFG,RFH,RFI)
Stimuli_values_sex_rev = (RSA,RSB,RSC)
Stimuli_values_ds_rev = (RDA,RDB,RDC)

# Fill out the test events in the test
TEA='Reward INTRO'
TEB='Light ON'
TEC='Door OPEN'
TED='Start fix cable'
TEE='Finish fix cable'
TEF='Play with cable'

# Fill out the compartments
CS='Start - left'
CR='Reward - right'

# Fill out your behavioral observations behind definition BA-BZ and BSA-BSZ
BA='Head towards door'
BB='Close to door'
BC='Exploring door'
BD='Exploring environment (+rearing)'
BE='Selfgrooming'
BF='In door open'
BG='Resting'
BH='Approach reward'
BI='Sniffing reward'
BJ='Close to reward'
BK='Anogenital sniffing'
BL='Anogenital sniffing (received by the male)'
BM='Allogrooming'
BN='Carry food'
BO='Eating'
BP='Paracopulatory'
BQ='Mount (received)'
BR='Intromission (received)'
BS='Ejaculation (received)'
BT='Lordosis 0'
BU='Lordosis 1'
BV='Lordosis 2'
BW='Lordosis 3'
BX='Rejection'
BY='other 1'
BZ='other 2'
BZA='other 3'
BZB='other 4'

# Fill in your extra behavioral calculations behind definition EA-EZ
EA='Copulations' # mounts, intromissions and ejaculations #BQ,BR,BS
EB='Lordosis' # lordosis1, lordosis2, lordosis3 #BU,BV,BW
EC='Reward_interest' # Exploring door, close to door #BB,BC
ED='Food_interaction' # eating, approach reward, sniffing reward, carrying food # BO,BH,BI,BN
EE='Sex_interaction' # lordosis, paracopulatory, approach reward, sniffing reward, sniffing anogenitally, allogrooming #BT,BU,BV,BW,BP,BH,BI,BK,BM
EF='Reward_anticipatory' # approach reward, sniffing reward, paracopulatory, sniffing anogenitally, allogrooming # BH, BI, BP,BK,BM
EG='Reward_consummatory' # eating,carrying food, lordosis #BO,BN,BT,BU,BV,BW
EH='Crossings' # start chamber, reward chamber #CS,CR

# Make a list of the standard behaviors and the to be calculated behaviors
list_sex=list((BP,BQ,BR,BS,BT,BU,BV,BW))
list_behaviors=list((BA,BB,BC,BD,BE,BF,BG,BH,BI,BJ,BK,BL,BM,BN,BO,BP,BQ,BR,BS,
                      BT,BU,BV,BW,BX))
list_behaviors_extra=list((EA,EB,EC,ED,EE,EF,EG,EH))
list_fooditems=list((ED,BN,BO))
list_sexitems=list((EE,BT,BQ,BR,BS,BU,BV,BW,BP,EA,EB))
list_beh_tdt=list((TEA,BA,BB,BC,BD,BE,BF,BG,BH,BI,BJ,BK,BL,BM,BN,BO,BP,BQ,BR,BS,BT,BU,BV,BW,BX,'Lordosis','LM','LI','LE'))
list_beh_tdt_plus=list((TEA,BA,BB,BC,BD,BE,BF,BG,BH,BI,BJ,BK,BL,BM,BN,BO,BP,BQ,BR,BS,BT,BU,BV,BW,BX,
                        'Lordosis','LM','LI','LE','Single eating','Single first eating','Single last eating',
                                    'Single middle eating','Eating starts EB','Eating ends EB','First eating in EB',
                                    'Last eating in EB','Eating middle EB','Single sex','Single first sex','Single last sex','Single middle sex',
                                                'sex starts SB','sex ends SB','First sex in SB','Last sex in SB','sex middle SB',
                                                'Single sex dart','Single first sex dart','Single last sex dart','Single middle sex dart',
                                                'sex starts SB dart','sex ends SB dart','First sex in SB dart','Last sex in SB dart','sex middle SB dart',
                                                'Single sex lor','Single first sex lor','Single last sex lor','Single middle sex lor',
                                                'sex starts SB lor','sex ends SB lor','First sex in SB lor','Last sex in SB lor','sex middle SB lor'))
list_interest_beh_prereward=['Close to door','Exploring door','Exploring environment (+rearing)',
                             'Head towards door','Paracopulatory','Reward INTRO','Selfgrooming']
list_interest_beh_reward=['Anogenital sniffing (received by the male)','Anogenital sniffing',
                          'Approach reward','Carry food','Close to reward','Eating',
                          'Ejaculation (received)','Exploring environment (+rearing)',
                          'Intromission (received)','LE','LI','LM','Lordosis 0','Lordosis 1',
                          'Lordosis 2', 'Lordosis 3','Lordosis','Mount (received)','Paracopulatory','Dart_ratio',
                          'Rejection','Selfgrooming','Sniffing reward','Reward_anticipatory','Reward_consummatory',
                          'Crossings','L1_Crossing','L1_Backcross','LQ','LQ_plus','LS','LM','LI','LE',
                          'L1_Reward_interest','Reward_interest','EB','TO','Single_eating','Single_first_eating','Single_last_eating',
                          'Single_middle_eating','Eating_starts_EB','Eating_ends_EB','First_eating_in_EB',
                          'Last_eating_in_EB','Eating_middle_EB',
                          'EB_plus','TO_plus','Single_eating_plus','Single_first_eating_plus','Single_last_eating_plus',
                          'Single_middle_eating_plus','Eating_starts_EB_plus','Eating_ends_EB_plus','First_eating_in_EB_plus',
                          'Last_eating_in_EB_plus','Eating_middle_EB_plus',
                          'SB_sex','TO_sex',
                          'Single_sex','Single_first_sex','Single_last_sex','Single_middle_sex',
                          'sex_starts_SB','sex_ends_SB','First_sex_in_SB','Last_sex_in_SB','sex_middle_SB',
                          'Single_sex_dart','Single_first_sex_dart','Single_last_sex_dart','Single_middle_sex_dart',
                          'sex_starts_SB_dart','sex_ends_SB_dart','First_sex_in_SB_dart','Last_sex_in_SB_dart','sex_middle_SB_dart',
                          'Single_sex_lor','Single_first_sex_lor','Single_last_sex_lor','Single_middle_sex_lor',
                          'sex_starts_SB_lor','sex_ends_SB_lor','First_sex_in_SB_lor','Last_sex_in_SB_lor','sex_middle_SB_lor']

list_tdt_EB=['Single eating','Single first eating','Single last eating',
            'Single middle eating','Eating starts EB','Eating ends EB','First eating in EB',
            'Last eating in EB','Eating middle EB']
list_tdt_EB_plus=['Single eating plus','Single first eating plus','Single last eating plus',
            'Single middle eating plus','Eating starts EB plus','Eating ends EB plus','First eating in EB plus',
            'Last eating in EB plus','Eating middle EB plus']
list_tdt_SB=['Single sex','Single first sex','Single last sex','Single middle sex',
            'sex starts SB','sex ends SB','First sex in SB','Last sex in SB','sex middle SB',
            'Single sex dart','Single first sex dart','Single last sex dart','Single middle sex dart',
            'sex starts SB dart','sex ends SB dart','First sex in SB dart','Last sex in SB dart','sex middle SB dart',
            'Single sex lor','Single first sex lor','Single last sex lor','Single middle sex lor',
            'sex starts SB lor','sex ends SB lor','First sex in SB lor','Last sex in SB lor','sex middle SB lor']

list_interest_beh_food=['Approach reward','Carry food','Close to reward','Eating',
                          'Exploring environment (+rearing)','Selfgrooming','Sniffing reward','Reward_anticipatory',
                          'Reward_consummatory','Crossings','L1_Crossing','L1_Backcross',
                          'L1_Reward_interest','Reward_interest','EB','TO','Single_eating','Single_first_eating','Single_last_eating',
                          'Single_middle_eating','Eating_starts_EB','Eating_ends_EB','First_eating_in_EB',
                          'Last_eating_in_EB','Eating_middle_EB',
                          'EB_plus','TO_plus','Single_eating_plus','Single_first_eating_plus','Single_last_eating_plus',
                          'Single_middle_eating_plus','Eating_starts_EB_plus','Eating_ends_EB_plus','First_eating_in_EB_plus',
                          'Last_eating_in_EB_plus','Eating_middle_EB_plus']

list_interest_beh_sex=['Anogenital sniffing (received by the male)','Anogenital sniffing',
                          'Approach reward','Close to reward',
                          'Ejaculation (received)','Exploring environment (+rearing)',
                          'Intromission (received)','LE','LI','LM','Lordosis 0','Lordosis 1',
                          'Lordosis 2', 'Lordosis 3','Lordosis','Mount (received)','Paracopulatory',
                          'L1_Paracopulatory','Dart_ratio',
                          'Rejection','Selfgrooming','Sniffing reward','Reward_anticipatory','Reward_consummatory',
                          'Crossings','L1_Crossing','L1_Backcross','LQ','LQ_plus','LS','LM','LI','LE',
                          'L1_Reward_interest','Reward_interest','SB_sex','TO_sex',
                          'Single_sex','Single_first_sex','Single_last_sex','Single_middle_sex',
                          'sex_starts_SB','sex_ends_SB','First_sex_in_SB','Last_sex_in_SB','sex_middle_SB',
                          'Single_sex_dart','Single_first_sex_dart','Single_last_sex_dart','Single_middle_sex_dart',
                          'sex_starts_SB_dart','sex_ends_SB_dart','First_sex_in_SB_dart','Last_sex_in_SB_dart','sex_middle_SB_dart',
                          'Single_sex_lor','Single_first_sex_lor','Single_last_sex_lor','Single_middle_sex_lor',
                          'sex_starts_SB_lor','sex_ends_SB_lor','First_sex_in_SB_lor','Last_sex_in_SB_lor','sex_middle_SB_lor']

list_interest_beh_sumsex=['Close to door','Exploring door','Exploring environment (+rearing)',
                             'Head towards door','Paracopulatory','Reward INTRO','Selfgrooming',
                             'Anogenital sniffing (received by the male)','Anogenital sniffing',
                          'Approach reward','Close to reward',
                          'Ejaculation (received)','Exploring environment (+rearing)',
                          'Intromission (received)','LE','LI','LM','Lordosis 0','Lordosis 1',
                          'Lordosis 2', 'Lordosis 3','Lordosis','Mount (received)','Paracopulatory','Dart_ratio',
                          'Rejection','Selfgrooming','Sniffing reward','Reward_anticipatory','Reward_consummatory',
                          'Crossings','L1_Crossing','L1_Backcross','LQ','LQ_plus','LS','LM','LI','LE',
                          'L1_Reward_interest','Reward_interest','SB_sex','TO_sex',
                          'Single_sex','Single_first_sex','Single_last_sex','Single_middle_sex',
                          'sex_starts_SB','sex_ends_SB','First_sex_in_SB','Last_sex_in_SB','sex_middle_SB',
                          'Single_sex_dart','Single_first_sex_dart','Single_last_sex_dart','Single_middle_sex_dart',
                          'sex_starts_SB_dart','sex_ends_SB_dart','First_sex_in_SB_dart','Last_sex_in_SB_dart','sex_middle_SB_dart',
                          'Single_sex_lor','Single_first_sex_lor','Single_last_sex_lor','Single_middle_sex_lor',
                          'sex_starts_SB_lor','sex_ends_SB_lor','First_sex_in_SB_lor','Last_sex_in_SB_lor','sex_middle_SB_lor']

list_behmark=[BO,BP,BU,BV,BW]

list_relevant_behaviors_food=[BI,BN,BO]
list_relevant_behaviors_sex=[BI,BK,BP,BQ,BR,BS,BU,BV,BW]
list_relevant_behaviors=[BI,BN,BO,BK,BP,BQ,BR,BS,BU,BV,BW]

list_rewardid=['PRIMREWARD1','PRIMREWARD3','PRIMREWARD5','SECREWARD1','SECREWARD2','SECREWARD3',
               'DISREWARD1','PRIMREWARD_rev1','PRIMREWARD_rev3','SECREWARD_rev1']

# Make a list of the behaviors in each category
list_EA=list((BQ,BR,BS))
list_EB=list((BU,BV,BW))
list_EC=list((BB,BC))
list_ED=list((BO,BH,BI,BN))
list_EE=list((BT,BU,BV,BW,BP,BH,BI,BK,BM))
list_EF=list((BH, BI, BP,BK,BM))
list_EG=list((BO,BN,BT,BU,BV,BW))
list_EH=list((CR,CS))

# Create a dictionary of lists of the extra behavior lists
dict_list_extra={EA:list_EA,EB:list_EB,EC:list_EC,ED:list_ED,EE:list_EE,EF:list_EF,EG:list_EG}

# Rename columns (add or remove letters according to number of columns)
dataraw.columns = [A,B,C,D,E,F,G,H,I,J,K,L,M,N]
dataraw.columns=[A,B,C,D,E,F,G,TIME,I,OBS,K,BEH,EVENT,N]

# Make a new datafile with selected columns
data_full=dataraw[[TIME,OBS,BEH,EVENT]]

# Make a column for the experiment and RatID_raw (this is the number used for the rats)
data_full=data_full.assign(RatID =lambda x: data_full.Observation.str.split('_').str[-1])
data_full=data_full.assign(Experiment =lambda x: data_full.Observation.str.split('_').str[0])
data_full=data_full.assign(Test =lambda x: data_full.Experiment.str[-1])
data_full=data_full.assign(Reward =lambda x: data_full.Experiment.str[:-1])

# Use metafile to fill in right virus, diets, and rewards
# Make column for reward
data_full[REWARD]=np.where(data_full[REWARD]=='F','Food',data_full[REWARD])
data_full[REWARD]=np.where(data_full[REWARD]=='S','Sex',data_full[REWARD])
data_full[REWARD]=np.where(data_full[REWARD]=='D','Chow',data_full[REWARD])
data_full[REWARD]=np.where(data_full[REWARD]=='RF','Foodrev',data_full[REWARD])
data_full[REWARD]=np.where(data_full[REWARD]=='RS','Sexrev',data_full[REWARD])
data_full[REWARD]=np.where(data_full[REWARD]=='RD','Chowrev',data_full[REWARD])

# Make a column for the diet and virus
data_full[DIET]=pd.to_numeric(data_full[RATID])
data_full[DIET]=data_full[DIET].map(dict_diet)

data_full[VIRUS]=pd.to_numeric(data_full[RATID])
data_full[VIRUS]=data_full[VIRUS].map(dict_virus)

# Make a column for  testreward moment
data_full[TESTREWARD]=data_full[REWARD]+data_full[TEST]

# Delete the rows that "end" a behavior
# Drop a row by condition
data_full=data_full[data_full.Event_Type != 'State stop']

# Clean up the file by selecting relevant columns and reorganize
data_full=data_full.drop(columns=[EVENT])
data_full=data_full[[OBS,EXP,RATID,DIET,VIRUS,TEST,REWARD,TESTREWARD,TIME,BEH]]


# Delete the rows with the excluded animals
for i in list_excl:
    data_full=data_full[data_full.RatID != i]

# Create an identical rat-test-session code
data_full['ID_pre']=np.where(data_full[REWARD]=='Food','PRIMREWARD','SECREWARD')
data_full['ID_pre']=np.where(data_full[REWARD]=='Foodrev','PRIMREWARD_rev',data_full['ID_pre'])
data_full['ID_pre']=np.where(data_full[REWARD]=='Sexrev','SECREWARD_rev',data_full['ID_pre'])
data_full['ID_pre']=np.where(data_full[REWARD]=='Chow','DISREWARD',data_full['ID_pre'])
data_full['ID_pre']=np.where(data_full[REWARD]=='Chowrev','DISREWARD_rev',data_full['ID_pre'])
data_full['ID']=data_full[RATID].map(str)+data_full['ID_pre']
data_full['ID']=data_full['ID']+data_full[TEST].map(str)

# Delete the rows with excluded animals for sex-tests
for s in list_excl_sex:
    data_full=data_full[(data_full.ID_pre != 'SECREWARD') | ((data_full.ID_pre == 'SECREWARD') & (data_full.RatID != s))]
    
# Create a dictionary of the light-times per test-rat
data_full['LIGHT']=np.where(data_full[BEH]==TEB,data_full[TIME],np.NAN)

dict_light={}
list_id=data_full['ID'].tolist()
set_id=set(list_id)
list_id2=list(set_id)

for key in list_id2:
    dict_light[key]={}
   
data_light = data_full[data_full[BEH].isin([TEB])]
     
# Fill in the dictionaries with the light times
for key,value in dict_light.items():
    temp=[]
    for index, row in data_light.iterrows():
        if row['ID']==key:
            temp.append(row[TIME])
                        
        dict_light[key]=temp


# Calculate the durations of each behavior
data_full= data_full.sort_values(by=[OBS,TIME])
data_full['time_diff'] = data_full[TIME].diff()

# Create a column with the start and times for behaviors
data_full['Time_cop'] = data_full.groupby('ID')[TIME].shift()
data_full['Time_next'] = data_full.groupby('ID')[TIME].shift(-1)
data_full['Beh_start'] = data_full[TIME]
data_full['Beh_end'] = np.where(data_full['Time_next'] > 0,data_full['Time_next'] ,Timetest_total)
data_full['Next_beh'] = data_full.groupby('ID')[BEH].shift(-1)

# Sort the dataset for further analysis
data_full = data_full.sort_values(by=[OBS,TIME], ascending = True)
data_full = data_full.reset_index(drop=True)

# Delete the times there were the RatID of next rat starts
data_full.loc[data_full.RatID != data_full.RatID.shift(), 'time_diff'] = None

# Mark beginning and end per rat
data_full['obs_num'] = data_full.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
data_full = data_full.sort_values(by=[OBS,TIME], ascending = False)
data_full['obs_num_back'] = data_full.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
data_full = data_full.sort_values(by=[OBS,TIME])

# Now put the time differences to the right behavior in column 'durations'
data_full['durations_pre'] = data_full.time_diff.shift(-1)
data_full['durations_pre'] = np.where((data_full['obs_num_back']==1),(Timetest_total-data_full[TIME]),data_full['durations_pre'])

# Fix the time of the  by adding it the previous behavior
data_full['durations_fix'] = data_full.durations_pre.shift(-1)
data_full['chamberduration_fix'] = data_full.Behavior.shift(-1)
data_full['durations'] = np.where(((data_full['chamberduration_fix']==CR)|(data_full['chamberduration_fix']==CS)),(data_full['durations_pre']+data_full['durations_fix']),data_full['durations_pre'])

# Mark the phases with identifying numbers
data_full['Phase_mark']=np.where(data_full[BEH]==TEA,999,np.NaN)
data_full['Phase_mark']=np.where(data_full[BEH]==TEB,888,data_full['Phase_mark'])
data_full['Phase_mark']=np.where(data_full[BEH]==TEC,777,data_full['Phase_mark'])
data_full['Phase_mark']=data_full.groupby(['ID'], sort=False)['Phase_mark'].fillna(method="backfill")
data_full['Phase_mark']=np.where(data_full[BEH]==TEC,666,data_full['Phase_mark'])
data_full['Phase_mark']=data_full.groupby(['ID'], sort=False)['Phase_mark'].fillna(method="ffill")

# Create a dictionary that matches the identifying numbers to the phases
dict_phases={999:'BASELINE',888:'INTRO',777:'ANTICIPATORY',666:'REWARD'}

# Code the phases with words
data_full['Phase_mark'] =data_full['Phase_mark'].map(dict_phases)

# Mark the pre-reward phase
data_full['Reward_mark']=np.where(data_full['Phase_mark']!='REWARD','PREREWARD','REWARD')
                                      
# Mark the presence in which chamber
data_full['Chamber_mark']=np.where(data_full[BEH]==CS,10,np.NaN)
data_full['Chamber_mark']=np.where(data_full[BEH]==CR,20,data_full['Chamber_mark'])
data_full['Chamber_mark']=data_full.groupby(['ID'], sort=False)['Chamber_mark'].fillna(method="ffill")

dict_chamber={10:'SC',20:'RC'}
data_full['Chamber_mark'] =data_full['Chamber_mark'].map(dict_chamber)

# # Make new dataframes for each phase
data_T = data_full.copy()
data_B = data_full[data_full['Phase_mark'].isin(['BASELINE'])]
data_I = data_full[data_full['Phase_mark'].isin(['INTRO'])]
data_A = data_full[data_full['Phase_mark'].isin(['ANTICIPATORY'])]
data_P = data_full[data_full['Reward_mark'].isin(['PREREWARD'])]
data_R = data_full[data_full['Phase_mark'].isin(['REWARD'])]

# Create list with phases
list_phases = ['B','I','A','P','R']

print("dataprep finished")    

df_data={'all':data_T,'B':data_B,'I':data_I,'A':data_A,'P':data_P,'R':data_R}

# # Save the dataframes to excel for check
# writer_data = pd.ExcelWriter(out_path4, engine='xlsxwriter')
# data_full.to_excel(writer_data, sheet_name='data_t')
# # data_B.to_excel(writer_data, sheet_name='data_b')
# # data_I.to_excel(writer_data, sheet_name='data_i')
# # data_A.to_excel(writer_data, sheet_name='data_a')
# # data_P.to_excel(writer_data, sheet_name='data_p')
# # data_R.to_excel(writer_data, sheet_name='data_r')
# writer_data.save()
# writer_data.close()

def dataprep (data):
    """
    Parameters
    ----------
    data : DataFrame 
        Add the dataframe for analysis
        e.g. data_R

    Returns
    -------
    data : DataFrame
        Returns a new dataframe with all columns needed later to retrieve the results
    """

    # Mark beginning per rat
    data = data.sort_values(by=[OBS,TIME])
    data['obs_num'] = data.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    
    # Make a new column that makes an unique name for the behaviors per rat
    data['beh_num_trick'] = data[BEH].map(str) + data['ID']
    
    # Number the behaviors per behavior per rat
    data['beh_num'] = data.groupby('beh_num_trick')[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    
    # # Create a new dataframe with only the Eating bout related behaviors
    data = data.sort_values(by=[OBS,TIME], ascending = False)
    data['obs_num_back'] = data.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    data = data.sort_values(by=[OBS,TIME])

    data['new_beh_mark']=np.where(data[BEH]==BO,BO,'break')
    data['new_beh_mark']=np.where(((data[BEH]==CS)|(data[BEH]==CR)),'ignore',data['new_beh_mark'])
    data['new_beh_mark']=np.where(((data[BEH]==BH)|(data[BEH]==BI)|(data[BEH]==BJ)|(data[BEH]==BN)),'bout',data['new_beh_mark'])
    data['EB_behavior']=np.where((data['obs_num']==1),"fix",data['new_beh_mark'])
    data['Next_behavior']=data.groupby('ID')['EB_behavior'].shift(-1)
    data['Previous_behavior']=data.groupby('ID')['new_beh_mark'].shift(1)
    data['Previous_behavior']=np.where((data['obs_num']==1),"fix",data['Previous_behavior'])
    data['Next_behavior']=np.where((data['obs_num_back']==1),"fix",data['Next_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']=='bout')&(data['Next_behavior']!='break')&(data['Previous_behavior']=='break')),"Start bout",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']=='bout')&(data['Next_behavior']=='break')&(data['Previous_behavior']!='break')),"End bout",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']==BO)&(data['Next_behavior']!=BO)&(data['Next_behavior']!='bout')&(data['Next_behavior']!='ignore')),"End eating",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']==BO)&(data['Previous_behavior']!=BO)&(data['Previous_behavior']!='bout')&(data['Previous_behavior']!='ignore')),"Start eating",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']==BO)&(data['Next_behavior']=='break')&(data['Previous_behavior']=='break')),"Single eating",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']=='break')&((data['Previous_behavior']=='ignore'))),"Cross break",data['EB_behavior'])
    data['EB_behavior']=np.where(((data['EB_behavior']=='break')&((data['Next_behavior']=='ignore'))),"Cross break",data['EB_behavior'])
    data['Previous_behavior']=data.groupby('ID')['EB_behavior'].shift(1)
    data['Previous_behavior']=np.where((data['obs_num']==1),"fix",data['Previous_behavior'])
    data['Previous_behavior2']=data.groupby('ID')['Previous_behavior'].shift(1)
    data['EB_behavior']=np.where(((data['EB_behavior']=='bout')&((data['Previous_behavior2']=='Cross break'))),"Start bout",data['EB_behavior'])

    # Create a small df_EBframe of only bout behaviors needed for further analysis
    df_EB=data.loc[(data['EB_behavior']=='Single eating')|(data['EB_behavior']=='Start eating')|(data['EB_behavior']=='End eating')|(data['EB_behavior']==BO)|
                   (data['EB_behavior']=='Start bout')|(data['EB_behavior']=='End bout')|(data['EB_behavior']=='Cross break')]
    df_EB['obs_num'] = df_EB.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_EB = df_EB.sort_values(by=[OBS,TIME], ascending = False)
    df_EB['obs_num_back'] = df_EB.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_EB = df_EB.sort_values(by=[OBS,TIME])
    df_EB['temp_behavior']=np.where((df_EB['obs_num']==1),"fix",df_EB['EB_behavior'])
    df_EB['Next_behavior']=df_EB.groupby(RATID)['temp_behavior'].shift(-1)
    df_EB['Previous_behavior']=df_EB.groupby(RATID)['EB_behavior'].shift(1)
    df_EB['Previous_behavior']=np.where((df_EB['obs_num']==1),"fix",df_EB['Previous_behavior'])
    df_EB['Next_behavior']=np.where((df_EB['obs_num_back']==1),"fix",df_EB['Next_behavior'])

    # Make column that marks the eating behavior right
    df_EB['EB_Eating_mark']=np.where(df_EB['EB_behavior']=='Single eating','Single eating','')
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Cross break')&(df_EB['Previous_behavior']=='Cross break')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Cross break')&(df_EB['Previous_behavior']==BO)),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Cross break')&(df_EB['Previous_behavior']=='End bout')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Cross break')&(df_EB['Previous_behavior']=='Start bout')),'Single last eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='Cross break')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']==BO)),'Middle eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='End bout')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='fix')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='Start bout')),'First eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='End eating')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']==BO)&(df_EB['Previous_behavior']=='Start eating')),'Middle eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='Cross break')),'Single first eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']==BO)),'Last eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='End bout')),'Single first eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='fix')),'Single first eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='Start bout')),'Single middle eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='End eating')),'Single first eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End bout')&(df_EB['Previous_behavior']=='Start eating')),'Last eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='fix')&(df_EB['Previous_behavior']==BO)),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='fix')&(df_EB['Previous_behavior']=='End bout')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='fix')&(df_EB['Previous_behavior']=='Start bout')),'Single last eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start bout')&(df_EB['Previous_behavior']=='Cross break')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start bout')&(df_EB['Previous_behavior']==BO)),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start bout')&(df_EB['Previous_behavior']=='fix')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start bout')&(df_EB['Previous_behavior']=='Start bout')),'Single last eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='Cross break')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']==BO)),'Middle eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='End bout')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='End eating')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='fix')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='Start bout')),'First eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='End eating')&(df_EB['Previous_behavior']=='Start eating')),'Middle eating in EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start eating')&(df_EB['Previous_behavior']=='Cross break')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']==BO)&(df_EB['Next_behavior']=='Start eating')&(df_EB['Previous_behavior']==BO)),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='Cross break')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']==BO)),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='End bout')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='End eating')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='Start bout')),'Single last eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='Start eating')),'Eating ends EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='End eating')&(df_EB['Previous_behavior']=='fix')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='Cross break')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']==BO)),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='End bout')),'Single first eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='End eating')),'Eating starts EB',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='Start bout')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='Start eating')),'Single eating',df_EB['EB_Eating_mark'])
    df_EB['EB_Eating_mark']=np.where(((df_EB['EB_behavior']=='Start eating')&(df_EB['Next_behavior']=='fix')),'Single eating',df_EB['EB_Eating_mark'])

    # Write the markers back in the real dataframe
    # Place the index numbers in lists
    list_idx_singleeating=df_EB.index[(df_EB['EB_Eating_mark']=='Single eating')].tolist()
    list_idx_singlefirsteating=df_EB.index[(df_EB['EB_Eating_mark']=='Single first eating')].tolist()
    list_idx_singlelasteating=df_EB.index[(df_EB['EB_Eating_mark']=='Single last eating')].tolist()
    list_idx_singlemiddleeating=df_EB.index[(df_EB['EB_Eating_mark']=='Single middle eating')].tolist()
    
    list_idx_eatingstartEB=df_EB.index[(df_EB['EB_Eating_mark']=='Eating starts EB')].tolist()
    list_idx_eatingendEB=df_EB.index[(df_EB['EB_Eating_mark']=='Eating ends EB')].tolist()
    list_idx_firsteatingEB=df_EB.index[(df_EB['EB_Eating_mark']=='First eating in EB')].tolist()
    list_idx_lasteatingEB=df_EB.index[(df_EB['EB_Eating_mark']=='Last eating in EB')].tolist()
    list_idx_eatingmiddleEB=df_EB.index[(df_EB['EB_Eating_mark']=='Middle eating in EB')].tolist()

    # Make a column for EB_Eating_mark
    data['EB_Eating_mark']=NaN    
    # Replace the "Eating" for the actual behavior it was
    for i in list_idx_singleeating:
        data.at[i,'EB_Eating_mark']='Single eating'
    for i in list_idx_singlefirsteating:
        data.at[i,'EB_Eating_mark']='Single first eating'
    for i in list_idx_singlelasteating:
        data.at[i,'EB_Eating_mark']='Single last eating'
    for i in list_idx_singlemiddleeating:
        data.at[i,'EB_Eating_mark']='Single middle eating'

    for i in list_idx_eatingstartEB:
        data.at[i,'EB_Eating_mark']='Eating starts EB'
    for i in list_idx_eatingendEB:
        data.at[i,'EB_Eating_mark']='Eating ends EB'
    for i in list_idx_firsteatingEB:
        data.at[i,'EB_Eating_mark']='First eating in EB'
    for i in list_idx_lasteatingEB:
        data.at[i,'EB_Eating_mark']='Last eating in EB'
    for i in list_idx_eatingmiddleEB:
        data.at[i,'EB_Eating_mark']='Middle eating in EB'

    # Mark the time of the start and end of each eating bout
    data['Time_start_eating_bout']=np.where(((data['EB_Eating_mark']=='Single eating')|(data['EB_Eating_mark']=='Single first eating')|
                                              (data['EB_Eating_mark']=='Single last eating')|(data['EB_Eating_mark']=='Single middle eating')|
                                              (data['EB_Eating_mark']=='Eating starts EB')|(data['EB_Eating_mark']=='First eating in EB')),
                                            data['Beh_start'],NaN)
    data['Time_start_eating_bout']=data.groupby(['ID'], sort=False)['Time_start_eating_bout'].fillna(method="backfill")
    
    data['Time_end_eating_bout']=np.where(((data['EB_Eating_mark']=='Single eating')|(data['EB_Eating_mark']=='Single first eating')|
                                              (data['EB_Eating_mark']=='Single last eating')|(data['EB_Eating_mark']=='Single middle eating')|
                                              (data['EB_Eating_mark']=='Eating ends EB')|(data['EB_Eating_mark']=='Last eating in EB')),
                                              data['Beh_end'],NaN)
    data['Time_end_eating_bout']=data.groupby(['ID'], sort=False)['Time_end_eating_bout'].fillna(method="backfill")

    # Get the duration of the eating bout, marked next to the start of the eating bout
    data['Duration_eating_bout']=np.where(((data['EB_Eating_mark']=="Eating starts EB")|(data['EB_Eating_mark']=="First eating in EB")),((data['Time_end_eating_bout'])-(data['Time_start_eating_bout'])),NaN)
    data['Duration_eating_bout']=np.where(((data['EB_Eating_mark']=='Single eating')|(data['EB_Eating_mark']=='Single first eating')|
                                              (data['EB_Eating_mark']=='Single last eating')|(data['EB_Eating_mark']=='Single middle eating')),data['durations'],data['Duration_eating_bout'])
    
    # Get column with the start of next mount bout
    data['Start_next_EB']=data.groupby(['ID'], sort=False)['Time_start_eating_bout'].shift(-1)
    
    # Get the duration of the time out
    data['Duration_time_out']=np.where(((data['EB_Eating_mark']=="Eating ends EB")|(data['EB_Eating_mark']=="Last eating in EB")|
                                        (data['EB_Eating_mark']=='Single eating')|(data['EB_Eating_mark']=='Single first eating')|
                                                                                  (data['EB_Eating_mark']=='Single last eating')|(data['EB_Eating_mark']=='Single middle eating')),
                                              (data['Start_next_EB']-data['Time_end_eating_bout']),NaN)
    
    # Count the mount bouts
    data['Eating_bout_count']=np.where(((data['EB_Eating_mark']=="Eating starts EB")|(data['EB_Eating_mark']=="First eating in EB")|
                                        (data['EB_Eating_mark']=='Single eating')|(data['EB_Eating_mark']=='Single first eating')|
                                              (data['EB_Eating_mark']=='Single last eating')|(data['EB_Eating_mark']=='Single middle eating')),
                                        1,NaN)
    data['OBS_EB_count'] = data['Eating_bout_count'].map(str) + data['ID'] 
    data['Eating_bout_num'] = data.groupby('OBS_EB_count')['Eating_bout_count'].transform(lambda x: np.arange(1, len(x) + 1))
    
    # Calculate the interval between the start of mount bouts
    data['Interval_EB']=np.where((data['Duration_eating_bout']>0),(data['Start_next_EB']-data['Time_start_eating_bout']),NaN)

    ###############
    # The same as above, but now with carrying food & eating as events
    data['new_beh_mark2']=np.where(((data[BEH]==BO) | (data[BEH]==BN)),BO,'break')
    data['new_beh_mark2']=np.where(((data[BEH]==CS)|(data[BEH]==CR)),'ignore',data['new_beh_mark2'])
    data['new_beh_mark2']=np.where(((data[BEH]==BH)|(data[BEH]==BI)|(data[BEH]==BJ)),'bout',data['new_beh_mark2'])
    data['EB_behavior2']=np.where((data['obs_num']==1),"fix",data['new_beh_mark2'])
    data['Next_behavior2']=data.groupby('ID')['EB_behavior2'].shift(-1)
    data['Previous_behavior2']=data.groupby('ID')['new_beh_mark2'].shift(1)
    data['Previous_behavior2']=np.where((data['obs_num']==1),"fix",data['Previous_behavior2'])
    data['Next_behavior2']=np.where((data['obs_num_back']==1),"fix",data['Next_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']=='bout')&(data['Next_behavior2']!='break')&(data['Previous_behavior2']=='break')),"Start bout",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']=='bout')&(data['Next_behavior2']=='break')&(data['Previous_behavior2']!='break')),"End bout",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']==BO)&(data['Next_behavior2']!=BO)&(data['Next_behavior2']!='bout')&(data['Next_behavior2']!='ignore')),"End eating",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']==BO)&(data['Previous_behavior2']!=BO)&(data['Previous_behavior2']!='bout')&(data['Previous_behavior2']!='ignore')),"Start eating",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']==BO)&(data['Next_behavior2']=='break')&(data['Previous_behavior2']=='break')),"Single eating",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']=='break')&((data['Previous_behavior2']=='ignore'))),"Cross break",data['EB_behavior2'])
    data['EB_behavior2']=np.where(((data['EB_behavior2']=='break')&((data['Next_behavior2']=='ignore'))),"Cross break",data['EB_behavior2'])
    data['Previous_behavior2']=data.groupby('ID')['EB_behavior2'].shift(1)
    data['Previous_behavior2']=np.where((data['obs_num']==1),"fix",data['Previous_behavior2'])
    data['Previous_behavior22']=data.groupby('ID')['Previous_behavior2'].shift(1)
    data['EB_behavior2']=np.where(((data['EB_behavior2']=='bout')&((data['Previous_behavior22']=='Cross break'))),"Start bout",data['EB_behavior2'])

    # Create a small df_EB2frame of only bout behaviors needed for further analysis
    df_EB2=data.loc[(data['EB_behavior2']=='Single eating')|(data['EB_behavior2']=='Start eating')|(data['EB_behavior2']=='End eating')|(data['EB_behavior2']==BO)|
                   (data['EB_behavior2']=='Start bout')|(data['EB_behavior2']=='End bout')|(data['EB_behavior2']=='Cross break')]
    df_EB2['obs_num'] = df_EB2.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_EB2 = df_EB2.sort_values(by=[OBS,TIME], ascending = False)
    df_EB2['obs_num_back'] = df_EB2.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_EB2 = df_EB2.sort_values(by=[OBS,TIME])
    df_EB2['temp_behavior2']=np.where((df_EB2['obs_num']==1),"fix",df_EB2['EB_behavior2'])
    df_EB2['Next_behavior2']=df_EB2.groupby(RATID)['temp_behavior2'].shift(-1)
    df_EB2['Previous_behavior2']=df_EB2.groupby(RATID)['EB_behavior2'].shift(1)
    df_EB2['Previous_behavior2']=np.where((df_EB2['obs_num']==1),"fix",df_EB2['Previous_behavior2'])
    df_EB2['Next_behavior2']=np.where((df_EB2['obs_num_back']==1),"fix",df_EB2['Next_behavior2'])

    # Make column that marks the eating behavior right
    df_EB2['EB_Eating_mark2']=np.where(df_EB2['EB_behavior2']=='Single eating','Single eating','')
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Cross break')&(df_EB2['Previous_behavior2']=='Cross break')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Cross break')&(df_EB2['Previous_behavior2']==BO)),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Cross break')&(df_EB2['Previous_behavior2']=='End bout')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Cross break')&(df_EB2['Previous_behavior2']=='Start bout')),'Single last eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='Cross break')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']==BO)),'Middle eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='End bout')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='fix')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='Start bout')),'First eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='End eating')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']==BO)&(df_EB2['Previous_behavior2']=='Start eating')),'Middle eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='Cross break')),'Single first eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']==BO)),'Last eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='End bout')),'Single first eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='fix')),'Single first eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='Start bout')),'Single middle eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='End eating')),'Single first eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End bout')&(df_EB2['Previous_behavior2']=='Start eating')),'Last eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='fix')&(df_EB2['Previous_behavior2']==BO)),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='fix')&(df_EB2['Previous_behavior2']=='End bout')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='fix')&(df_EB2['Previous_behavior2']=='Start bout')),'Single last eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start bout')&(df_EB2['Previous_behavior2']=='Cross break')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start bout')&(df_EB2['Previous_behavior2']==BO)),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start bout')&(df_EB2['Previous_behavior2']=='fix')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start bout')&(df_EB2['Previous_behavior2']=='Start bout')),'Single last eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Cross break')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']==BO)),'Middle eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='End bout')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='End eating')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='fix')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Start bout')),'First eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Start eating')),'Middle eating in EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start eating')&(df_EB2['Previous_behavior2']=='Cross break')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']==BO)&(df_EB2['Next_behavior2']=='Start eating')&(df_EB2['Previous_behavior2']==BO)),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Cross break')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']==BO)),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='End bout')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='End eating')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Start bout')),'Single last eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='Start eating')),'Eating ends EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='End eating')&(df_EB2['Previous_behavior2']=='fix')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='Cross break')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']==BO)),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='End bout')),'Single first eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='End eating')),'Eating starts EB',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='Start bout')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='Start eating')),'Single eating',df_EB2['EB_Eating_mark2'])
    df_EB2['EB_Eating_mark2']=np.where(((df_EB2['EB_behavior2']=='Start eating')&(df_EB2['Next_behavior2']=='fix')),'Single eating',df_EB2['EB_Eating_mark2'])

    # Write the markers back in the real dataframe
    # Place the index numbers in lists
    list_idx_singleeating2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Single eating')].tolist()
    list_idx_singlefirsteating2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Single first eating')].tolist()
    list_idx_singlelasteating2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Single last eating')].tolist()
    list_idx_singlemiddleeating2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Single middle eating')].tolist()
    
    list_idx_eatingstartEB2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Eating starts EB')].tolist()
    list_idx_eatingendEB2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Eating ends EB')].tolist()
    list_idx_firsteatingEB2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='First eating in EB')].tolist()
    list_idx_lasteatingEB2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Last eating in EB')].tolist()
    list_idx_eatingmiddleEB2=df_EB2.index[(df_EB2['EB_Eating_mark2']=='Middle eating in EB')].tolist()

    # Make a column for EB_Eating_mark2
    data['EB_Eating_mark2']=NaN    
    # Replace the "Eating" for the actual behavior it was
    for i in list_idx_singleeating2:
        data.at[i,'EB_Eating_mark2']='Single eating'
    for i in list_idx_singlefirsteating2:
        data.at[i,'EB_Eating_mark2']='Single first eating'
    for i in list_idx_singlelasteating2:
        data.at[i,'EB_Eating_mark2']='Single last eating'
    for i in list_idx_singlemiddleeating2:
        data.at[i,'EB_Eating_mark2']='Single middle eating'

    for i in list_idx_eatingstartEB2:
        data.at[i,'EB_Eating_mark2']='Eating starts EB'
    for i in list_idx_eatingendEB2:
        data.at[i,'EB_Eating_mark2']='Eating ends EB'
    for i in list_idx_firsteatingEB2:
        data.at[i,'EB_Eating_mark2']='First eating in EB'
    for i in list_idx_lasteatingEB2:
        data.at[i,'EB_Eating_mark2']='Last eating in EB'
    for i in list_idx_eatingmiddleEB2:
        data.at[i,'EB_Eating_mark2']='Middle eating in EB'

    # Mark the time of the start and end of each eating bout
    data['Time_start_eating_bout2']=np.where(((data['EB_Eating_mark2']=='Single eating')|(data['EB_Eating_mark2']=='Single first eating')|
                                              (data['EB_Eating_mark2']=='Single last eating')|(data['EB_Eating_mark2']=='Single middle eating')|
                                              (data['EB_Eating_mark2']=='Eating starts EB')|(data['EB_Eating_mark2']=='First eating in EB')),
                                            data['Beh_start'],NaN)
    data['Time_start_eating_bout2']=data.groupby(['ID'], sort=False)['Time_start_eating_bout2'].fillna(method="backfill")
    
    data['Time_end_eating_bout2']=np.where(((data['EB_Eating_mark2']=='Single eating')|(data['EB_Eating_mark2']=='Single first eating')|
                                              (data['EB_Eating_mark2']=='Single last eating')|(data['EB_Eating_mark2']=='Single middle eating')|
                                              (data['EB_Eating_mark2']=='Eating ends EB')|(data['EB_Eating_mark2']=='Last eating in EB')),
                                              data['Beh_end'],NaN)
    data['Time_end_eating_bout2']=data.groupby(['ID'], sort=False)['Time_end_eating_bout2'].fillna(method="backfill")

    # Get the duration of the eating bout, marked next to the start of the eating bout
    data['Duration_eating_bout2']=np.where(((data['EB_Eating_mark2']=="Eating starts EB")|(data['EB_Eating_mark2']=="First eating in EB")),((data['Time_end_eating_bout2'])-(data['Time_start_eating_bout2'])),NaN)
    data['Duration_eating_bout2']=np.where(((data['EB_Eating_mark2']=='Single eating')|(data['EB_Eating_mark2']=='Single first eating')|
                                              (data['EB_Eating_mark2']=='Single last eating')|(data['EB_Eating_mark2']=='Single middle eating')),data['durations'],data['Duration_eating_bout2'])
    
    # Get column with the start of next mount bout
    data['Start_next_EB2']=data.groupby(['ID'], sort=False)['Time_start_eating_bout2'].shift(-1)
    
    # Get the duration of the time out
    data['Duration_time_out2']=np.where(((data['EB_Eating_mark2']=="Eating ends EB")|(data['EB_Eating_mark2']=="Last eating in EB")|
                                        (data['EB_Eating_mark2']=='Single eating')|(data['EB_Eating_mark2']=='Single first eating')|
                                                                                  (data['EB_Eating_mark2']=='Single last eating')|(data['EB_Eating_mark2']=='Single middle eating')),
                                              (data['Start_next_EB2']-data['Time_end_eating_bout2']),NaN)
    
    # Count the mount bouts
    data['Eating_bout_count2']=np.where(((data['EB_Eating_mark2']=="Eating starts EB")|(data['EB_Eating_mark2']=="First eating in EB")|
                                        (data['EB_Eating_mark2']=='Single eating')|(data['EB_Eating_mark2']=='Single first eating')|
                                              (data['EB_Eating_mark2']=='Single last eating')|(data['EB_Eating_mark2']=='Single middle eating')),
                                        1,NaN)
    data['OBS_EB_count2'] = data['Eating_bout_count2'].map(str) + data['ID'] 
    data['Eating_bout_num2'] = data.groupby('OBS_EB_count2')['Eating_bout_count2'].transform(lambda x: np.arange(1, len(x) + 1))
    
    # Calculate the interval between the start of mount bouts
    data['Interval_EB2']=np.where((data['Duration_eating_bout2']>0),(data['Start_next_EB2']-data['Time_start_eating_bout2']),NaN)

    # Create new column for EB_Eating_mark2 to match eating or carrying food
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Single eating')),'Single carry food',data['EB_Eating_mark2'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Single first eating')),'Single first carry food',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Single last eating')),'Single last carry food',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Single middle eating')),'Single middle carry food',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Eating starts EB')),'Carry food starts EB',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Eating ends EB')),'Carry food ends EB',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='First eating in EB')),'First carry food in EB',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Last eating in EB')),'Last carry food in EB',data['EB_Eating_mark2_split'])
    data['EB_Eating_mark2_split']=np.where(((data[BEH]==BN)&(data['EB_Eating_mark2']=='Middle eating in EB')),'Middle carry food in EB',data['EB_Eating_mark2_split'])
    
    ##########################
    # # Create a new dataframe with only the Copulation bout related behaviors -> lordosis0 is part of bout, but not marked!
    data['new_sex_mark']=np.where(((data[BEH]==BP)|(data[BEH]==BU)|(data[BEH]==BV)|(data[BEH]==BW)),'sex','break')
    data['new_sex_mark']=np.where(((data[BEH]==CS)|(data[BEH]==CR)),'ignore',data['new_sex_mark'])
    data['new_sex_mark']=np.where(((data[BEH]==BT)|(data[BEH]==BH)|(data[BEH]==BI)|(data[BEH]==BJ)|(data[BEH]==BK)|(data[BEH]==BL)|
                                    (data[BEH]==BQ)|(data[BEH]==BR)|(data[BEH]==BS)),'bout',data['new_sex_mark'])
    data['SB_behavior']=np.where((data['obs_num']==1),"fix",data['new_sex_mark'])
    data['Next_behavior_sex']=data.groupby('ID')['SB_behavior'].shift(-1)
    data['Previous_behavior_sex']=data.groupby('ID')['new_sex_mark'].shift(1)
    data['Previous_behavior_sex']=np.where((data['obs_num']==1),"fix",data['Previous_behavior_sex'])
    data['Next_behavior_sex']=np.where((data['obs_num_back']==1),"fix",data['Next_behavior_sex'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='bout')&(data['Next_behavior_sex']!='break')&(data['Previous_behavior_sex']=='break')),"Start bout",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='bout')&(data['Next_behavior_sex']=='break')&(data['Previous_behavior_sex']!='break')),"End bout",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='sex')&(data['Next_behavior_sex']!='sex')&(data['Next_behavior_sex']!='bout')&(data['Next_behavior_sex']!='ignore')),"End sex",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='sex')&(data['Previous_behavior_sex']!='sex')&(data['Previous_behavior_sex']!='bout')&(data['Previous_behavior_sex']!='ignore')),"Start sex",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='sex')&(data['Next_behavior_sex']=='break')&(data['Previous_behavior_sex']=='break')),"Single sex",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='break')&((data['Previous_behavior_sex']=='ignore'))),"Cross break",data['SB_behavior'])
    data['SB_behavior']=np.where(((data['SB_behavior']=='break')&((data['Next_behavior_sex']=='ignore'))),"Cross break",data['SB_behavior'])
    data['Previous_behavior_sex']=data.groupby('ID')['SB_behavior'].shift(1)
    data['Previous_behavior_sex']=np.where((data['obs_num']==1),"fix",data['Previous_behavior_sex'])
    data['Previous_behavior_sex2']=data.groupby('ID')['Previous_behavior_sex'].shift(1)
    data['SB_behavior']=np.where(((data['SB_behavior']=='bout')&((data['Previous_behavior_sex2']=='Cross break'))),"Start bout",data['SB_behavior'])

    # Create a small df_SBframe of only bout behaviors needed for further analysis
    df_SB=data.loc[(data['SB_behavior']=='Single sex')|(data['SB_behavior']=='Start sex')|(data['SB_behavior']=='End sex')|(data['SB_behavior']=='sex')|
                   (data['SB_behavior']=='Start bout')|(data['SB_behavior']=='End bout')|(data['SB_behavior']=='Cross break')]
    df_SB['obs_num'] = df_SB.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_SB = df_SB.sort_values(by=[OBS,TIME], ascending = False)
    df_SB['obs_num_back'] = df_SB.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_SB = df_SB.sort_values(by=[OBS,TIME])
    df_SB['temp_behavior']=np.where((df_SB['obs_num']==1),"fix",df_SB['SB_behavior'])
    df_SB['Next_behavior_sex']=df_SB.groupby(RATID)['temp_behavior'].shift(-1)
    df_SB['Previous_behavior_sex']=df_SB.groupby(RATID)['SB_behavior'].shift(1)
    df_SB['Previous_behavior_sex']=np.where((df_SB['obs_num']==1),"fix",df_SB['Previous_behavior_sex'])
    df_SB['Next_behavior_sex']=np.where((df_SB['obs_num_back']==1),"fix",df_SB['Next_behavior_sex'])

    # Make column that marks the sex behavior right
    df_SB['SB_sex_mark']=np.where(df_SB['SB_behavior']=='Single sex','Single sex','')
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Cross break')&(df_SB['Previous_behavior_sex']=='Cross break')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Cross break')&(df_SB['Previous_behavior_sex']=='sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Cross break')&(df_SB['Previous_behavior_sex']=='End bout')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Cross break')&(df_SB['Previous_behavior_sex']=='Start bout')),'Single last sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='Cross break')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='sex')),'Middle sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='End bout')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='fix')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='Start bout')),'First sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='End sex')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='sex')&(df_SB['Previous_behavior_sex']=='Start sex')),'Middle sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='Cross break')),'Single first sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='sex')),'Last sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='End bout')),'Single first sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='fix')),'Single first sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='Start bout')),'Single middle sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='End sex')),'Single first sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End bout')&(df_SB['Previous_behavior_sex']=='Start sex')),'Last sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='fix')&(df_SB['Previous_behavior_sex']=='sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='fix')&(df_SB['Previous_behavior_sex']=='End bout')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='fix')&(df_SB['Previous_behavior_sex']=='Start bout')),'Single last sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start bout')&(df_SB['Previous_behavior_sex']=='Cross break')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start bout')&(df_SB['Previous_behavior_sex']=='sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start bout')&(df_SB['Previous_behavior_sex']=='fix')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start bout')&(df_SB['Previous_behavior_sex']=='Start bout')),'Single last sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='Cross break')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='sex')),'Middle sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='End bout')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='End sex')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='fix')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='Start bout')),'First sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='End sex')&(df_SB['Previous_behavior_sex']=='Start sex')),'Middle sex in SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start sex')&(df_SB['Previous_behavior_sex']=='Cross break')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='sex')&(df_SB['Next_behavior_sex']=='Start sex')&(df_SB['Previous_behavior_sex']=='sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='Cross break')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='End bout')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='End sex')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='Start bout')),'Single last sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='Start sex')),'sex ends SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='End sex')&(df_SB['Previous_behavior_sex']=='fix')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='Cross break')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='sex')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='End bout')),'Single first sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='End sex')),'sex starts SB',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='Start bout')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='Start sex')),'Single sex',df_SB['SB_sex_mark'])
    df_SB['SB_sex_mark']=np.where(((df_SB['SB_behavior']=='Start sex')&(df_SB['Next_behavior_sex']=='fix')),'Single sex',df_SB['SB_sex_mark'])

    # Write the markers back in the real dataframe
    # Place the index numbers in lists
    list_idx_singlesex=df_SB.index[(df_SB['SB_sex_mark']=='Single sex')].tolist()
    list_idx_singlefirstsex=df_SB.index[(df_SB['SB_sex_mark']=='Single first sex')].tolist()
    list_idx_singlelastsex=df_SB.index[(df_SB['SB_sex_mark']=='Single last sex')].tolist()
    list_idx_singlemiddlesex=df_SB.index[(df_SB['SB_sex_mark']=='Single middle sex')].tolist()
    
    list_idx_sexstartSB=df_SB.index[(df_SB['SB_sex_mark']=='sex starts SB')].tolist()
    list_idx_sexendSB=df_SB.index[(df_SB['SB_sex_mark']=='sex ends SB')].tolist()
    list_idx_firstsexSB=df_SB.index[(df_SB['SB_sex_mark']=='First sex in SB')].tolist()
    list_idx_lastsexSB=df_SB.index[(df_SB['SB_sex_mark']=='Last sex in SB')].tolist()
    list_idx_sexmiddleSB=df_SB.index[(df_SB['SB_sex_mark']=='Middle sex in SB')].tolist()

    # Make a column for SB_sex_mark
    data['SB_sex_mark']=NaN    
    # Replace the "sex" for the actual behavior it was
    for i in list_idx_singlesex:
        data.at[i,'SB_sex_mark']='Single sex'
    for i in list_idx_singlefirstsex:
        data.at[i,'SB_sex_mark']='Single first sex'
    for i in list_idx_singlelastsex:
        data.at[i,'SB_sex_mark']='Single last sex'
    for i in list_idx_singlemiddlesex:
        data.at[i,'SB_sex_mark']='Single middle sex'

    for i in list_idx_sexstartSB:
        data.at[i,'SB_sex_mark']='sex starts SB'
    for i in list_idx_sexendSB:
        data.at[i,'SB_sex_mark']='sex ends SB'
    for i in list_idx_firstsexSB:
        data.at[i,'SB_sex_mark']='First sex in SB'
    for i in list_idx_lastsexSB:
        data.at[i,'SB_sex_mark']='Last sex in SB'
    for i in list_idx_sexmiddleSB:
        data.at[i,'SB_sex_mark']='Middle sex in SB'

    # Mark the time of the start and end of each sex bout
    data['Time_start_sex_bout']=np.where(((data['SB_sex_mark']=='Single sex')|(data['SB_sex_mark']=='Single first sex')|
                                              (data['SB_sex_mark']=='Single last sex')|(data['SB_sex_mark']=='Single middle sex')|
                                              (data['SB_sex_mark']=='sex starts SB')|(data['SB_sex_mark']=='First sex in SB')),
                                            data['Beh_start'],NaN)
    data['Time_start_sex_bout']=data.groupby(['ID'], sort=False)['Time_start_sex_bout'].fillna(method="backfill")
    
    data['Time_end_sex_bout']=np.where(((data['SB_sex_mark']=='Single sex')|(data['SB_sex_mark']=='Single first sex')|
                                              (data['SB_sex_mark']=='Single last sex')|(data['SB_sex_mark']=='Single middle sex')|
                                              (data['SB_sex_mark']=='sex ends SB')|(data['SB_sex_mark']=='Last sex in SB')),
                                              data['Beh_end'],NaN)
    data['Time_end_sex_bout']=data.groupby(['ID'], sort=False)['Time_end_sex_bout'].fillna(method="backfill")

    # Get the duration of the sex bout, marked next to the start of the sex bout
    data['Duration_sex_bout']=np.where(((data['SB_sex_mark']=="sex starts SB")|(data['SB_sex_mark']=="First sex in SB")),((data['Time_end_sex_bout'])-(data['Time_start_sex_bout'])),NaN)
    data['Duration_sex_bout']=np.where(((data['SB_sex_mark']=='Single sex')|(data['SB_sex_mark']=='Single first sex')|
                                              (data['SB_sex_mark']=='Single last sex')|(data['SB_sex_mark']=='Single middle sex')),data['durations'],data['Duration_sex_bout'])
    
    # Get column with the start of next mount bout
    data['Start_next_SB']=data.groupby(['ID'], sort=False)['Time_start_sex_bout'].shift(-1)
    
    # Get the duration of the time out
    data['Duration_time_out_SB']=np.where(((data['SB_sex_mark']=="sex ends SB")|(data['SB_sex_mark']=="Last sex in SB")|
                                        (data['SB_sex_mark']=='Single sex')|(data['SB_sex_mark']=='Single first sex')|
                                                                                  (data['SB_sex_mark']=='Single last sex')|(data['SB_sex_mark']=='Single middle sex')),
                                              (data['Start_next_SB']-data['Time_end_sex_bout']),NaN)
    
    # Count the mount bouts
    data['sex_bout_count']=np.where(((data['SB_sex_mark']=="sex starts SB")|(data['SB_sex_mark']=="First sex in SB")|
                                        (data['SB_sex_mark']=='Single sex')|(data['SB_sex_mark']=='Single first sex')|
                                              (data['SB_sex_mark']=='Single last sex')|(data['SB_sex_mark']=='Single middle sex')),
                                        1,NaN)
    data['OBS_SB_count'] = data['sex_bout_count'].map(str) + data['ID'] 
    data['sex_bout_num'] = data.groupby('OBS_SB_count')['sex_bout_count'].transform(lambda x: np.arange(1, len(x) + 1))
    
    # Calculate the interval between the start of mount bouts
    data['Interval_SB']=np.where((data['Duration_sex_bout']>0),(data['Start_next_SB']-data['Time_start_sex_bout']),NaN)

    # Create new column for SB_sex_mark to match sex or carrying food
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Single sex')),'Single dart',data['SB_sex_mark'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Single first sex')),'Single first dart',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Single last sex')),'Single last dart',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Single middle sex')),'Single middle dart',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='sex starts SB')),'dart starts SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='sex ends SB')),'dart ends SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='First sex in SB')),'First dart in SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Last sex in SB')),'Last dart in SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]==BP)&(data['SB_sex_mark']=='Middle sex in SB')),'Middle dart in SB',data['SB_sex_mark_split'])

    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Single sex')),'Single lordosis',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Single first sex')),'Single first lordosis',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Single last sex')),'Single last lordosis',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Single middle sex')),'Single middle lordosis',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='sex starts SB')),'lordosis starts SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='sex ends SB')),'lordosis ends SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='First sex in SB')),'First lordosis in SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Last sex in SB')),'Last lordosis in SB',data['SB_sex_mark_split'])
    data['SB_sex_mark_split']=np.where(((data[BEH]!=BP)&(data['SB_sex_mark_split']=='Middle sex in SB')),'Middle lordosis in SB',data['SB_sex_mark_split'])

    ##########
    # Get the times it takes the female to get back to mating after M/I/E
    # Create a small dataframe of only copulating behaviors needed for further analysis
    df_sex=data.loc[(data[BEH]==BP)|(data[BEH]==BQ)|(data[BEH]==BR)|(data[BEH]==BS)]
    df_sex['obs_num'] = df_sex.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))
    df_sex['temp_behavior']=np.where((df_sex['obs_num']==1),"fix",df_sex[BEH])
    df_sex['Next_cop_behavior']=df_sex.groupby(RATID)['temp_behavior'].shift(-1)
    df_sex['Time_next_cop_behavior']=df_sex.groupby(RATID)[TIME].shift(-1)
    
    list_idx_next_cop=df_sex.index[df_sex['Time_next_cop_behavior']>0].tolist()

    # Make a column for the CRL
    data['Time_next_cop_behavior']=NaN    
    # Replace the "sex" for the actual behavior it was
    for i in list_idx_next_cop:
        data.at[i,'Time_next_cop_behavior']=i

    data['CRL_M']=np.where(((data[BEH]==BQ)&(data['Time_next_cop_behavior']>0)),(data['Time_next_cop_behavior'])-data[TIME],np.NaN)
    data['CRL_I']=np.where(((data[BEH]==BR)&(data['Time_next_cop_behavior']>0)),(data['Time_next_cop_behavior'])-data[TIME],np.NaN)
    data['CRL_E']=np.where(((data[BEH]==BS)&(data['Time_next_cop_behavior']>0)),(data['Time_next_cop_behavior'])-data[TIME],np.NaN)

    return data

data_R=dataprep(data_R)    
data_P=dataprep(data_P)    
data_B=dataprep(data_B)    
data_I=dataprep(data_I)    
data_A=dataprep(data_A)    
data_T=dataprep(data_T)    

# Make list of the eating bout related outcomes
list_eating_bout=['Single eating','Single first eating','Single last eating','Single middle eating','Eating starts EB',
                  'Eating ends EB','First eating in EB','Last eating in EB','Middle eating in EB']

list_sex_bout=['Single sex','Single first sex','Single last sex','Single middle sex','sex starts SB',
                  'sex ends SB','First sex in SB','Last sex in SB','Middle sex in SB']


# # Definition to remove nan from nested dictionary to prepare for dataframe convertion
# def remove_nan_from_dict(dict_to_check):

#     for key in list(dict_to_check.keys()):
#         val = dict_to_check[key]
#         if type(val) == dict:
#             remove_nan_from_dict(val)
#         if type(val) == float :
#             if val >0:
#                 pass
#             else:
#                 print("Removing key:", key)
#                 del dict_to_check[key]

# new_dict_R=my_dict_behavior['dict_results_R']
# remove_nan_from_dict(new_dict_R)

# Create dataframes of your data for graphs
df_R = pd.DataFrame.from_dict(my_dict_behavior['dict_results_R'])
df_R=df_R.T
df_P = pd.DataFrame.from_dict(my_dict_behavior['dict_results_P'])
df_P=df_P.T
df_B = pd.DataFrame.from_dict(my_dict_behavior['dict_results_B'])
df_B=df_B.T
df_A = pd.DataFrame.from_dict(my_dict_behavior['dict_results_A'])
df_A=df_A.T
df_I = pd.DataFrame.from_dict(my_dict_behavior['dict_results_I'])
df_I=df_I.T
df_T = pd.DataFrame.from_dict(my_dict_behavior['dict_results_T'])
df_T=df_T.T

# Make dictionary of dataframes with total
dfs={'T':df_T,'B':df_B,'I':df_I,'A':df_A,'P':df_P,'R':df_R}

# Add columns about virus, diet, etc
for key,df in dfs.items():
    df.reset_index(inplace=True)
    df.columns = df.columns.str.replace('index','ID',regex=True) 

    df[RATID]=df['ID']
    df[RATID]=df[RATID].map(dict_id)

    df[VIRUS]=pd.to_numeric(df[RATID])
    df[VIRUS]=df[VIRUS].map(dict_virus)

    df[DIET]=pd.to_numeric(df[RATID])
    df[DIET]=df[DIET].map(dict_diet)

    df[TEST]=df['ID']
    df[TEST]=df[TEST].map(dict_test)

    df['Testsession']=df['ID']
    df['Testsession']=df['Testsession'].map(dict_testsession)
    
    df['BW']=df['ID']
    df['BW']=df['ID'].map(dict_BW)
    
    df['BW_gain']=df['ID']
    df['BW_gain']=df['ID'].map(dict_BW_gain)

# Calculate BW upper and lower levels
df_BW=df_R.drop_duplicates(subset=[RATID])
df_BW_CTR=df_BW.loc[df_BW[DIET]=='CTR']
df_BW_HFHS=df_BW.loc[df_BW[DIET]=='HFHS']
df_BW_CAF=df_BW.loc[df_BW[DIET]=='CAF']

BW_CTR_low=np.mean(df_BW_CTR['BW'])-2*np.std(df_BW_CTR['BW'])
BW_CTR_middle=np.mean(df_BW_CTR['BW'])
BW_CTR_high=np.mean(df_BW_CTR['BW'])+2*np.std(df_BW_CTR['BW'])
BW_HFHS_low=np.mean(df_BW_HFHS['BW'])-2*np.std(df_BW_HFHS['BW'])
BW_HFHS_middle=np.mean(df_BW_HFHS['BW'])
BW_HFHS_high=np.mean(df_BW_HFHS['BW'])+2*np.std(df_BW_HFHS['BW'])
BW_CAF_low=np.mean(df_BW_CAF['BW'])-2*np.std(df_BW_CAF['BW'])
BW_CAF_middle=np.mean(df_BW_CAF['BW'])
BW_CAF_high=np.mean(df_BW_CAF['BW'])+2*np.std(df_BW_CAF['BW'])

BW_gain_CTR_low=np.mean(df_BW_CTR['BW_gain'])-2*np.std(df_BW_CTR['BW_gain'])
BW_gain_CTR_middle=np.mean(df_BW_CTR['BW_gain'])
BW_gain_CTR_high=np.mean(df_BW_CTR['BW_gain'])+2*np.std(df_BW_CTR['BW_gain'])
BW_gain_HFHS_low=np.mean(df_BW_HFHS['BW_gain'])-2*np.std(df_BW_HFHS['BW_gain'])
BW_gain_HFHS_middle=np.mean(df_BW_HFHS['BW_gain'])
BW_gain_HFHS_high=np.mean(df_BW_HFHS['BW_gain'])+2*np.std(df_BW_HFHS['BW_gain'])
BW_gain_CAF_low=np.mean(df_BW_CAF['BW_gain'])-2*np.std(df_BW_CAF['BW_gain'])
BW_gain_CAF_middle=np.mean(df_BW_CAF['BW_gain'])
BW_gain_CAF_high=np.mean(df_BW_CAF['BW_gain'])+2*np.std(df_BW_CAF['BW_gain'])

for key,df in dfs.items():
    df['BW_level']=np.where(((df[DIET]=='CTR') & (df['BW']<=BW_CTR_middle)),'Low','High')
    df['BW_level']=np.where(((df[DIET]=='CAF') & (df['BW']<=BW_CAF_middle)),'Low',df['BW_level'])
    df['BW_level']=np.where(((df[DIET]=='HFHS') & (df['BW']<=BW_HFHS_middle)),'Low',df['BW_level'])
    df['BW_level']=np.where(((df[DIET]=='CAF') & (df['BW']>BW_CAF_middle)),'High',df['BW_level'])
    df['BW_level']=np.where(((df[DIET]=='HFHS') & (df['BW']>BW_HFHS_middle)),'High',df['BW_level'])

    df['BW_gain_level']=np.where(((df[DIET]=='CTR') & (df['BW_gain']<=BW_gain_CTR_middle)),'Low','High')
    df['BW_gain_level']=np.where(((df[DIET]=='CAF') & (df['BW_gain']<=BW_gain_CAF_middle)),'Low',df['BW_gain_level'])
    df['BW_gain_level']=np.where(((df[DIET]=='HFHS') & (df['BW_gain']<=BW_gain_HFHS_middle)),'Low',df['BW_gain_level'])
    df['BW_gain_level']=np.where(((df[DIET]=='CAF') & (df['BW_gain']>BW_gain_CAF_middle)),'High',df['BW_gain_level'])
    df['BW_gain_level']=np.where(((df[DIET]=='HFHS') & (df['BW_gain']>BW_gain_HFHS_middle)),'High',df['BW_gain_level'])

# # Save the results dataframes to excel for check
# writer_results = pd.ExcelWriter(out_path5, engine='xlsxwriter')
# df_R.to_excel(writer_results, sheet_name='data_R')
# writer_results.save()
# writer_results.close()


#################################################################################################

# Delete the rows with the excluded animals
for i in list_excl:
    data_full=data_full[data_full.RatID != i]

# Create a list with statistical measures
list_stat=['Mean','Median','Std','SEM','Q25','Q75','semedian','var']
list_treat=['CTR','HFHS','CAF']

# fill list of RatIDs for each group
list_CTR=[]
list_CAF=[]
list_HFHS=[]

for key,value in dict_diet.items():
    if value == 'CTR':
        list_CTR.append(key)
    if value == 'CAF':
        list_CAF.append(key)
    if value == 'HFHS':
        list_HFHS.append(key)

# set font size for all figures
SMALL_SIZE = 12
MEDIUM_SIZE = 16
BIGGER_SIZE = 18
# plt.rcParams['font.size'] = 22 
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
custom_params = {"axes.spines.right": False, "axes.spines.top": False}        

color_snips='#95A5A6'
color_GCaMP='#117864'
color_GFP_snips='#7C6B39'
color_GFP='#F8D672'
color_shadow='xkcd:silver'

color_scat_snips='#5F6A6A'
color_scat_GCaMP='#0E6251'
color_scat_GFP_snips='#d472bc'
color_scat_GFP='#57224a'

color_CTR='#5F6A6A'
color_HFHS='#9E3C86'
color_CAF='#117864'

color_low='#7b8888'
color_high='#151717'
# color_HFHS_low='#c464ad'
# color_HFHS_high='#3a1632'
# color_CAF_low='#53e7ca'
# color_CAF_high='#07332b'

color_CTR_shadow='#cacccc'
color_HFHS_shadow='#f7c1ea'
color_CAF_shadow='#afede1'
color_GFP_shadow='#FCF2D4'

color_scat_CTR='#4D5656'
color_scat_HFHS='#57224a'
color_scat_CAF='#0E6251'

color_light='#515A5A'
color_door='#424949'
color_zeroline='#515A5A'

color_AUC_CTR_pre='#D5DBDB'
color_AUC_CTR_light='#95A5A6'
color_AUC_CTR_post='#5F6A6A'

color_AUC_HFHS_pre='#E884D0'
color_AUC_HFHS_light='#C766AF'
color_AUC_HFHS_post='#9E3C86'

color_AUC_CAF_pre='#A3E4D7'
color_AUC_CAF_light='#1ABC9C'
color_AUC_CAF_post='#117864'

color_AUC_CTR_pre_scatter='#BFC9CA'
color_AUC_CTR_light_scatter='#839192'
color_AUC_CTR_post_scatter='#4D5656'

color_AUC_HFHS_pre_scatter='#d472bc'
color_AUC_HFHS_light_scatter='#a65391'
color_AUC_HFHS_post_scatter='#57224a'

color_AUC_CAF_pre_scatter='#76D7C4'
color_AUC_CAF_light_scatter='#17A589'
color_AUC_CAF_post_scatter='#0E6251'

# color_zeroline='#17202A'


################## MAKE BEHAVIOR GRAPHS###################################################################

def graphs_3behaviors_3groups(dataframe,test1,testsession1,behavior1,title1,
                    test2,testsession2,behavior2,title2,
                    test3,testsession3,behavior3,title3,hue,graphtitle):
    """
    Parameters
    ----------
    DataFrame : DataFrame
        Add 1st dictionary of data you want to add to the figure 
        e.g. df_R, df_P, df_B
    test1 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession1 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior1 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title1 : string
        Add the subtitle of the subplot
    test2 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession2 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior2 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title2 : string
        Add the subtitle of the subplot
    test3 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession3 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior3 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward antiapatory', 'TN_Reward consummatory'
    title3 : string
        Add the subtitle of the subplot
    hue : string
        Add the column name of the variable you would you to divide your individual datapoint on
        e.g. 'BW_level' or 'BW_gain_level'
    graphtitle : string
        Add the start name of the figure that is saved. 

    Returns
    -------
    Figure
    Makes a figure of 3 horizontal subplots of the 3 behaviors you want and from the dictionaries you want.
    It automatically takes the CTR, HFHS and CAF groups.
    """
    
    df=dataframe
    data1=df.loc[(df['Test']==test1)&(df['Testsession']==testsession1)]
    data2=df.loc[(df['Test']==test2)&(df['Testsession']==testsession2)]
    data3=df.loc[(df['Test']==test3)&(df['Testsession']==testsession3)]

    sns.set(style="ticks", rc=custom_params)
    # barWidth = 0.6
    yy=0
    
    max1=np.max(data1[behavior1])
    max2=np.max(data2[behavior2])
    max3=np.max(data3[behavior3])
    
    ymax = max1
    if max2 > ymax:
            ymax = max2
    if max3 > ymax:
            ymax = max3
            
    y_max=round(ymax / 10) * 10
    if y_max <= 10:
        yy=np.arange(0,(y_max+2),2).tolist()
    if y_max >10 and y_max <= 50:
        yy=np.arange(0,(y_max+10),10).tolist()
    if y_max > 50 and y_max <= 100:
        yy=np.arange(0,(y_max+10),20).tolist()
    if y_max > 100 and y_max <= 1000:
        yy=np.arange(0,(y_max+100),100).tolist()
    if y_max > 1000:
        yy=np.arange(0,(y_max+100),200).tolist()

    hue = hue
    palette_bar = [color_CTR,color_HFHS,color_CAF]
    palette_swarm = [color_scat_CTR,color_scat_HFHS,color_scat_CAF]
    palette_swarm_hue= [color_low,color_high]
    order = ['CTR','HFHS','CAF']

    if not os.path.isdir(directory_results_beh+directory_behavior_total):
        os.mkdir(directory_results_beh+directory_behavior_total)

    os.chdir(directory_results_beh+directory_behavior_total)
    
    fig, axs = plt.subplots(1,3, figsize=(12,4), sharex=True, sharey=True)

    sns.swarmplot(ax=axs[0], data=data1,x='Diet', y=behavior1, hue=hue,palette=palette_swarm_hue, order=order, legend=False)
    sns.barplot(ax=axs[0], data=data1,x='Diet', y=behavior1, errorbar = None,palette=palette_bar, order=order)
    axs[0].set(xlabel=None)
    axs[0].set_title(title1)
    if 'TD' in behavior1:
        axs[0].set(ylabel='Time spent (s)')
    elif 'L1' in behavior1:
        axs[0].set(ylabel='Seconds')
    else:
        axs[0].set(ylabel='Frequency')
    axs[0].set(yticks=yy)

    sns.swarmplot(ax=axs[1], data=data2,x='Diet', y=behavior2, hue=hue,palette=palette_swarm_hue, order=order, legend=False)
    sns.barplot(ax=axs[1], data=data2,x='Diet', y=behavior2, errorbar = None, palette=palette_bar, order=order)
    axs[1].set_title(title2)
    axs[1].set(xlabel=None)
    axs[1].set(ylabel=None)
    axs[1].spines['left'].set_visible(False)                
    axs[1].set(yticks=yy)
    axs[1].tick_params(left=False)              
    # axs[1].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)

    sns.swarmplot(ax=axs[2], data=data3,x='Diet', y=behavior3, hue=hue,palette=palette_swarm_hue, order=order,legend=False)
    sns.barplot(ax=axs[2], data=data3,x='Diet', y=behavior3, errorbar = None, palette=palette_bar, order=order)
    axs[2].set_title(title3)
    axs[2].set(xlabel=None)
    axs[2].set(ylabel=None)
    axs[2].spines['left'].set_visible(False)                
    axs[2].set(yticks=yy)
    axs[2].tick_params(left=False)              
    # axs[2].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)
    # axs[2].legend(bbox_to_anchor=(1, 1), title='Body Weight',shadow = True, facecolor = 'white') 
    
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.3, 
                        hspace=0.5)
    plt.savefig('%s.png'%(graphtitle))
    plt.close(fig)

    os.chdir(directory)
    print('graphs_3behaviors_3groups finished')
    
def graphs_2behaviors_3groups(dataframe,test1,testsession1,behavior1,title1,
                    test2,testsession2,behavior2,title2,
                    hue,graphtitle):
    """
    Parameters
    ----------
    DataFrame : DataFrame
        Add 1st dictionary of data you want to add to the figure 
        e.g. df_R, df_P, df_B
    test1 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession1 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior1 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title1 : string
        Add the subtitle of the subplot
    test2 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession2 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior2 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title2 : string
        Add the subtitle of the subplot
    hue : string
        Add the column name of the variable you would you to divide your individual datapoint on
        e.g. 'BW_level' or 'BW_gain_level'
    graphtitle : string
        Add the start name of the figure that is saved. 

    Returns
    -------
    Figure
    Makes a figure of 3 horizontal subplots of the 3 behaviors you want and from the dictionaries you want.
    It automatically takes the CTR, HFHS and CAF groups.
    """
    
    df=dataframe
    data1=df.loc[(df['Test']==test1)&(df['Testsession']==testsession1)]
    data2=df.loc[(df['Test']==test2)&(df['Testsession']==testsession2)]

    sns.set(style="ticks", rc=custom_params)
    # barWidth = 0.6
    yy=0
    
    max1=np.max(data1[behavior1])
    max2=np.max(data2[behavior2])
    
    ymax = max1
    if max2 > ymax:
            ymax = max2
            
    y_max=round(ymax / 10) * 10
    if y_max <= 10:
        yy=np.arange(0,(y_max+2),2).tolist()
    if y_max >10 and y_max <= 50:
        yy=np.arange(0,(y_max+10),10).tolist()
    if y_max > 50 and y_max <= 100:
        yy=np.arange(0,(y_max+10),20).tolist()
    if y_max > 100 and y_max <= 1000:
        yy=np.arange(0,(y_max+100),100).tolist()
    if y_max > 1000:
        yy=np.arange(0,(y_max+100),200).tolist()

    hue = hue
    palette_bar = [color_CTR,color_HFHS,color_CAF]
    palette_swarm = [color_scat_CTR,color_scat_HFHS,color_scat_CAF]
    palette_swarm_hue= [color_low,color_high]
    order = ['CTR','HFHS','CAF']

    if not os.path.isdir(directory_results_beh+directory_behavior_total):
        os.mkdir(directory_results_beh+directory_behavior_total)

    os.chdir(directory_results_beh+directory_behavior_total)
    
    fig, axs = plt.subplots(1,2, figsize=(8,4), sharex=True, sharey=True)

    sns.swarmplot(ax=axs[0], data=data1,x='Diet', y=behavior1, hue=hue,palette=palette_swarm_hue, order=order, legend=False)
    sns.barplot(ax=axs[0], data=data1,x='Diet', y=behavior1, errorbar = None,palette=palette_bar, order=order)
    axs[0].set(xlabel=None)
    axs[0].set_title(title1)
    if 'TD' in behavior1:
        axs[0].set(ylabel='Time spent (s)')
    elif 'L1' in behavior1:
        axs[0].set(ylabel='Seconds')
    else:
        axs[0].set(ylabel='Frequency')
    axs[0].set(yticks=yy)

    sns.swarmplot(ax=axs[1], data=data2,x='Diet', y=behavior2, hue=hue,palette=palette_swarm_hue, order=order,legend=False)
    sns.barplot(ax=axs[1], data=data2,x='Diet', y=behavior2, errorbar = None, palette=palette_bar, order=order)
    axs[1].set_title(title2)
    axs[1].set(xlabel=None)
    axs[1].set(ylabel=None)
    axs[1].spines['left'].set_visible(False)                
    axs[1].set(yticks=yy)
    axs[1].tick_params(left=False)              
    # axs[1].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)

    # axs[1].legend(bbox_to_anchor=(1, 1), title='Body Weight',shadow = True, facecolor = 'white') 
    
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.3, 
                        hspace=0.5)
    plt.savefig('%s.png'%(graphtitle))
    plt.close(fig)

    os.chdir(directory)
    print('graphs_2behaviors_3groups finished')

# Make graphs of these behaviors
def graphs_behaviors_3groups(dataframe,phase,test1,testsession1,behavior1,title1,
                    hue,graphtitle):
    """
    Parameters
    ----------
    DataFrame : DataFrame
        Add 1st dictionary of data you want to add to the figure 
        e.g. df_R, df_P, df_B
    phase : string
        Add the phase of the behaviors you expore, so that they are stored in the right folder
        e.g. "R","P"
    test1 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession1 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior1 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title1 : string
        Add the subtitle of the subplot
    hue : string
        Add the column name of the variable you would you to divide your individual datapoint on
        e.g. 'BW_level' or 'BW_gain_level'
    graphtitle : string
        Add the start name of the figure that is saved. 

    Returns
    -------
    Figure
    Makes a figure of 3 horizontal subplots of the 3 behaviors you want and from the dictionaries you want.
    It automatically takes the CTR, HFHS and CAF groups.
    """
    
    df=dataframe
    data1=df.loc[(df['Test']==test1)&(df['Testsession']==testsession1)]

    sns.set(style="ticks", rc=custom_params)
    # barWidth = 0.6
    yy=0
    
    max1=np.max(data1[behavior1])
    
    ymax = max1
            
    y_max=round(ymax / 10) * 10
    if y_max <= 10:
        yy=np.arange(0,(y_max+2),2).tolist()
    if y_max >10 and y_max <= 50:
        yy=np.arange(0,(y_max+10),10).tolist()
    if y_max > 50 and y_max <= 100:
        yy=np.arange(0,(y_max+10),20).tolist()
    if y_max > 100 and y_max <= 1000:
        yy=np.arange(0,(y_max+100),100).tolist()
    if y_max > 1000:
        yy=np.arange(0,(y_max+100),200).tolist()

    hue = hue
    palette_bar = [color_CTR,color_HFHS,color_CAF]
    palette_swarm = [color_scat_CTR,color_scat_HFHS,color_scat_CAF]
    palette_swarm_hue= [color_low,color_high]
    order = ['CTR','HFHS','CAF']

    # Change directory to output folder
    if not os.path.isdir(directory_results_beh+directory_behavior_pertest):
        os.mkdir(directory_results_beh+directory_behavior_pertest)
    if phase == 'T':
        if not os.path.isdir(directory_results_beh+directory_behavior_total):
            os.mkdir(directory_results_beh+directory_behavior_total)
    elif phase == 'P':
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/P'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/P')
    elif phase == 'R':
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/R'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/R')
    else:
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/P'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/P')

    if phase == 'T':
        os.chdir(directory_results_beh+directory_behavior_total)
    elif phase == 'P':
        os.chdir(directory_results_beh+directory_behavior_pertest+'/P')
    elif phase == 'R':
        os.chdir(directory_results_beh+directory_behavior_pertest+'/R')
    else:
        os.chdir(directory_results_beh+directory_behavior_pertest+'/P')
    
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)

    sns.swarmplot(ax=ax, data=data1,x='Diet', y=behavior1, hue=hue,palette=palette_swarm_hue, order=order,legend=False)
    sns.barplot(ax=ax, data=data1,x='Diet', y=behavior1, errorbar = None,palette=palette_bar, order=order)
    ax.set(xlabel=None)
    ax.set_title(title1)
    if 'TD' in behavior1:
        ax.set(ylabel='Time spent (s)')
    elif 'L1' in behavior1:
        ax.set(ylabel='Seconds')
    else:
        ax.set(ylabel='Frequency')
    ax.set(yticks=yy)

    # ax.legend(bbox_to_anchor=(1, 1), title='Body Weight',shadow = True, facecolor = 'white') 
    
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.3, 
                        hspace=0.5)
    plt.savefig('%s.png'%(graphtitle))
    plt.close(fig)

    os.chdir(directory)
    print('graphs_1behavior_3groups finished')

###################################################################################################    
###################################################################################################    
########### 3 GRAPHS of 3 GROUPS 
###################################################################################################    
###################################################################################################    

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_R,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_level','BW_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_sex:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_R,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_level','BW_SEC %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_P,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_level','BW_P_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_P,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_level','BW_P_SEC %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_A,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_level','BW_A_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_A,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_level','BW_A_SEC %s'%beh_keys)

###################################################################################################    
###################################################################################################    
######### 2 GRAPH 3 GROUPS
###################################################################################################    

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_R,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_level','BW_PRIM_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_P,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_level','BW_P_PRIM_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_A,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_level','BW_A_PRIM_rev %s'%beh_keys)

###################################################################################################    
###################################################################################################    
######### 1 GRAPH 3 GROUPS
###################################################################################################    

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_sex:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_R,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_level','BW_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_P,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_level','BW_P_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_A,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_level','BW_A_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_R,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_level','BW_DIS %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_P,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_level','BW_P_DIS %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_A,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_level','BW_A_DIS %s'%beh_keys)

# ###################################################################################################    
# ######### PER TEST
# ###################################################################################################    

# # Graphs per behavior
# for beh_keys in my_dict_behavior['dict_group_R'].keys():
#     for beh in list_interest_beh_reward:
#         if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh:
#             for rewardid in list_rewardid:
#                 graphs_behavior_3groups('R','dict_group_R',rewardid,'%s'%beh_keys,"%s %s"%(beh,rewardid))

# for beh_keys in my_dict_behavior['dict_group_P'].keys():
#     for beh in list_interest_beh_prereward:
#         if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh:
#             for rewardid in list_rewardid:
#                 graphs_behavior_3groups('P','dict_group_P',rewardid,'%s'%beh_keys,"%s %s"%(beh,rewardid))

###################################################################################################    
###################################################################################################    
############## BODY WEIGHT GAIN
###################################################################################################    
###################################################################################################    
for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_R,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_gain_level','BWG_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_sex:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_R,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_gain_level','BWG_SEC %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_P,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_gain_level','BWG_P_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_P,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_gain_level','BWG_P_SEC %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_A,'PRIMREWARD',1,'%s'%beh_keys,'1st food reward',
                                          'PRIMREWARD',3,'%s'%beh_keys,'3rd food reward',
                                          'PRIMREWARD',5,'%s'%beh_keys,'5th food reward','BW_gain_level','BWG_A_PRIM %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_3behaviors_3groups(df_A,'SECREWARD',1,'%s'%beh_keys,'1st sex reward',
                                          'SECREWARD',2,'%s'%beh_keys,'2nd sex reward',
                                          'SECREWARD',3,'%s'%beh_keys,'3rd sex reward','BW_gain_level','BWG_A_SEC %s'%beh_keys)

###################################################################################################    
###################################################################################################    
######### 2 GRAPH 3 GROUPS
###################################################################################################    

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_R,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_gain_level','BWG_PRIM_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_P,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_gain_level','BWG_P_PRIM_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_2behaviors_3groups(df_A,'PRIMREWARD_rev',1,'%s'%beh_keys,'1st food reward after reversal',
                                          'PRIMREWARD_rev',3,'%s'%beh_keys,'3rd food reward after reversal',
                                          'BW_gain_level','BWG_A_PRIM_rev %s'%beh_keys)

###################################################################################################    
###################################################################################################    
######### 1 GRAPH 3 GROUPS
###################################################################################################    

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_sex:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_R,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_gain_level','BWG_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_P,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_gain_level','BWG_P_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_A,'T','SECREWARD_rev',1,'%s'%beh_keys,'1st sex reward after reversal',
                                    'BW_gain_level','BWG_A_SEC_rev %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_R'].keys():
    for beh in list_interest_beh_food:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_R,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_gain_level','BWG_DIS %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_P'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_P,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_gain_level','BWG_P_DIS %s'%beh_keys)

for beh_keys in my_dict_behavior['dict_group_A'].keys():
    for beh in list_interest_beh_prereward:
        if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh or beh_keys== 'MD_%s'%beh:
            graphs_behaviors_3groups(df_A,'T','DISREWARD',1,'%s'%beh_keys,'standard chow',
                                    'BW_gain_level','BWG_A_DIS %s'%beh_keys)

####################################################################################################    
####################################################################################################    


# Create dictionaries to combine 1st-3rd sex test
tests=['2test','3test']
summean=['Sum','Mean']

list_rats=[]
for i in list_ratid:
    if i not in list_rats:
        list_rats.append(i) 

list_parameter_sexsum_R=[]
for parameter in my_dict_behavior['dict_results_R']['301SECREWARD1'].keys():
    for beh in list_interest_beh_sumsex:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            list_parameter_sexsum_R.append(parameter)

list_parameter_sexsum_P=[]
for parameter in my_dict_behavior['dict_results_P']['301SECREWARD1'].keys():
    for beh in list_interest_beh_sumsex:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            list_parameter_sexsum_P.append(parameter)

list_parameter_sexsum_A=[]
for parameter in my_dict_behavior['dict_results_A']['301SECREWARD1'].keys():
    for beh in list_interest_beh_sumsex:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            list_parameter_sexsum_A.append(parameter)

# create empty dictionaries    
dict_sex_R={rat:{test:{parameter:{stat:[] for stat in summean} for parameter in list_parameter_sexsum_R} for test in tests} for rat in list_rats}
dict_sex_P={rat:{test:{parameter:{stat:[] for stat in summean} for parameter in list_parameter_sexsum_P} for test in tests} for rat in list_rats}
dict_sex_A={rat:{test:{parameter:{stat:[] for stat in summean} for parameter in list_parameter_sexsum_A} for test in tests} for rat in list_rats}

# fill dictionaries
for rat in list_rats:
    if '%sSECREWARD1'%rat in my_dict_behavior['dict_results_R'].keys() and '%sSECREWARD2'%rat in my_dict_behavior['dict_results_R'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_R'].keys():
        for key,parameters in my_dict_behavior['dict_results_R'].items():
            for parameter,value in parameters.items():
                if parameter in list_parameter_sexsum_R:
                    dict_sex_R[rat]['3test'][parameter]['Sum']=my_dict_behavior['dict_results_R']["%sSECREWARD1"%rat][parameter] if my_dict_behavior['dict_results_R']["%sSECREWARD1"%rat][parameter]>0 else 0
                    dict_sex_R[rat]['3test'][parameter]['Sum']=dict_sex_R[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_R']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_R']["%sSECREWARD2"%rat][parameter]>0 else +0
                    dict_sex_R[rat]['3test'][parameter]['Sum']=dict_sex_R[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_R']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_R']["%sSECREWARD3"%rat][parameter]>0 else +0
                    dict_sex_R[rat]['3test'][parameter]['Mean']=dict_sex_R[rat]['3test'][parameter]['Sum']/3

for rat in list_rats:
    if '%sSECREWARD1'%rat in my_dict_behavior['dict_results_P'].keys() and '%sSECREWARD2'%rat in my_dict_behavior['dict_results_P'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_P'].keys():
        for key,parameters in my_dict_behavior['dict_results_P'].items():
            for parameter,value in parameters.items():
                if parameter in list_parameter_sexsum_P:
                    dict_sex_P[rat]['3test'][parameter]['Sum']=my_dict_behavior['dict_results_P']["%sSECREWARD1"%rat][parameter] if my_dict_behavior['dict_results_P']["%sSECREWARD1"%rat][parameter]>0 else 0
                    dict_sex_P[rat]['3test'][parameter]['Sum']=dict_sex_P[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_P']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_P']["%sSECREWARD2"%rat][parameter]>0 else +0
                    dict_sex_P[rat]['3test'][parameter]['Sum']=dict_sex_P[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_P']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_P']["%sSECREWARD3"%rat][parameter]>0 else +0
                    dict_sex_P[rat]['3test'][parameter]['Mean']=dict_sex_P[rat]['3test'][parameter]['Sum']/3

for rat in list_rats:
    if '%sSECREWARD1'%rat in my_dict_behavior['dict_results_A'].keys() and '%sSECREWARD2'%rat in my_dict_behavior['dict_results_P'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_P'].keys():
        for key,parameters in my_dict_behavior['dict_results_A'].items():
            for parameter,value in parameters.items():
                if parameter in list_parameter_sexsum_A:
                    dict_sex_A[rat]['3test'][parameter]['Sum']=my_dict_behavior['dict_results_A']["%sSECREWARD1"%rat][parameter] if my_dict_behavior['dict_results_A']["%sSECREWARD1"%rat][parameter]>0 else 0
                    dict_sex_A[rat]['3test'][parameter]['Sum']=dict_sex_A[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_A']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_A']["%sSECREWARD2"%rat][parameter]>0 else +0
                    dict_sex_A[rat]['3test'][parameter]['Sum']=dict_sex_A[rat]['3test'][parameter]['Sum']+my_dict_behavior['dict_results_A']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_A']["%sSECREWARD3"%rat][parameter]>0 else +0
                    dict_sex_A[rat]['3test'][parameter]['Mean']=dict_sex_A[rat]['3test'][parameter]['Sum']/3

for rat in list_rats:
    if '%sSECREWARD2'%rat in my_dict_behavior['dict_results_R'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_R'].keys():
        for key,parameters in my_dict_behavior['dict_results_R'].items():
            for parameter,value in parameters.items():
                if parameter in list_parameter_sexsum_R:
                    dict_sex_R[rat]['2test'][parameter]['Sum']=my_dict_behavior['dict_results_R']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_R']["%sSECREWARD2"%rat][parameter]>0 else 0
                    dict_sex_R[rat]['2test'][parameter]['Sum']=dict_sex_R[rat]['2test'][parameter]['Sum']+my_dict_behavior['dict_results_R']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_R']["%sSECREWARD3"%rat][parameter]>0 else +0
                    dict_sex_R[rat]['2test'][parameter]['Mean']=dict_sex_R[rat]['2test'][parameter]['Sum']/2
                
for rat in list_rats:
    if '%sSECREWARD2'%rat in my_dict_behavior['dict_results_P'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_P'].keys():
        for key,parameters in my_dict_behavior['dict_results_P'].items():
            for parameter,value in parameters.items():
                if parameter in list_parameter_sexsum_P:
                    dict_sex_P[rat]['2test'][parameter]['Sum']=my_dict_behavior['dict_results_P']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_P']["%sSECREWARD2"%rat][parameter]>0 else 0
                    dict_sex_P[rat]['2test'][parameter]['Sum']=dict_sex_P[rat]['2test'][parameter]['Sum']+my_dict_behavior['dict_results_P']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_P']["%sSECREWARD3"%rat][parameter]>0 else +0
                    dict_sex_P[rat]['2test'][parameter]['Mean']=dict_sex_P[rat]['2test'][parameter]['Sum']/2

    for rat in list_rats:
        if '%sSECREWARD2'%rat in my_dict_behavior['dict_results_A'].keys() and '%sSECREWARD3'%rat in my_dict_behavior['dict_results_P'].keys():
            for key,parameters in my_dict_behavior['dict_results_A'].items():
                for parameter,value in parameters.items():
                    if parameter in list_parameter_sexsum_A:
                        dict_sex_A[rat]['2test'][parameter]['Sum']=my_dict_behavior['dict_results_A']["%sSECREWARD2"%rat][parameter] if my_dict_behavior['dict_results_A']["%sSECREWARD2"%rat][parameter]>0 else 0
                        dict_sex_A[rat]['2test'][parameter]['Sum']=dict_sex_A[rat]['2test'][parameter]['Sum']+my_dict_behavior['dict_results_A']["%sSECREWARD3"%rat][parameter] if my_dict_behavior['dict_results_A']["%sSECREWARD3"%rat][parameter]>0 else +0
                        dict_sex_A[rat]['2test'][parameter]['Mean']=dict_sex_A[rat]['2test'][parameter]['Sum']/2
     

dict_sexgroup_R={test:{parameter:{stat:{t:[] for t in list_treat} for stat in summean} for parameter in list_parameter_sexsum_R} for test in tests} 
dict_sexgroup_P={test:{parameter:{stat:{t:[] for t in list_treat} for stat in summean} for parameter in list_parameter_sexsum_P} for test in tests} 
dict_sexgroup_A={test:{parameter:{stat:{t:[] for t in list_treat} for stat in summean} for parameter in list_parameter_sexsum_A} for test in tests} 
        
for parameter in list_parameter_sexsum_R:
    for rat in list_rats:
        for test in tests:
            for stat in summean:
                if rat in list_CTR:
                    if dict_sex_R[rat][test][parameter][stat]:
                        dict_sexgroup_R[test][parameter][stat]['CTR'].append(dict_sex_R[rat][test][parameter][stat])
                if rat in list_HFHS:
                    if dict_sex_R[rat][test][parameter][stat]:
                        dict_sexgroup_R[test][parameter][stat]['HFHS'].append(dict_sex_R[rat][test][parameter][stat])
                if rat in list_CAF:
                    if dict_sex_R[rat][test][parameter][stat]:
                        dict_sexgroup_R[test][parameter][stat]['CAF'].append(dict_sex_R[rat][test][parameter][stat])
    
for parameter in list_parameter_sexsum_P:
    for rat in list_rats:
        for test in tests:
            for stat in summean:
                if rat in list_CTR:
                    if dict_sex_P[rat][test][parameter][stat]:
                        dict_sexgroup_P[test][parameter][stat]['CTR'].append(dict_sex_P[rat][test][parameter][stat])
                if rat in list_HFHS:
                    if dict_sex_P[rat][test][parameter][stat]:
                        dict_sexgroup_P[test][parameter][stat]['HFHS'].append(dict_sex_P[rat][test][parameter][stat])
                if rat in list_CAF:
                    if dict_sex_P[rat][test][parameter][stat]:
                        dict_sexgroup_P[test][parameter][stat]['CAF'].append(dict_sex_P[rat][test][parameter][stat])

for parameter in list_parameter_sexsum_A:
    for rat in list_rats:
        for test in tests:
            for stat in summean:
                if rat in list_CTR:
                    if dict_sex_A[rat][test][parameter][stat]:
                        dict_sexgroup_A[test][parameter][stat]['CTR'].append(dict_sex_A[rat][test][parameter][stat])
                if rat in list_HFHS:
                    if dict_sex_A[rat][test][parameter][stat]:
                        dict_sexgroup_A[test][parameter][stat]['HFHS'].append(dict_sex_A[rat][test][parameter][stat])
                if rat in list_CAF:
                    if dict_sex_A[rat][test][parameter][stat]:
                        dict_sexgroup_A[test][parameter][stat]['CAF'].append(dict_sex_A[rat][test][parameter][stat])


# Create dataframes of your data for graphs
# ##########################UNDER CONSTRUCTION ##############
# df_R_sexsum=pd.DataFrame.from_dict({(rat,parameter,stat): dict_sexgroup_R[rat][parameter][stat] 
#                            for rat in dict_sexgroup_R.keys() 
#                            for parameter in dict_sexgroup_R[rat].keys()
#                            for stat in dict_sexgroup_R[rat][parameter].keys()},
#                        orient='index')
# ###########################################################
# df_R_sexsum = pd.DataFrame(dict_sexgroup_R)
# df_R_sexsum=df_R_sexsum.T
# df_P_sexsum = pd.DataFrame(dict_sexgroup_P)
# df_P_sexsum=df_P_sexsum.T

# # Make dictionary of dataframes with total
# dfs_sexsum={'P':df_P_sexsum,'R':df_R_sexsum}

# # Add columns about virus, diet, etc
# for key,df in dfs_sexsum.items():
#     df.reset_index(inplace=True)
#     df.columns = df.columns.str.replace('index','ID',regex=True) 

#     df[RATID]=df['ID']
#     df[RATID]=df[RATID].map(dict_id)

#     df[VIRUS]=pd.to_numeric(df[RATID])
#     df[VIRUS]=df[VIRUS].map(dict_virus)

#     df[DIET]=pd.to_numeric(df[RATID])
#     df[DIET]=df[DIET].map(dict_diet)

#     df[TEST]=df['ID']
#     df[TEST]=df[TEST].map(dict_test)

#     df['Testsession']=df['ID']
#     df['Testsession']=df['Testsession'].map(dict_testsession)
    
#     df['BW']=df['ID']
#     df['BW']=df['ID'].map(dict_BW)
    
#     df['BW_gain']=df['ID']
#     df['BW_gain']=df['ID'].map(dict_BW_gain)

# for key,df in dfs_sexsum.items():
#     df['BW_level']=np.where(((df[DIET]=='CTR') & (df['BW']<=BW_CTR_middle)),'Low','High')
#     df['BW_level']=np.where(((df[DIET]=='CAF') & (df['BW']<=BW_CAF_middle)),'Low',df['BW_level'])
#     df['BW_level']=np.where(((df[DIET]=='HFHS') & (df['BW']<=BW_HFHS_middle)),'Low',df['BW_level'])
#     df['BW_level']=np.where(((df[DIET]=='CAF') & (df['BW']>BW_CAF_middle)),'High',df['BW_level'])
#     df['BW_level']=np.where(((df[DIET]=='HFHS') & (df['BW']>BW_HFHS_middle)),'High',df['BW_level'])

#     df['BW_gain_level']=np.where(((df[DIET]=='CTR') & (df['BW_gain']<=BW_gain_CTR_middle)),'Low','High')
#     df['BW_gain_level']=np.where(((df[DIET]=='CAF') & (df['BW_gain']<=BW_gain_CAF_middle)),'Low',df['BW_gain_level'])
#     df['BW_gain_level']=np.where(((df[DIET]=='HFHS') & (df['BW_gain']<=BW_gain_HFHS_middle)),'Low',df['BW_gain_level'])
#     df['BW_gain_level']=np.where(((df[DIET]=='CAF') & (df['BW_gain']>BW_gain_CAF_middle)),'High',df['BW_gain_level'])
#     df['BW_gain_level']=np.where(((df[DIET]=='HFHS') & (df['BW_gain']>BW_gain_HFHS_middle)),'High',df['BW_gain_level'])
    


def graphs_behaviorsum_3groups(phase,value_CTR,value_HFHS,value_CAF,title,behavior,graphtitle):
    """
    Parameters
    ----------
    DataFrame : DataFrame
        Add 1st dictionary of data you want to add to the figure 
        e.g. df_R, df_P, df_B
    phase : string
        Add the phase of the behaviors you expore, so that they are stored in the right folder
        e.g. "R","P"
    test1 : string
        Add the code for the experiment
        e.g. 'PRIMREWARD5', 'PRIMREWARD1','SECREWARD1','PRIMREWARD_rev1','DISREWARD'
    testsession1 : float
        Add the code for the experiment session
        e.g. 1,2,3
    behavior1 : string
        Add the behavior you want plotted (as stored as key in dictionary)
        e.g. 'TN_Eating', 'TD_Reward anticipatory', 'TN_Reward consummatory'
    title1 : string
        Add the subtitle of the subplot
    tests : string
        Add '2test' if 2nd and 3rd sextest are combined, or '3test' when all 3 are combined
    hue : string
        Add the column name of the variable you would you to divide your individual datapoint on
        e.g. 'BW_level' or 'BW_gain_level'
    graphtitle : string
        Add the start name of the figure that is saved. 

    Returns
    -------
    Figure
    Makes a figure of 3 horizontal subplots of the 3 behaviors you want and from the dictionaries you want.
    It automatically takes the CTR, HFHS and CAF groups.
    """
    # Make a barplot
    # Plot the data in bar charts with individual datapoints
    # Set position of bar on X axis - MAKE SURE IT MATCHES YOUR NUMBER OF GROUPS
    # set width of bar
    
    barWidth = 0.6
    x1 = ['CTR']
    x2 = ['HFHS']
    x3 = ['CAF']
    
    x_scatter1=len(value_CTR)
    x_scatter2=len(value_HFHS)
    x_scatter3=len(value_CAF)
    
    ymax=0
    yy=0
    list_values=[value_CTR,value_HFHS,value_CAF]
    for val in list_values:
        for i in val:
            if i > ymax:
                ymax = i 
    y_max=round(ymax / 10) * 10
    if y_max <= 5:
        yy=np.arange(0,(y_max+1),1).tolist()
    if y_max >5 and y_max<= 10:
        yy=np.arange(0,(y_max+2),2).tolist()
    if y_max >10 and y_max <= 50:
        yy=np.arange(0,(y_max+10),10).tolist()
    if y_max > 50 and y_max <= 100:
        yy=np.arange(0,(y_max+10),20).tolist()
    if y_max > 100 and y_max <= 1000:
        yy=np.arange(0,(y_max+100),100).tolist()
    if y_max > 1000:
        yy=np.arange(0,(y_max+100),200).tolist()
    
    sns.set(style="ticks", rc=custom_params)
    # Change directory to output folder
    if not os.path.isdir(directory_results_beh+directory_behavior_pertest):
        os.mkdir(directory_results_beh+directory_behavior_pertest)
    if phase == 'T':
        if not os.path.isdir(directory_results_beh+directory_behavior_total):
            os.mkdir(directory_results_beh+directory_behavior_total)
    elif phase == 'P':
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/P'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/P')
    elif phase == 'R':
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/R'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/R')
    else:
        if not os.path.isdir(directory_results_beh+directory_behavior_pertest+'/P'):
            os.mkdir(directory_results_beh+directory_behavior_pertest+'/P')
    
    if any(value_CTR) or any(value_HFHS) or any(value_CAF):
        if phase == 'T':
            os.chdir(directory_results_beh+directory_behavior_total)
        elif phase == 'P':
            os.chdir(directory_results_beh+directory_behavior_pertest+'/P')
        elif phase == 'R':
            os.chdir(directory_results_beh+directory_behavior_pertest+'/R')
        else:
            os.chdir(directory_results_beh+directory_behavior_pertest+'/P')
        

        fig = plt.figure(figsize=(6,4))
        ax = fig.add_subplot(111)
        ax.bar(x1, np.nanmean(value_CTR), color=color_CTR, width=barWidth, edgecolor='white',label='CTR', zorder=2)
        ax.scatter(x_scatter1*x1, value_CTR, color=color_scat_CTR, alpha=.9,zorder=3)
        ax.bar(x2, np.nanmean(value_HFHS), color=color_HFHS, width=barWidth, edgecolor='white', label ='HFHS',zorder=2)
        ax.scatter(x_scatter2*x2, value_HFHS,color=color_scat_HFHS,  alpha=.9,zorder=3)
        ax.bar(x3, np.nanmean(value_CAF), color=color_CAF, width=barWidth, edgecolor='white',label='CAF',zorder=2)
        ax.scatter(x_scatter3*x3, value_CAF,color=color_scat_CAF,  alpha=.9,zorder=3)
        ax.set_title(title)
        if 'TD' in behavior:
            ax.set_ylabel('Time spent (s)')
        elif 'L1' in behavior:
            ax.set_ylabel('Seconds')
        else:
            ax.set_ylabel('Frequency')
        ax.set_yticks(yy)
        
        plt.subplots_adjust(left=0.1,
                            bottom=0.1, 
                            right=0.9, 
                            top=0.9, 
                            wspace=0.3, 
                            hspace=0.5)
        plt.savefig('%s.png'%(graphtitle))
        plt.close(fig)   
        os.chdir(directory)
    
    print('graphs_1behavior_3groups finished')

######## OLD
for parameter in dict_sexgroup_R['2test'].keys():
    for beh in list_interest_beh_sex:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            graphs_behaviorsum_3groups('T',dict_sexgroup_R['2test'][parameter]['Sum']['CTR'],dict_sexgroup_R['2test'][parameter]['Sum']['HFHS'],
                                        dict_sexgroup_R['2test'][parameter]['Sum']['CAF'],'Sum of 2nd and 3rd sex tests',parameter,'Sum2_SEC_%s'%(parameter))

for parameter in dict_sexgroup_P['2test'].keys():
    for beh in list_interest_beh_prereward:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            graphs_behaviorsum_3groups('P',dict_sexgroup_P['2test'][parameter]['Sum']['CTR'],dict_sexgroup_P['2test'][parameter]['Sum']['HFHS'],
                                        dict_sexgroup_P['2test'][parameter]['Sum']['CAF'],'Sum of 2nd and 3rd sex tests',parameter,'Sum2_P_SEC_%s'%(parameter))

for parameter in dict_sexgroup_A['2test'].keys():
    for beh in list_interest_beh_sex:
        if parameter == beh or parameter== 'TN_%s'%beh or parameter== 'TD_%s'%beh or parameter== 'MD_%s'%beh:
            graphs_behaviorsum_3groups('A',dict_sexgroup_A['2test'][parameter]['Sum']['CTR'],dict_sexgroup_A['2test'][parameter]['Sum']['HFHS'],
                                        dict_sexgroup_A['2test'][parameter]['Sum']['CAF'],'Sum of 2nd and 3rd sex tests',parameter,'Sum2_A_SEC_%s'%(parameter))

# ########## NIEUW
# for beh_keys in my_dict_behavior['2test'].keys():
#     for beh in list_interest_beh_sex:
#         if beh_keys == beh or beh_keys== 'TN_%s'%beh or beh_keys== 'TD_%s'%beh:
#             graphs_behaviorsum_3groups(df_R_sexsum,'T','SECREWARD',1,'%s'%beh_keys,'1st sex reward after reversal',
#                                     'BW_level','BW_SEC_rev %s'%beh_keys)

######################################################################################3
# Run dictionaries again for TDT analysis later so that animals will be excluded

# Delete the excluded rats from the metafile
for i in list_excltdt:
    metafile=metafile[metafile.RatID != i]
for s in list_excltdt_sex:
    metafile=metafile[(metafile.Test != 'SECREWARD') | ((metafile.Test == 'SECREWARD') & (metafile.RatID != s))]

# Delete the rats-tests that have too many artifacts
########## CHECK OF HET KLOPT...RH001 GING FOUT#################
for o in list_signal_artifact_excl:
    metafile=metafile[(metafile.RatID != o[:3]) & (metafile.Test != o[3:])]
    
# Create a dictionary from the metafile
dict_metafile = metafile.to_dict()

# Create lists of the metafile
list_directory_tank=metafile['directory_tank'].tolist()
list_ratid=metafile['RatID'].tolist()
list_ID=metafile['ID'].tolist()
list_blue=metafile['blue'].tolist()
list_uv=metafile['uv'].tolist()
list_virus=metafile['Virus'].tolist()
list_diet=metafile['Diet'].tolist()
list_test=metafile['Test'].tolist()
list_reward=metafile['Reward'].tolist()
list_testsession=metafile['Testsession'].tolist()
list_startbox=metafile['Startbox'].tolist()
list_light=metafile['Light'].tolist()

# Make dictionary for diet and virus
dict_diet = dict(zip(list_ratid,list_diet))
dict_virus = dict(zip(list_ratid,list_virus))
dict_id= dict(zip(list_ID,list_ratid))
dict_test=dict(zip(list_ID,list_test))
dict_testsession=dict(zip(list_ID,list_testsession))

##############################################################################################################################################################################
# Analysis of TDT data from Synapse

############################### LIGHT AND DOOR ###############################################################
# Make a definition for the behavior snips
def lightdoor_snipper(diet,test,testsession,virus='GCaMP6',correction=True,
                          sniptime_pre=5,sniptime_post=15,exclude_outliers=False,graphtitle=None):
    """
    Parameters
    ----------
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string
        Add which virus you want to analyze -> Default = 'GCaMP6'
        e.g. "GCaMP6" or "GFP"
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True
    sniptime_pre : integer
        Add the number of seconds you want the snip to start before the lights on -> Default = 5
    sniptime_post : integer
        Add the number of seconds you want the snip to end after the doors open -> Default = 15
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    dict_tdt_mean : Dictionary & Figure
        It returns a dictionary of the mean signals of the dFF signals for the period of determined snips around TTL signals
        And corrects for a baseline measure to bring back to zero.
        It also returns a figure of each individual/test with the dFF signals for the period of determined snips around TTL signals with markings
        for the lights and opening of the door, with grey each behavior-dFF and in green the mean of these signals
        In addition, it creates a heatmap.
    """
    
    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary = my_dict_process[d]

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor
        
    # Make empty dictionaries
    outs=['dFF','zscore','zscore_snip']
    dict_tdt_mean={}
    for out in outs:
        dict_tdt_mean[out]={}
    
    # Get dFF,time and fs from dictionary of processed data
    for rat,value in dictionary.items(): 
        if rat not in list_signal_artifact_excl:
            print("Start TTL_snipper %s"%(rat))
            if exclude_outliers == False:
                dFF=dictionary[rat]['dFF']
                zscore=dictionary[rat]['zscore']
                time=dictionary[rat]['time']
            else: 
                dFF=dictionary[rat]['dFF_cor']
                zscore=dictionary[rat]['zscore_cor']
                time=dictionary[rat]['time_cor']
            
            fs=dictionary[rat]['fs']
            LIGHT=dictionary[rat]['LIGHT_on']
    
            # Make an empty dictionary
            dict_tdt_mean[rat]={}
    
            # Run over every lights on
            # for on in LIGHT:
                # Only continue if the TTL is for the actual light
            if LIGHT > 100:
                # First make a continous time series of behavior events (epocs) and plot
                LIGHT_MARK = LIGHT
    
                # Now make snips of the data
                PRE_TIME = sniptime_pre # number of seconds before event onset
                POST_TIME = sniptime_post # number of seconds after
                BASELINE_START = -5 #baseline_start
                BASELINE_END = 0 #baseline_end
                TRANGE = [-PRE_TIME*np.floor(fs), POST_TIME*np.floor(fs)]
                TRANGE_BASELINE = [BASELINE_START*np.floor(fs), BASELINE_END*np.floor(fs)]
    
                # # time span for peri-event filtering, PRE and POST, in samples
                # for event,name in zip(EVENTS,LABEL_EVENTS):
                # dFF_snips = []
                # dFF_snips_BASELINE=[]
                array_ind = []
                pre_START = []
                post_START = []
                pre_BASELINE= []
                post_BASELINE= []
                dFF_snips_cor=[]
                zscore_snips_cor=[]
    
                # find first time index after event onset
                array_ind.append(np.where(time > LIGHT_MARK)[0][0])
                # find index corresponding to pre and post START durations
                pre_START.append(array_ind[-1] + TRANGE[0])
                post_START.append(array_ind[-1] + TRANGE[1])
                pre_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[0])
                post_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[1])
                BASELINE=dFF[int(pre_BASELINE[-1]):int(post_BASELINE[-1])]
                BASELINE_zscore=zscore[int(pre_BASELINE[-1]):int(post_BASELINE[-1])]
                mean_BASELINE=np.mean(BASELINE)
                mean_BASELINE_zscore=np.mean(BASELINE_zscore)
                std_BASELINE=np.std(BASELINE)
                std_BASELINE_zscore=np.std(BASELINE_zscore)
                
                dFF_snip=dFF[int(pre_START[-1]):int(post_START[-1])]
                dFF_snips_cor.append(np.subtract(dFF_snip,mean_BASELINE))
    
                zscore_snip=zscore[int(pre_START[-1]):int(post_START[-1])]
                zscore_snips_cor.append(np.subtract(zscore_snip,mean_BASELINE_zscore))
                
                # Based on condition correct or don't correct for baseline
                if correction == True:
                    dFF_snips=dFF_snips_cor
                    zscore_snips=zscore_snips_cor
                else:
                    dFF_snips=dFF_snip
                    zscore_snips=zscore_snip
                
                # Remove the snips that are shorter in size
                max1 = np.max([np.size(x) for x in dFF_snips])
                dFF_snips=[snip for snip in dFF_snips if np.size(snip)==max1]                    
    
                mean_dFF_snips = np.mean(dFF_snips, axis=0)
                std_dFF_snips = np.std(mean_dFF_snips, axis=0)
    
                mean_zscore_snips = np.mean(zscore_snips, axis=0)
                std_zscore_snips = np.std(mean_zscore_snips, axis=0)
    
                # Calculate z-score from only the dFF snip 
                zall = []
                for snip in dFF_snips: 
                    zb = np.mean(snip)
                    zsd = np.std(snip)
                    zall.append((snip - zb)/zsd)
                   
                zscore_dFF_snips = np.mean(zall, axis=0) 
    
                # Put the data in the dictionaries
                dict_tdt_mean['dFF'][rat]=mean_dFF_snips
                dict_tdt_mean['zscore'][rat]=mean_dFF_snips
                dict_tdt_mean['zscore_snip'][rat]=zscore_dFF_snips 
    
                peri_time = np.linspace(1, len(mean_dFF_snips), len(mean_dFF_snips))/fs - PRE_TIME
                
                if graphtitle == None:
                    pass
                else:
                    # Change directory to output folder
                    if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat):
                        os.mkdir(directory_graph+directory_TDT_lightdoor_perrat)
                    if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore"):
                        os.mkdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore")
                    if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips"):
                        os.mkdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips")
    
                    # Make a peri-event STARTulus plot and heatmap
                    os.chdir(directory_graph+directory_TDT_lightdoor_perrat)
                    fig1 = plt.figure(figsize=(6,10))
                    ax1 = fig1.add_subplot(211)
                    for snip in dFF_snips:
                        p1, = ax1.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                    p2, = ax1.plot(peri_time, mean_dFF_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                    ax1.axis('tight')
                    ax1.set_xlabel('Seconds',fontsize=16)
                    ax1.set_ylabel(r'$\Delta$F/F',fontsize=16)
                    ax1.set_title('%s_%s_%s_%s'%(graphtitle,rat,diet,virus),fontsize=16)
                    ax1.legend(handles=[p1, p2], bbox_to_anchor=(1.1, 1.05),fontsize=16);
    
                    ax2 = fig1.add_subplot(212)
                    cs = ax2.imshow(dFF_snips, cmap=plt.cm.Greys,
                                    interpolation='none', extent=[-PRE_TIME,POST_TIME,len(dFF_snips),0],)
                    ax2.set_ylabel('Trial Number')
                    ax2.set_yticks(np.arange(.5, len(dFF_snips), 2))
                    ax2.set_yticklabels(np.arange(0, len(dFF_snips), 2))
                    fig1.colorbar(cs)
                    plt.savefig("dFF %s_%s_%s_%s.png"%(graphtitle,rat,diet,virus))
                    plt.close(fig1)
    
                    os.chdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore")
                    fig2 = plt.figure(figsize=(6,10))
                    ax3 = fig2.add_subplot(211)
                    for snip in zscore_snips:
                        p1, = ax3.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                    p2, = ax3.plot(peri_time, mean_zscore_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                    ax3.axis('tight')
                    ax3.set_xlabel('Seconds',fontsize=16)
                    ax3.set_ylabel('z-score',fontsize=16)
                    ax3.set_title('%s_%s_%s_%s'%(graphtitle,rat,diet,virus),fontsize=16)
                    ax3.legend(handles=[p1, p2], bbox_to_anchor=(1.1, 1.05),fontsize=16);
    
                    ax4 = fig2.add_subplot(212)
                    cs = ax4.imshow(dFF_snips, cmap=plt.cm.Greys,
                                    interpolation='none', extent=[-PRE_TIME,POST_TIME,len(dFF_snips),0],)
                    ax4.set_ylabel('Trial Number')
                    ax4.set_yticks(np.arange(.5, len(dFF_snips), 2))
                    ax4.set_yticklabels(np.arange(0, len(dFF_snips), 2))
                    fig2.colorbar(cs)
                    plt.savefig("Z_score %s_%s_%s_%s.png"%(graphtitle,rat,diet,virus))
                    plt.close(fig2)
    
                    os.chdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips")
                    fig3 = plt.figure(figsize=(6,10))
                    ax5 = fig3.add_subplot(211)
                    for snip in zall:
                        p1, = ax5.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                    p2, = ax5.plot(peri_time, zscore_dFF_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                    ax5.axis('tight')
                    ax5.set_xlabel('Seconds',fontsize=16)
                    ax5.set_ylabel('z-score',fontsize=16)
                    ax5.set_title('%s_%s_%s_%s'%(graphtitle,rat,diet,virus),fontsize=16)
                    ax5.legend(handles=[p1, p2], bbox_to_anchor=(1.1, 1.05),fontsize=16);
                
                    ax6 = fig3.add_subplot(212)
                    cs = ax6.imshow(dFF_snips, cmap=plt.cm.Greys,
                                    interpolation='none', extent=[-PRE_TIME,POST_TIME,len(dFF_snips),0],)
                    ax6.set_ylabel('Trial Number')
                    ax6.set_yticks(np.arange(.5, len(dFF_snips), 2))
                    ax6.set_yticklabels(np.arange(0, len(dFF_snips), 2))
                    fig3.colorbar(cs)
                    plt.savefig("Z_score_snip %s_%s_%s_%s.png"%(graphtitle,rat,diet,virus))
                    plt.close(fig3)
                    
                    # Change directory back
                    os.chdir(directory)
                            
    print("light_snipper done")
    return dict_tdt_mean

# Make a definition for the mean behavior snips per ratdiet,test,testsession,virus='GCaMP6',sniptime_pre=5,sniptime_post=15,output='dFF',exclude_outliers=False,graphtitle=None
def result_lightdoor_snipper(diet,test,testsession,virus='GCaMP6',correction=True,
                                 sniptime_pre=5,sniptime_post=15,exclude_outliers=False,graphtitle=None):
    """
    Parameters
    ----------
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string
        Add which virus you want to analyze -> Default = 'GCaMP6'
        e.g. "GCaMP6" or "GFP"
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True
    sniptime_pre : integer
        Add the number of seconds you want the snip to start before the lights on -> Default = 5
    sniptime_post : integer
        Add the number of seconds you want the snip to end after the doors open -> Default = 15
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None
    Returns
    -------
    dict_ratmeans : Dictionary & Figure
        It returns a dictionary of the mean signals (per treatment) of the dFF signals for the period of determined snips around TTL signals
        And corrects for a baseline measure to bring back to zero, and takes the averages per rat in one figure.
        It also returns a figure of the mean dFF signals per rat for the period of determined snips around TTL signals with markings
        for the lights and opening of the door, with grey each behavior-dFF and in green the mean of these signals
        In addition, it creates a heatmap.
    """
    print(" Start result_lightdoor_snipper")

    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary_analysis = my_dict_process[d]

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    dictionary=lightdoor_snipper(diet,test,testsession,virus=virus,correction=correction,
                                     sniptime_pre=sniptime_pre,sniptime_post=sniptime_post, 
                                     exclude_outliers=exclude_outliers)
    
    stats=['mean','sem']
    outs=['dFF','zscore','zscore_snip']
    
    list_of_means_dFF=[]
    list_of_means_zscore=[]
    list_of_means_zscore_snip=[]

    dict_ratmeans={}
    for out in outs:
        dict_ratmeans[out]={}
        for stat in stats:
            dict_ratmeans[out][stat]=[]
        
    for rat,value in dictionary['dFF'].items():
        list_of_means_dFF.append(value)
    for rat,value in dictionary['zscore'].items():
        list_of_means_zscore.append(value)
    for rat,value in dictionary['zscore_snip'].items():
        list_of_means_zscore_snip.append(value)

    yarray_dFF = np.array(list_of_means_dFF)
    y_dFF = np.mean(yarray_dFF, axis=0)
    yerror_dFF = np.std(yarray_dFF, axis=0)/np.sqrt(len(yarray_dFF))

    # mean_dFF_behavior = [sum(sub_list) / len(sub_list) for sub_list in zip(*list_of_means)]
    dict_ratmeans['dFF']['mean']=y_dFF
    dict_ratmeans['dFF']['sem']=yerror_dFF

    yarray_zscore = np.array(list_of_means_zscore)
    y_zscore = np.mean(yarray_zscore, axis=0)
    yerror_zscore = np.std(yarray_zscore, axis=0)/np.sqrt(len(yarray_zscore))

    # mean_zscore_behavior = [sum(sub_list) / len(sub_list) for sub_list in zip(*list_of_means)]
    dict_ratmeans['zscore']['mean']=y_zscore
    dict_ratmeans['zscore']['sem']=yerror_zscore

    yarray_zscore_snip = np.array(list_of_means_zscore_snip)
    y_zscore_snip = np.mean(yarray_zscore_snip, axis=0)
    yerror_zscore_snip = np.std(yarray_zscore_snip, axis=0)/np.sqrt(len(yarray_zscore_snip))

    # mean_zscore_snip_behavior = [sum(sub_list) / len(sub_list) for sub_list in zip(*list_of_means)]
    dict_ratmeans['zscore_snip']['mean']=y_zscore_snip
    dict_ratmeans['zscore_snip']['sem']=yerror_zscore_snip
    
    length=y_dFF.size

    # Get fs from dictionary of processed data
    for rat,value in dictionary['dFF'].items():        
        fs=dictionary_analysis[rat]['fs']
        x = np.linspace(1, length, length)/fs - sniptime_pre

    # Make a peri-event stimulus plot and heatmap
    if graphtitle == None:
        pass
    else:
        # Change directory to output folder
        # Change directory to output folder
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat):
            os.mkdir(directory_graph+directory_TDT_lightdoor_perrat)
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore"):
            os.mkdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore")
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips"):
            os.mkdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips")
        
        os.chdir(directory_graph+directory_TDT_lightdoor_perrat)
        fig1 = plt.figure(figsize=(6,10))
        ax1 = fig1.add_subplot(211)
        for signal in list_of_means_dFF:
            p1, = ax1.plot(x, signal, linewidth=.5, color=color_snips, label='Individual Trials')
        p2, = ax1.plot(x, y_dFF, linewidth=2, color=color_GCaMP, label='Mean Response')
        # Plotting time stamps
        p3 = ax1.axvline(x=0, linewidth=3, color='slategray', label="Light on")
        p4 = ax1.axvline(x=Timetest_anticipatory, linewidth=3, color='dimgray', label='Door open')
        ax1.axis('tight')
        ax1.set_xlabel('Seconds',fontsize=16)
        ax1.set_ylabel(r'$\Delta$F/F',fontsize=16)
        ax1.set_title('%s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession),fontsize=16)
        ax1.legend(handles=[p1, p2, p3, p4], bbox_to_anchor=(1.1, 1.05),fontsize=16);
    
        ax2 = fig1.add_subplot(212)
        cs = ax2.imshow(list_of_means_dFF, cmap=plt.cm.Greys,
                        interpolation='none', extent=[-sniptime_pre,sniptime_post,len(list_of_means_dFF),0],)
        ax2.set_ylabel('Trial Number')
        ax2.set_yticks(np.arange(0, len(list_of_means_dFF), 1))
        ax2.set_yticklabels(np.arange(0, len(list_of_means_dFF), 1))
        fig1.colorbar(cs)
        plt.savefig('dFF %s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession))
        plt.close(fig1)

        os.chdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscore")
        fig2 = plt.figure(figsize=(6,10))
        ax1 = fig2.add_subplot(211)
        for signal in list_of_means_zscore:
            p1, = ax1.plot(x, signal, linewidth=.5, color=color_snips, label='Individual Trials')
        p2, = ax1.plot(x, y_zscore, linewidth=2, color=color_GCaMP, label='Mean Response')
        # Plotting time stamps
        p3 = ax1.axvline(x=0, linewidth=3, color='slategray', label="Light on")
        p4 = ax1.axvline(x=Timetest_anticipatory, linewidth=3, color='dimgray', label='Door open')
        ax1.axis('tight')
        ax1.set_xlabel('Seconds',fontsize=16)
        ax1.set_ylabel('z-score',fontsize=16)
        ax1.set_title('%s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession),fontsize=16)
        ax1.legend(handles=[p1, p2, p3, p4], bbox_to_anchor=(1.1, 1.05),fontsize=16);
    
        ax2 = fig2.add_subplot(212)
        cs = ax2.imshow(list_of_means_zscore, cmap=plt.cm.Greys,
                        interpolation='none', extent=[-sniptime_pre,sniptime_post,len(list_of_means_zscore),0],)
        ax2.set_ylabel('Trial Number')
        ax2.set_yticks(np.arange(0, len(list_of_means_zscore), 1))
        ax2.set_yticklabels(np.arange(0, len(list_of_means_zscore), 1))
        fig2.colorbar(cs)
        plt.savefig('zscore %s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession))
        plt.close(fig2)

        os.chdir(directory_graph+directory_TDT_lightdoor_perrat+"/zscoresnips")
        fig3 = plt.figure(figsize=(6,10))
        ax1 = fig3.add_subplot(211)
        for signal in list_of_means_zscore_snip:
            p1, = ax1.plot(x, signal, linewidth=.5, color=color_snips, label='Individual Trials')
        p2, = ax1.plot(x, y_zscore_snip, linewidth=2, color=color_GCaMP, label='Mean Response')
        # Plotting time stamps
        p3 = ax1.axvline(x=0, linewidth=3, color='slategray', label="Light on")
        p4 = ax1.axvline(x=Timetest_anticipatory, linewidth=3, color='dimgray', label='Door open')
        ax1.axis('tight')
        ax1.set_xlabel('Seconds',fontsize=16)
        ax1.set_ylabel('z-score',fontsize=16)
        ax1.set_title('%s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession),fontsize=16)
        ax1.legend(handles=[p1, p2, p3, p4], bbox_to_anchor=(1.1, 1.05),fontsize=16);
    
        ax2 = fig3.add_subplot(212)
        cs = ax2.imshow(list_of_means_zscore_snip, cmap=plt.cm.Greys,
                        interpolation='none', extent=[-sniptime_pre,sniptime_post,len(list_of_means_zscore_snip),0],)
        ax2.set_ylabel('Trial Number')
        ax2.set_yticks(np.arange(0, len(list_of_means_zscore_snip), 1))
        ax2.set_yticklabels(np.arange(0, len(list_of_means_zscore_snip), 1))
        fig3.colorbar(cs)
        plt.savefig('zscore_snip %s_%s_%s_%s_%s'%(graphtitle,diet,virus,test,testsession))
        plt.close(fig3)

        # Change directory back
        os.chdir(directory)
    
    print("result_light_snipper done")
    return dict_ratmeans

# Make a definition for comparing GCAMP signals from light snips
def compare_light_snipper (dictionary1,dictionary2,dictionary3,condition1,condition2,condition3,
                           sniptime_pre=5,exclude_outliers=False,graphtitle=None):
    """
    Note -> If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dictionary1 : dictionary
        Add dictionary of 1st treatment group
        e.g. RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1
    dictionary2 : dictionary
        Add dictionary of 2nd treatment group
        e.g. RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1
    dictionary3 : dictionary
        Add dictionary of 3rd treatment group
        e.g. RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1
    condition1 : string
        Add the name of the treatment corresponding to dictionary 1
        e.g. "CTR", "CAF","HFHS"
    condition2 : string
        Add the name of the treatment corresponding to dictionary 2
        e.g. "CTR", "CAF","HFHS"
    condition3 : string
        Add the name of the treatment corresponding to dictionary 3
        e.g. "CTR", "CAF","HFHS"
    sniptime_pre : integer -> Default = 5
        Add the number of seconds you want the snip to start before the lights on
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string > Default = None
        Add the name of the figure. If no figure is wanted, add an empty string ""

    Returns
    -------
    Figure
        It returns a graph of the mean signals of the dFF signals for the period of determined snips around 
        lights and door opening per group and compares in one figure.
        Figures of the mean dFF signals aligned to the behaviors, plus sem-bands.
    """
    
    print("Start compare_light_snipper")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    length=len(dictionary1['dFF']['mean'])

    # Get fs from dictionary of processed data
    for rat,value in my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'].items():        
        fs=my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'][rat]['fs']
        x = np.linspace(1, length, length)/fs - sniptime_pre
    
    # Make a peri-event stimulus plot and heatmap
    if graphtitle == None:
        pass
    else:
        # Change directory to output folder
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor):
            os.mkdir(directory_graph+directory_TDT_lightdoor)
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor+"/zscore"):
            os.mkdir(directory_graph+directory_TDT_lightdoor+"/zscore")
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips"):
            os.mkdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips")
            
            
        os.chdir(directory_graph+directory_TDT_lightdoor)
        sns.set(style="ticks", rc=custom_params)
        fig1 = plt.figure(figsize=(15,9))
        ax = fig1.add_subplot(111)
        xx =[-5,0,5,10,15]
        yy =[-10,-5,0,5,10,15,20]
        p1, = ax.plot(x, dictionary1['dFF']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['dFF']['mean']-dictionary1['dFF']['sem'], dictionary1['dFF']['mean']+dictionary1['dFF']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['dFF']['mean'], linewidth=0.8, color=color_HFHS, label=condition2)
        ax.fill_between(x, dictionary2['dFF']['mean']-dictionary2['dFF']['sem'], dictionary2['dFF']['mean']+dictionary2['dFF']['sem'], color=color_HFHS_shadow, alpha=0.4)
        p3, = ax.plot(x, dictionary3['dFF']['mean'], linewidth=0.8, color=color_CAF, label=condition3)
        ax.fill_between(x, dictionary3['dFF']['mean']-dictionary3['dFF']['sem'], dictionary3['dFF']['mean']+dictionary3['dFF']['sem'], color=color_CAF_shadow, alpha=0.4)
        # Plotting the zero line
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(yy)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2, p3], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("dFF Lightdoor %s.png"%(graphtitle))
        plt.close(fig1)

        os.chdir(directory_graph+directory_TDT_lightdoor+"/zscore")
        sns.set(style="ticks", rc=custom_params)
        fig2 = plt.figure(figsize=(15,9))
        ax = fig2.add_subplot(111)
        xx =[-5,0,5,10,15]
        zz =[-4,-2,0,2,4,6,8,10,12,14,16,18]
        p1, = ax.plot(x, dictionary1['zscore']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['zscore']['mean']-dictionary1['zscore']['sem'], dictionary1['zscore']['mean']+dictionary1['zscore']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['zscore']['mean'], linewidth=0.8, color=color_HFHS, label=condition2)
        ax.fill_between(x, dictionary2['zscore']['mean']-dictionary2['zscore']['sem'], dictionary2['zscore']['mean']+dictionary2['zscore']['sem'], color=color_HFHS_shadow, alpha=0.4)
        p3, = ax.plot(x, dictionary3['zscore']['mean'], linewidth=0.8, color=color_CAF, label=condition3)
        ax.fill_between(x, dictionary3['zscore']['mean']-dictionary3['zscore']['sem'], dictionary3['zscore']['mean']+dictionary3['zscore']['sem'], color=color_CAF_shadow, alpha=0.4)
        # Plotting the zero line
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(zz)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel('z-score',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2, p3], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("zscore Lightdoor %s.png"%(graphtitle))
        plt.close(fig2)

        os.chdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips")
        sns.set(style="ticks", rc=custom_params)
        fig3 = plt.figure(figsize=(15,9))
        ax = fig3.add_subplot(111)
        xx =[-5,0,5,10,15]
        zz =[-3,-2,-1,0,1,2,3,4,5,6]
        p1, = ax.plot(x, dictionary1['zscore_snip']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['zscore_snip']['mean']-dictionary1['zscore_snip']['sem'], dictionary1['zscore_snip']['mean']+dictionary1['zscore_snip']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['zscore_snip']['mean'], linewidth=0.8, color=color_HFHS, label=condition2)
        ax.fill_between(x, dictionary2['zscore_snip']['mean']-dictionary2['zscore_snip']['sem'], dictionary2['zscore_snip']['mean']+dictionary2['zscore_snip']['sem'], color=color_HFHS_shadow, alpha=0.4)
        p3, = ax.plot(x, dictionary3['zscore_snip']['mean'], linewidth=0.8, color=color_CAF, label=condition3)
        ax.fill_between(x, dictionary3['zscore_snip']['mean']-dictionary3['zscore_snip']['sem'], dictionary3['zscore_snip']['mean']+dictionary3['zscore_snip']['sem'], color=color_CAF_shadow, alpha=0.4)
        # Plotting the zero line
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(zz)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel('z-score',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2, p3], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("zscore_snip Lightdoor %s.png"%(graphtitle))
        plt.close(fig3)

        # Change directory back
        os.chdir(directory)
        
    print("compare_light_snipper done")

# Make a definition for comparing GCAMP signals from light snips
def compare_light_snipper_2cond (dictionary1,dictionary2,condition1,condition2,
                                 sniptime_pre=5,exclude_outliers=False,graphtitle=None):
    """
    Note -> If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dictionary1 : dictionary
        Add dictionary of 1st treatment group
        e.g. RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1
    dictionary2 : dictionary
        Add dictionary of 2nd treatment group
        e.g. RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1
    condition1 : string
        Add the name of the treatment corresponding to dictionary 1
        e.g. "CTR", "CAF","HFHS"
    condition2 : string
        Add the name of the treatment corresponding to dictionary 2
        e.g. "CTR", "CAF","HFHS"
    sniptime_pre : integer -> Default = 5
        Add the number of seconds you want the snip to start before the lights on
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    Figure
        It returns a graph of the mean signals of the dFF signals for the period of determined snips around 
        lights and door opening per group and compares in one figure.
        Figures of the mean dFF signals aligned to the behaviors, plus sem-bands.
    """
    
    print("Start compare_light_snipper_2cond")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    length=len(dictionary1['dFF']['mean'])

    # Get fs from dictionary of processed data
    for rat,value in my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'].items():        
        fs=my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'][rat]['fs']
        x = np.linspace(1, length, length)/fs - sniptime_pre
    
    # Make a peri-event stimulus plot and heatmap
    if graphtitle == None:
        pass
    else:
        # Change directory to output folder
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor):
            os.mkdir(directory_graph+directory_TDT_lightdoor)
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor+"/zscore"):
            os.mkdir(directory_graph+directory_TDT_lightdoor+"/zscore")
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips"):
            os.mkdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips")
            
            
        os.chdir(directory_graph+directory_TDT_lightdoor)
        sns.set(style="ticks", rc=custom_params)
        fig1 = plt.figure(figsize=(15,9))
        ax = fig1.add_subplot(111)
        xx =[-5,0,5,10,15]
        yy =[-10,-5,0,5,10,15,20]
        p1, = ax.plot(x, dictionary1['dFF']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['dFF']['mean']-dictionary1['dFF']['sem'], dictionary1['dFF']['mean']+dictionary1['dFF']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['dFF']['mean'], linewidth=0.8, color=color_CAF, label=condition2)
        ax.fill_between(x, dictionary2['dFF']['mean']-dictionary2['dFF']['sem'], dictionary2['dFF']['mean']+dictionary2['dFF']['sem'], color=color_CAF_shadow, alpha=0.4)
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(yy)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("dFF Lightdoor_CAF %s.png"%(graphtitle))
        plt.close(fig1)

        os.chdir(directory_graph+directory_TDT_lightdoor+"/zscore")
        sns.set(style="ticks", rc=custom_params)
        fig2 = plt.figure(figsize=(15,9))
        ax = fig2.add_subplot(111)
        xx =[-5,0,5,10,15]
        zz =[-4,-2,0,2,4,6,8,10,12,14,16,18]
        p1, = ax.plot(x, dictionary1['zscore']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['zscore']['mean']-dictionary1['zscore']['sem'], dictionary1['zscore']['mean']+dictionary1['zscore']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['zscore']['mean'], linewidth=0.8, color=color_CAF, label=condition2)
        ax.fill_between(x, dictionary2['zscore']['mean']-dictionary2['zscore']['sem'], dictionary2['zscore']['mean']+dictionary2['zscore']['sem'], color=color_CAF_shadow, alpha=0.4)
        # Plotting the zero line
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(zz)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel('z-score',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("zscore Lightdoor_CAF %s.png"%(graphtitle))
        plt.close(fig2)

        os.chdir(directory_graph+directory_TDT_lightdoor+"/zscore_snips")
        sns.set(style="ticks", rc=custom_params)
        fig3 = plt.figure(figsize=(15,9))
        ax = fig3.add_subplot(111)
        xx =[-5,0,5,10,15]
        zz =[-3,-2,-1,0,1,2,3,4,5,6]
        p1, = ax.plot(x, dictionary1['zscore_snip']['mean'], linewidth=0.8, color=color_CTR, label=condition1)
        ax.fill_between(x, dictionary1['zscore_snip']['mean']-dictionary1['zscore_snip']['sem'], dictionary1['zscore_snip']['mean']+dictionary1['zscore_snip']['sem'], color=color_CTR_shadow, alpha=0.4)
        p2, = ax.plot(x, dictionary2['zscore_snip']['mean'], linewidth=0.8, color=color_CAF, label=condition2)
        ax.fill_between(x, dictionary2['zscore_snip']['mean']-dictionary2['zscore_snip']['sem'], dictionary2['zscore_snip']['mean']+dictionary2['zscore_snip']['sem'], color=color_CAF_shadow, alpha=0.4)
        # Plotting the zero line
        ax.axvline(x=0, linewidth=2, color=color_light, label="Light on")
        ax.axvline(x=Timetest_anticipatory, linewidth=2, color=color_door, label='Door open')
        ax.set_xticks(xx)
        ax.set_yticks(zz)
        ax.set_xlabel('Seconds',fontsize=16)
        ax.set_ylabel('z-score',fontsize=16)
        # ax.set_title('%s'%(graphtitle),fontsize=16)
        ax.legend(handles=[p1, p2], loc="upper left",fontsize=16);
        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
        # plt.savefig("Lightdoor_%s.png"%(graphtitle))
        plt.savefig("zscore_snip Lightdoor_CAF %s.png"%(graphtitle))
        plt.close(fig3)

        # Change directory back
        os.chdir(directory)
        
    print("compare_light_snipper_2cond done")
######### BEHAVIOR ###################################################################################
def make_dict_start_behavior(dataframe,diet,test,testsession,
                             virus='GCaMP6'):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Default ='GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"

    Returns
    -------
    Dictionary with start times of the behaviors
    (when a behavior was scored (except Mount, intromission, ejaculation))
    """
   
    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary = my_dict_process[d]
    
    # Create a dict for the behavior times
    make_dict_start_beh={}
    for key in dictionary.keys():
        make_dict_start_beh[key]={}
        for beh in list_beh_tdt:
            make_dict_start_beh[key][beh]=[]
    
    # Get times linked to the behaviors per test per rat and place in dictionary
    for rat,value in dictionary.items():    
        if rat in dict_light.keys():
            LIGHT_on=dictionary[rat]['LIGHT_on']
            LIGHT_video=dict_light[rat]
            delay=LIGHT_on-LIGHT_video
            print(rat,delay)
        
        # Fill in the dictionaries with the start and end times of the behaviors
        # for keys,value in make_dict_start_beh.items():
        for behav in list_beh_tdt:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe[BEH] == behav)]
            temp_start = list(df_reduced['Beh_start']+ delay)
            make_dict_start_beh[rat][behav]=temp_start 

        for behav_EB in list_tdt_EB:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['EB_Eating_mark'] == behav_EB)]
            temp_start = list(df_reduced['Beh_start']+ delay)
            make_dict_start_beh[rat][behav_EB]=temp_start 

        # for behav_EB_plus in list_tdt_EB_plus: # should be off because are same names for behavior as EB
        #     df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['EB_eating_mark2'] == behav_EB_plus)]
        #     temp_start = list(df_reduced['Beh_start']+ delay)
        #     make_dict_start_beh[rat][behav_EB_plus]=temp_start 

        for behav_SB in list_tdt_SB:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['SB_sex_mark'] == behav_SB)]
            temp_start = list(df_reduced['Beh_start']+ delay)
            make_dict_start_beh[rat][behav_SB]=temp_start 
        
        df_lordosis = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW))]
        temp_start_lordosis = list(df_lordosis['Beh_start']+ delay)
        make_dict_start_beh[rat]['Lordosis']=temp_start_lordosis 
        
        df_LM = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BQ)]
        temp_start_LM = list(df_LM['Beh_start']+ delay)
        make_dict_start_beh[rat]['LM']=temp_start_LM

        df_LI = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BR)]
        temp_start_LI = list(df_LI['Beh_start']+ delay)
        make_dict_start_beh[rat]['LI']=temp_start_LI

        df_LE = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BS)]
        temp_start_LE = list(df_LE['Beh_start']+ delay)
        make_dict_start_beh[rat]['LE']=temp_start_LE

    return make_dict_start_beh

def make_dict_end_behavior(dataframe,diet,test,testsession,
                           virus='GCaMP6'):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Deafult = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"

    Returns
    -------
    Dictionary with end times of the behaviors
    (when a next behavior was scored, and thus ending the previous behavior (Mount, intromission, and ejaculation signal
    end of lordosis))
    """

    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary = my_dict_process[d]
    
    # Create a dict for the behavior times
    make_dict_end_beh={}
    for key in dictionary.keys():
        make_dict_end_beh[key]={}
        for beh in list_beh_tdt:
            make_dict_end_beh[key][beh]=[]
    
    # Get times linked to the behaviors per test per rat and place in dictionary
    for rat,value in dictionary.items():    
        if rat in dict_light.keys():
            LIGHT_on=dictionary[rat]['LIGHT_on']
            LIGHT_video=dict_light[rat]
            delay=LIGHT_on-LIGHT_video
            print(rat,delay)
            
        # Fill in the dictionaries with the end and end times of the behaviors
        # for keys,value in make_dict_end_beh.items():
        for behav in list_beh_tdt:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe[BEH] == behav)]
            temp_end = list(df_reduced['Beh_end']+ delay)
            make_dict_end_beh[rat][behav]=temp_end 

        for behav_EB in list_tdt_EB:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['EB_Eating_mark'] == behav_EB)]
            temp_end = list(df_reduced['Beh_end']+ delay)
            make_dict_end_beh[rat][behav_EB]=temp_end 

        # for behav_EB_plus in list_tdt_EB_plus:
        #     df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['EB_eating_mark2'] == behav_EB_plus)]
        #     temp_end = list(df_reduced['Beh_end']+ delay)
        #     make_dict_end_beh[rat][behav_EB_plus]=temp_end 

        for behav_SB in list_tdt_SB:
            df_reduced = dataframe[(dataframe['ID'] == rat) & (dataframe['SB_sex_mark'] == behav_SB)]
            temp_end = list(df_reduced['Beh_end']+ delay)
            make_dict_end_beh[rat][behav_SB]=temp_end

        df_lordosis = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW))]
        temp_end_lordosis = list(df_lordosis['Beh_end']+ delay)
        make_dict_end_beh[rat]['Lordosis']=temp_end_lordosis 

        df_LM = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BQ)]
        temp_end_LM = list(df_LM['Beh_end']+ delay)
        make_dict_end_beh[rat]['LM']=temp_end_LM

        df_LI = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BR)]
        temp_end_LI = list(df_LI['Beh_end']+ delay)
        make_dict_end_beh[rat]['LI']=temp_end_LI

        df_LE = dataframe[(dataframe['ID'] == rat) & ((dataframe[BEH] == BU)|(dataframe[BEH] == BV)|(dataframe[BEH] == BW)) & (dataframe['Next_beh']==BS)]
        temp_end_LE = list(df_LE['Beh_end']+ delay)
        make_dict_end_beh[rat]['LE']=temp_end_LE
            
    return make_dict_end_beh

#################################################################################################################
################## EXCLUDE PREVIOUS BEHAVIORS ###################################################################
#################################################################################################################
# Create definitions that retrieve the timings of certain behaviors
def make_dict_start_behavior_excl(dataframe,diet,test,testsession,list_relevant_behaviors=list_relevant_behaviors,
                                  virus='GCaMP'):
    """
    Parameters
    ----------
    dataframe : DataFrame
        Add dataframe of the data you want to process
        e.g. data_T, data_B, data_R, data_P, data_I
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Default = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    list_relevant_behaviors : list
        Add a list with the behaviors that cannot happen before the behavior you explore

    Returns
    -------
    Dictionary with start times of the behaviors EXCLUDING the behaviors before another (relevant) behavior has taken place.
    """
    print("Start make dict start behavior exclude")

    # Make a new dictionary with start times excluding behavior before which another behavior has taken place
    original_dict=make_dict_start_behavior(dataframe,diet,test,testsession,virus=virus)
    new_dict={}
    temp_dict={}
    final_dict={}
    for rat in original_dict.keys():
        new_dict[rat]={}
        temp_dict[rat]={}
        final_dict[rat]={}
        
    # Create a temporary dictionary of start times that includes all times of behaviors              
    for rat,behaviors in original_dict.items():   
        temp=[]           
        for beh,time1 in behaviors.items():
            if beh in list_relevant_behaviors:
                for i in time1:
                    temp.append(i)
        temp_dict[rat]=temp
        temp_dict[rat].sort()
    
    # Create a new dictionary after excluding behaviors with all times of behaviors
    for rat,times in temp_dict.items():
        temp=[]
        for index, elem in enumerate(times):
            if (len(times) and index - 1 >= 0):
                prev_el = (times[index-1])
                curr_el = (elem)
                if curr_el-prev_el > 5:
                    temp.append(curr_el)
        new_dict[rat]=temp
    
    # Create a new dictionary per behavior excluding the behaviors that needed exclusion
    for rat1,behaviors in original_dict.items():
        for beh, times in behaviors.items():
            temp=[]
            for time1 in times:
                for rat2, time2 in new_dict.items():
                    if rat1 == rat2:
                        if time1 in time2:
                            temp.append(time1)
            final_dict[rat1][beh]=temp
   
    return final_dict   

# Create definitions that retrieve the timings of certain behaviors
def make_dict_end_behavior_excl(dataframe,diet,test,testsession,list_relevant_behaviors=list_relevant_behaviors,
                                  virus='GCaMP'):
    """
    Parameters
    ----------
    dataframe : DataFrame
        Add dataframe of the data you want to process
        e.g. data_T, data_B, data_R, data_P, data_I
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Default = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    list_relevant_behaviors : list
        Add a list with the behaviors that cannot happen before the behavior you explore
        
    Returns
    -------
    Dictionary with end times of the behaviors EXCLUDING the behaviors before another (relevant) behavior has taken place.
    """
    print("Start make dict end behavior exclude")

    # Make a new dictionary with end times excluding behavior before which another behavior has taken place
    
    original_dict=make_dict_end_behavior(dataframe,diet,test,testsession,virus=virus)
    new_dict={}
    temp_dict={}
    final_dict={}
    for rat in original_dict.keys():
        new_dict[rat]={}
        temp_dict[rat]={}
        final_dict[rat]={}
    
    # Create a temporary dictionary of end times that includes all times of behaviors              
    for rat,behaviors in original_dict.items():   
        temp=[]           
        for beh,time1 in behaviors.items():
            if beh in list_relevant_behaviors:
                for i in time1:
                    temp.append(i)
        temp_dict[rat]=temp
        temp_dict[rat].sort()
    
    # Create a new dictionary after excluding behaviors with all times of behaviors
    for rat,times in temp_dict.items():
        temp=[]
        for index, elem in enumerate(times):
            if (len(times) and index - 1 >= 0):
                prev_el = (times[index-1])
                curr_el = (elem)
                if curr_el-prev_el > 5:
                    temp.append(curr_el)
        new_dict[rat]=temp
    
    # Create a new dictionary per behavior excluding the behaviors that needed exclusion
    for rat1,behaviors in original_dict.items():
        for beh, times in behaviors.items():
            temp=[]
            for time1 in times:
                for rat2, time2 in new_dict.items():
                    if rat1 == rat2:
                        if time1 in time2:
                            temp.append(time1)
            final_dict[rat1][beh]=temp

# SNIPPER WITH CORRECTION
# Make a definition for the behavior snips corrected for baseline
def behavior_snipper(dataframe,diet,test,testsession,virus='GCaMP6',
                     correction=True, beh_list=list_beh_tdt_plus,sniptime_pre=2,sniptime_post=5,exclude_outliers=False,
                     excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,graphtitle=None):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Deafult = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True
    beh_list : list -> Default = list_beh_tdt
        Add the list with behaviors that need to be analyzed -> Default is list_beh_tdt
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the amount of seconds before the start of the behavior that needs to be analyzed
    sniptime_post : integer -> Default = 5
        Add the amount of seconds after the start of the behavior that needs to be analyzed
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    excluding_behaviors : string -> Default = 'exclude'
        Add "exclude" if you want the delete the behaviors before which another behavior has taken place
    list_relevant_behaviors : list -> Default = list_relevant_behaviors
        If you have "exclude", add a list with the behaviors that cannot happen before the behavior you explore
        Note -> if you don't exclude, just name a random list. This variable will then not be used.
    graphtitle : string
            Add the start name of the figure that is saved. If no figure is needed, type ""

    Returns
    -------
    Dictionary & Figures (per rat and test)
    Dictionary with corrected dFF of snips before and after the behaviors per rat and per test (and other information)
    Figures of each individual and the mean dFF signals aligned to the behaviors
    Correction is done by taking the average of the dFF signal during the defined "baseline" period, and correcting 
    the real dFF by minusing this baseline. The signals are thus "aligned to zero" from the start.
    """
    
    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary = my_dict_process[d]

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    if excluding_behaviors== "exclude":
        dict_start_beh=make_dict_start_behavior_excl(dataframe,diet,test,testsession,virus=virus,list_relevant_behaviors=list_relevant_behaviors)
        # dict_end_beh=make_dict_end_behavior_excl(dataframe,diet,test,testsession,virus=virus,list_relevant_behaviors=list_relevant_behaviors)
    else:        
        dict_start_beh=make_dict_start_behavior(dataframe,diet,test,testsession,virus=virus)
        # dict_end_beh=make_dict_end_behavior(dataframe,diet,test,testsession,virus=virus)
    
    # Make empty dictionaries
    dict_tdt_mean={}

    outs=['dFF','zscore','zscore_snip']
    
    for out in outs:
        dict_tdt_mean[out]={}        

    # Get dFF,time and fs from dictionary of processed data
    for rat,value in dictionary.items():  
        print("Start behavior_snipper %s"%(rat))
        if rat not in list_signal_artifact_excl:
            if exclude_outliers == False:
                dFF=dictionary[rat]['dFF']
                zscore=dictionary[rat]['zscore']
                time=dictionary[rat]['time']
            else: 
                dFF=dictionary[rat]['dFF_cor']
                zscore=dictionary[rat]['zscore_cor']
                time=np.array(dictionary[rat]['time_cor'])
    
            fs=dictionary[rat]['fs']
            maxtime=np.max(time[-1])
    
            # Make an empty dictionary
            for out in outs:
                dict_tdt_mean[out][rat]={}
            
            # Run over every behavior
            for beh in beh_list:
                # Only continue if the dictionairy contains numbers of events:
                # if len(dict_start_beh[rat][beh]) > 0:
                if dict_start_beh[rat][beh]:
                    # First make a continous time series of behavior events (epocs) and plot
                    BEH_on = dict_start_beh[rat][beh]
                    # BEH_off = dict_end_beh[rat][beh]
                        
                    # # Create a list of these lists for later
                    # EVENTS=[BEH_on,BEH_off]
                    # # Create label names that come with it
                    # LABEL_EVENTS=['Start %s'%beh, 'End %s'%beh]
    
                    # Create a list of these lists for later
                    EVENTS=[BEH_on]
                    # Create label names that come with it
                    LABEL_EVENTS=['Start %s'%beh]
                
                    # Now make snips of the data
                    PRE_TIME = sniptime_pre # number of seconds before event onset
                    POST_TIME = sniptime_post # number of seconds after
                    BASELINE_START = baseline_start
                    BASELINE_END = baseline_end
                    TRANGE = [-PRE_TIME*np.floor(fs), POST_TIME*np.floor(fs)]
                    TRANGE_BASELINE = [BASELINE_START*np.floor(fs), BASELINE_END*np.floor(fs)]
    
                    # time span for peri-event filtering, PRE and POST, in samples
                    for event,name in zip(EVENTS,LABEL_EVENTS):
                        dFF_snips = []
                        dFF_snips_BASELINE=[]
                        zscore_snips = []
                        zscore_snips_BASELINE=[]
                        array_ind = []
                        pre_stim = []
                        post_stim = []
                        pre_BASELINE= []
                        post_BASELINE= []
                        dFF_snips_cor=[]
                        zscore_snips_cor=[]
                    
                        for on in event:
                            #If the event cannot include pre-time seconds before event, exclude it from the data analysis
                            if on > PRE_TIME and on < maxtime:
                                # find first time index after event onset
                                array_ind.append(np.where(time > on)[0][0])
                                # find index corresponding to pre and post stim durations
                                pre_stim.append(array_ind[-1] + TRANGE[0])
                                post_stim.append(array_ind[-1] + TRANGE[1])
                                pre_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[0])
                                post_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[1])
                                BASELINE_dFF=dFF[int(pre_BASELINE[-1]):int(post_BASELINE[-1])]
                                BASELINE_zscore=zscore[int(pre_BASELINE[-1]):int(post_BASELINE[-1])]
                                mean_BASELINE_dFF=np.mean(BASELINE_dFF)
                                mean_BASELINE_zscore=np.mean(BASELINE_zscore)
                                dFF_snip=dFF[int(pre_stim[-1]):int(post_stim[-1])]
                                dFF_snips_cor.append(np.subtract(dFF_snip,mean_BASELINE_dFF))
                                zscore_snip=zscore[int(pre_stim[-1]):int(post_stim[-1])]
                                zscore_snips_cor.append(np.subtract(zscore_snip,mean_BASELINE_dFF))
                        
                        # Based on condition correct or don't correct for baseline
                        if correction == True:
                            dFF_snips=dFF_snips_cor
                            zscore_snips=zscore_snips_cor
                        else:
                            dFF_snips=dFF_snip
                            zscore_snips=zscore_snip
    
                        # Remove the snips that are shorter in size
                        if dFF_snips:
                            max1 = np.max([np.size(x) for x in dFF_snips])
                            dFF_snips=[snip for snip in dFF_snips if np.size(snip)==max1]                    
                            zscore_snips=[snip for snip in zscore_snips if np.size(snip)==max1]                    
                            
                            # Take the mean of the snips
                            mean_dFF_snips = np.mean(dFF_snips, axis=0)
                            std_dFF_snips = np.std(mean_dFF_snips, axis=0)
    
                            mean_zscore_snips = np.mean(zscore_snips, axis=0)
                            std_zscore_snips = np.std(mean_zscore_snips, axis=0)
                        
                            zall = []
                            for snip in dFF_snips: 
                               zb = np.mean(snip)
                               zsd = np.std(snip)
                               zall.append((snip - zb)/zsd)
                               
                            zscore_dFF_snips = np.mean(zall, axis=0)
                
                            # Put the data in the dictionaries
                            dict_tdt_mean['dFF'][rat][name]=mean_dFF_snips
                            dict_tdt_mean['zscore'][rat][name]=mean_zscore_snips
                            dict_tdt_mean['zscore_snip'][rat][name]=zscore_dFF_snips
                
                            peri_time = np.linspace(1, len(mean_dFF_snips), len(mean_dFF_snips))/fs - PRE_TIME
    
                            if graphtitle == None:
                                pass
                            else:
                                # Change directory to output folder
                                if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat):
                                    os.mkdir(directory_graph+directory_TDT_behavior_perrat)
                                if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat+"/zscore"):
                                    os.mkdir(directory_graph+directory_TDT_behavior_perrat+"/zscore")
                                if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips"):
                                    os.mkdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips")
    
                                os.chdir(directory_graph+directory_TDT_behavior_perrat)
                                # Make a peri-event stimulus plot and heatmap
                                sns.set(style="ticks", rc=custom_params)
                                fig1 = plt.figure(figsize=(7,6))
                                ax = fig1.add_subplot(111)
                                for snip in dFF_snips:
                                    p1, = ax.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                                p2, = ax.plot(peri_time, mean_dFF_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                                # Plotting the start line
                                p3 = ax.axvline(x=0, linewidth=2, color=color_zeroline)
                                xx=np.arange(-sniptime_pre,sniptime_post+1,1).tolist()
                                ax.set_xticks(xx)
                                ax.axis('tight')
                                ax.set_xlabel('Seconds',fontsize=16)
                                ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
                                ax.set_title('%s_%s_%s'%(graphtitle,name,rat))
                                ax.legend(handles=[p1, p2], loc="upper left");#bbox_to_anchor=(1.1, 1.05));
                                plt.savefig("dFF %s_%s_%s.png"%(graphtitle,name,rat))
                                plt.close(fig1)
    
                                os.chdir(directory_graph+directory_TDT_behavior_perrat+"/zscore")
                                # Make a peri-event stimulus plot and heatmap
                                sns.set(style="ticks", rc=custom_params)
                                fig2 = plt.figure(figsize=(7,6))
                                ax = fig2.add_subplot(111)
                                for snip in zscore_snips:
                                    p1, = ax.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                                p2, = ax.plot(peri_time, mean_zscore_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                                # Plotting the start line
                                p3 = ax.axvline(x=0, linewidth=2, color=color_zeroline)
                                xx=np.arange(-sniptime_pre,sniptime_post+1,1).tolist()
                                ax.set_xticks(xx)
                                ax.axis('tight')
                                ax.set_xlabel('Seconds',fontsize=16)
                                ax.set_ylabel('z-score',fontsize=16)
                                ax.set_title('%s_%s_%s'%(graphtitle,name,rat))
                                ax.legend(handles=[p1, p2], loc="upper left");#bbox_to_anchor=(1.1, 1.05));
                                plt.savefig("zscore %s_%s_%s.png"%(graphtitle,name,rat))
                                plt.close(fig2)
    
                                os.chdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips")
                                # Make a peri-event stimulus plot and heatmap
                                sns.set(style="ticks", rc=custom_params)
                                fig3 = plt.figure(figsize=(7,6))
                                ax = fig3.add_subplot(111)
                                for snip in zall:
                                    p1, = ax.plot(peri_time, snip, linewidth=.5, color=color_snips, label='Individual Trials')
                                p2, = ax.plot(peri_time, zscore_dFF_snips, linewidth=2, color=color_GCaMP, label='Mean Response')
                                # Plotting the start line
                                p3 = ax.axvline(x=0, linewidth=2, color=color_zeroline)
                                xx=np.arange(-sniptime_pre,sniptime_post+1,1).tolist()
                                ax.set_xticks(xx)
                                ax.axis('tight')
                                ax.set_xlabel('Seconds',fontsize=16)
                                ax.set_ylabel('z-score',fontsize=16)
                                ax.set_title('%s_%s_%s'%(graphtitle,name,rat))
                                ax.legend(handles=[p1, p2], loc="upper left");#bbox_to_anchor=(1.1, 1.05));
                                plt.savefig("dFF %s_%s_%s.png"%(graphtitle,name,rat))
                                plt.close(fig3)
                        
                                # Change directory back
                                os.chdir(directory)
                               
    print("behavior_snipper done")
    return dict_tdt_mean

# Make a definition for the mean behavior snips per rat
def result_snipper(dataframe,diet,test,testsession,virus='GCaMP6',correction=True,
                     beh_list=list_beh_tdt_plus,sniptime_pre=2,sniptime_post=5,exclude_outliers=False,
                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,graphtitle=None):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Deafult = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True
    beh_list : list -> Default = list_beh_tdt
        Add the list with behaviors that need to be analyzed -> Default is list_beh_tdt
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the amount of seconds before the start of the behavior that needs to be analyzed
    sniptime_post : integer -> Default = 5
        Add the amount of seconds after the start of the behavior that needs to be analyzed
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    excluding_behaviors : string -> Default = 'exclude'
        Add "exclude" if you want the delete the behaviors before which another behavior has taken place
    list_relevant_behaviors : list -> Default = list_relevant_behaviors
        If you have "exclude", add a list with the behaviors that cannot happen before the behavior you explore
        Note -> if you don't exclude, just name a random list. This variable will then not be used.
    graphtitle : string
        Add the start name of the figure that is saved. If no figure is needed, type ""

    Returns
    -------
    Dictionary & Figures (Means per test)
    Dictionary with the baseline-corrected mean dFF of snips before and after the behaviors per test. 
    First a mean of dFF-behavior-snips per rat is calculated. Then this mean is used to calculate the overall mean of the coptest.
    Correction is done by taking the average of the dFF signal during the defined "baseline" period, and correcting 
    Figures of the mean dFF signals aligned to the behaviors, plus sem-bands.
    """
    print("Start result_snipper %s%s"%(test,testsession))

    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary_analysis = my_dict_process[d]

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    if excluding_behaviors== "exclude":
        dictionary=behavior_snipper(dataframe,diet,test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
    else:        
        dictionary=behavior_snipper(dataframe,diet,test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='include',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
    

    ymax_dFF=[]
    ymin_dFF=[]
    ymax_zscore=[]
    ymin_zscore=[]
    ymax_zscore_snip=[]
    ymin_zscore_snip=[]
    list_means=[]
    stats=['mean','sem']
    outs=['dFF','zscore','zscore_snip']

    for beh in beh_list:
        temp1='Start %s'%beh
        temp2='End %s'%beh
        list_means.append(temp1)
        list_means.append(temp2)
        
    dict_of_means={}  
    dict_ratmeans={}
    for out in outs:
        dict_of_means[out]={}
        dict_ratmeans[out]={}
        for beh in list_means:
            dict_of_means[out][beh]=[]
            dict_ratmeans[out][beh]={}
            for stat in stats:
                dict_ratmeans[out][beh][stat]=[]
            for rat in dictionary[out].keys():
                if beh in dictionary[out][rat]:
                    dict_of_means[out][beh].append(dictionary[out][rat][beh])

    for out in outs:
        for beh in list_means:
            if dict_of_means['dFF'][beh]:
                max2 = np.max([np.size(x) for x in dict_of_means['dFF'][beh]])
                dict_of_means['dFF'][beh]=[snip for snip in dict_of_means['dFF'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore'][beh]=[snip for snip in dict_of_means['zscore'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore_snip'][beh]=[snip for snip in dict_of_means['zscore_snip'][beh] if np.size(snip)==max2]                    
    
                yarray_dFF = np.array(dict_of_means['dFF'][beh])
                y_dFF = np.mean(yarray_dFF, axis=0)
                yerror_dFF = np.std(yarray_dFF, axis=0)/np.sqrt(len(yarray_dFF))

                yarray_zscore = np.array(dict_of_means['zscore'][beh])
                y_zscore = np.mean(yarray_zscore, axis=0)
                yerror_zscore = np.std(yarray_zscore, axis=0)/np.sqrt(len(yarray_zscore))
 
                yarray_zscore_snip = np.array(dict_of_means['zscore_snip'][beh])
                y_zscore_snip = np.mean(yarray_zscore_snip, axis=0)
                yerror_zscore_snip = np.std(yarray_zscore_snip, axis=0)/np.sqrt(len(yarray_zscore_snip))

                min_ymin_dFF = np.min(y_dFF)
                max_ymax_dFF = np.max(y_dFF)

                min_ymin_zscore = np.min(y_zscore)
                max_ymax_zscore = np.max(y_zscore)

                min_ymin_zscore_snip = np.min(y_zscore_snip)
                max_ymax_zscore_snip = np.max(y_zscore_snip)
                
                min_yerrormin_dFF = np.min(yerror_dFF)
                max_yerrormax_dFF = np.max(yerror_dFF)

                min_yerrormin_zscore = np.min(yerror_zscore)
                max_yerrormax_zscore = np.max(yerror_zscore)

                min_yerrormin_zscore_snip = np.min(yerror_zscore_snip)
                max_yerrormax_zscore_snip = np.max(yerror_zscore_snip)
                
                ymax_dFF.append(max_ymax_dFF+max_yerrormax_dFF)
                ymin_dFF.append(min_ymin_dFF-min_yerrormin_dFF)

                ymax_zscore.append(max_ymax_zscore+max_yerrormax_zscore)
                ymin_zscore.append(min_ymin_zscore-min_yerrormin_zscore)

                ymax_zscore_snip.append(max_ymax_zscore_snip+max_yerrormax_zscore_snip)
                ymin_zscore_snip.append(min_ymin_zscore_snip-min_yerrormin_zscore_snip)
    
        for beh in list_means:
            if dict_of_means['dFF'][beh]:
                max2 = np.max([np.size(x) for x in dict_of_means['dFF'][beh]])
                dict_of_means['dFF'][beh]=[snip for snip in dict_of_means['dFF'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore'][beh]=[snip for snip in dict_of_means['zscore'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore_snip'][beh]=[snip for snip in dict_of_means['zscore_snip'][beh] if np.size(snip)==max2]                    
    
                yarray_dFF = np.array(dict_of_means['dFF'][beh])
                y_dFF = np.mean(yarray_dFF, axis=0)
                yerror_dFF = np.std(yarray_dFF, axis=0)/np.sqrt(len(yarray_dFF))

                yarray_zscore = np.array(dict_of_means['zscore'][beh])
                y_zscore = np.mean(yarray_zscore, axis=0)
                yerror_zscore = np.std(yarray_zscore, axis=0)/np.sqrt(len(yarray_zscore))
 
                yarray_zscore_snip = np.array(dict_of_means['zscore_snip'][beh])
                y_zscore_snip = np.mean(yarray_zscore_snip, axis=0)
                yerror_zscore_snip = np.std(yarray_zscore_snip, axis=0)/np.sqrt(len(yarray_zscore_snip))
    
                length=y_dFF.size
        
                # Put the data in the dictionaries
                dict_ratmeans['dFF'][beh]['mean']=y_dFF
                dict_ratmeans['dFF'][beh]['sem']=yerror_dFF
                dict_ratmeans['zscore'][beh]['mean']=y_zscore
                dict_ratmeans['zscore'][beh]['sem']=yerror_zscore
                dict_ratmeans['zscore_snip'][beh]['mean']=y_zscore_snip
                dict_ratmeans['zscore_snip'][beh]['sem']=yerror_zscore_snip
        
                # Get fs from dictionary of processed data
                for rat,value in dictionary_analysis.items():        
                    fs=dictionary_analysis[rat]['fs']
                    x = np.linspace(1, length, length)/fs - sniptime_pre
        
                # Plot the data
                if graphtitle == None:
                    pass
                else:
                    # Change directory to figure save location
                    if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat):
                        os.mkdir(directory_graph+directory_TDT_behavior_perrat)
                    if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat+"/zscore"):
                        os.mkdir(directory_graph+directory_TDT_behavior_perrat+"/zscore")
                    if not os.path.isdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips"):
                        os.mkdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips")
                    
                    os.chdir(directory_graph+directory_TDT_behavior_perrat)
                    sns.set(style="ticks", rc=custom_params)
                    fig1 = plt.figure(figsize=(7,5))
                    ax = fig1.add_subplot(111)
                    # for ratevent in dict_of_means[beh]:
                    #     p1, = ax7.plot(peri_time, ratevent, linewidth=.5, color=color_snips, label='Individual Trials',zorder=1)
                    ax.plot(x, y_dFF, linewidth=1.5, color=color_GCaMP,zorder=3)
                    ax.fill_between(x, y_dFF-yerror_dFF, y_dFF+yerror_dFF, color='xkcd:silver', alpha=0.4)
                    # Plotting the start line
                    ax.axvline(x=0, linewidth=2, color='#515A5A', )
                    # Plotting appropiate axes
                    xx=np.arange(-sniptime_pre,sniptime_post+1,2).tolist()
                    y_max=np.max(ymax_dFF)
                    y_max= round(y_max / 10) * 10
                    y_min=np.min(ymin_dFF)
                    y_min= round(y_min / 10) * 10
                    yy=np.arange(y_min-10,y_max+15,10).tolist()
                    ax.set_xticks(xx)
                    ax.set_yticks(yy)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
                    ax.set_title("%s_%s_%s%s_%s"%(graphtitle,beh,test,testsession,diet))
                    ax.axhline(y=0, linewidth=0.5, color='#515A5A',zorder=4)
                    plt.savefig("dFF %s_%s_%s%s_%s.png"%(graphtitle,beh,test,testsession,diet))
                    plt.close(fig1)

                    os.chdir(directory_graph+directory_TDT_behavior_perrat+"/zscore")
                    sns.set(style="ticks", rc=custom_params)
                    fig2 = plt.figure(figsize=(7,5))
                    ax = fig2.add_subplot(111)
                    # for ratevent in dict_of_means[beh]:
                    #     p1, = ax7.plot(peri_time, ratevent, linewidth=.5, color=color_snips, label='Individual Trials',zorder=1)
                    ax.plot(x, y_zscore, linewidth=1.5, color=color_GCaMP,zorder=3)
                    ax.fill_between(x, y_zscore-yerror_zscore, y_zscore+yerror_zscore, color='xkcd:silver', alpha=0.4)
                    # Plotting the start line
                    ax.axvline(x=0, linewidth=2, color='#515A5A', )
                    # Plotting appropiate axes
                    xx=np.arange(-sniptime_pre,sniptime_post+1,2).tolist()
                    y_max=np.max(ymax_zscore)
                    y_max= round(y_max / 2) * 2
                    y_min=np.min(ymin_zscore)
                    y_min= round(y_min / 2) * 2
                    yy=np.arange(y_min-1,y_max+1,1).tolist()
                    ax.set_xticks(xx)
                    ax.set_yticks(yy)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel('z-score',fontsize=16)
                    ax.set_title("%s_%s_%s%s_%s"%(graphtitle,beh,test,testsession,diet))
                    ax.axhline(y=0, linewidth=0.5, color='#515A5A',zorder=4)
                    plt.savefig("zscore %s_%s_%s%s_%s.png"%(graphtitle,beh,test,testsession,diet))
                    plt.close(fig2)

                    os.chdir(directory_graph+directory_TDT_behavior_perrat+"/zscoresnips")
                    sns.set(style="ticks", rc=custom_params)
                    fig3 = plt.figure(figsize=(7,5))
                    ax = fig3.add_subplot(111)
                    # for ratevent in dict_of_means[beh]:
                    #     p1, = ax7.plot(peri_time, ratevent, linewidth=.5, color=color_snips, label='Individual Trials',zorder=1)
                    ax.plot(x, y_zscore_snip, linewidth=1.5, color=color_GCaMP,zorder=3)
                    ax.fill_between(x, y_zscore_snip-yerror_zscore_snip, y_zscore_snip+yerror_zscore_snip, color='xkcd:silver', alpha=0.4)
                    # Plotting the start line
                    ax.axvline(x=0, linewidth=2, color='#515A5A', )
                    # Plotting appropiate axes
                    xx=np.arange(-sniptime_pre,sniptime_post+1,2).tolist()
                    y_max=np.max(ymax_zscore_snip)
                    y_max= round(y_max / 2) * 2
                    y_min=np.min(ymin_zscore_snip)
                    y_min= round(y_min / 2) * 2
                    yy=np.arange(y_min-1,y_max+1,1).tolist()
                    ax.set_xticks(xx)
                    ax.set_yticks(yy)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel('z-score',fontsize=16)
                    ax.set_title("%s_%s_%s%s_%s"%(graphtitle,beh,test,testsession,diet))
                    ax.axhline(y=0, linewidth=0.5, color='#515A5A',zorder=4)
                    plt.savefig("zscore_snip %s_%s_%s%s_%s.png"%(graphtitle,beh,test,testsession,diet))
                    plt.close(fig3)

                    # Change back directory 
                    os.chdir(directory)
    
    print("result_snipper done")
    return dict_ratmeans


# Make a definition for the mean behavior snips per rat
def result_snipper_GFP(dataframe,test,testsession,virus='GFP',correction=True,
                     beh_list=list_beh_tdt_plus,sniptime_pre=2,sniptime_post=5,exclude_outliers=False,
                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,graphtitle=None):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string -> Deafult = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True
    beh_list : list -> Default = list_beh_tdt
        Add the list with behaviors that need to be analyzed -> Default is list_beh_tdt
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the amount of seconds before the start of the behavior that needs to be analyzed
    sniptime_post : integer -> Default = 5
        Add the amount of seconds after the start of the behavior that needs to be analyzed
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    excluding_behaviors : string -> Default = 'exclude'
        Add "include" if you don't want the delete the behaviors before which another behavior has taken place
    list_relevant_behaviors : list -> Default = list_relevant_behaviors
        If you have "exclude", add a list with the behaviors that cannot happen before the behavior you explore
        Note -> if you don't exclude, just name a random list. This variable will then not be used.
    graphtitle : string
        Add the start name of the figure that is saved. If no figure is needed, type ""
    
    Returns
    -------
    dict_ratmeans (Means per test) (designed for GFP data)
    Dictionary with the baseline-corrected mean dFF of snips before and after the behaviors per test. 
    First a mean of dFF-behavior-snips per rat is calculated. Then this mean is used to calculate the overall mean of the test.
    Correction is done by taking the average of the dFF signal during the defined "baseline" period, and correcting 
    """
    
    print("Start result_snipper_GFP %s%s"%(test,testsession))

    if excluding_behaviors== "exclude":
        dictionary1=behavior_snipper(dataframe,"CAF",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
        dictionary2=behavior_snipper(dataframe,"CTR",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
        dictionary3=behavior_snipper(dataframe,"HFHS",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='exclude',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)

    else:        
        dictionary1=behavior_snipper(dataframe,"CAF",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='include',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
        dictionary2=behavior_snipper(dataframe,"CTR",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='include',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
        dictionary3=behavior_snipper(dataframe,"HFHS",test,testsession,virus=virus,correction=correction,
                                    excluding_behaviors='include',list_relevant_behaviors=list_relevant_behaviors,
                                 beh_list=beh_list,sniptime_pre=sniptime_pre,sniptime_post=sniptime_post,
                                 exclude_outliers=exclude_outliers)
    
    list_means=[]
    stats=['mean','sem']
    outs=['dFF','zscore','zscore_snip']

    for beh in beh_list:
        temp1='Start %s'%beh
        # temp2='End %s'%beh
        list_means.append(temp1)
        # list_means.append(temp2)
      
    dict_of_means={}  
    dict_ratmeans={}
    for out in outs:
        dict_of_means[out]={}
        dict_ratmeans[out]={}
        for beh in list_means:
            dict_of_means[out][beh]=[]
            dict_ratmeans[out][beh]={}
            for stat in stats:
                dict_ratmeans[out][beh][stat]=[]
            for rat in dictionary1[out].keys():
                if beh in dictionary1[out][rat]:
                    dict_of_means[out][beh].append(dictionary1[out][rat][beh])
            for rat in dictionary2[out].keys():
                if beh in dictionary2[out][rat]:
                    dict_of_means[out][beh].append(dictionary2[out][rat][beh])
            for rat in dictionary3[out].keys():
                if beh in dictionary3[out][rat]:
                    dict_of_means[out][beh].append(dictionary3[out][rat][beh])
        
    for out in outs:
        for beh in list_means:
            if dict_of_means['dFF'][beh]:
                max2 = np.max([np.size(x) for x in dict_of_means['dFF'][beh]])
                dict_of_means['dFF'][beh]=[snip for snip in dict_of_means['dFF'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore'][beh]=[snip for snip in dict_of_means['zscore'][beh] if np.size(snip)==max2]                    
                dict_of_means['zscore_snip'][beh]=[snip for snip in dict_of_means['zscore_snip'][beh] if np.size(snip)==max2]                    
    
                yarray_dFF = np.array(dict_of_means['dFF'][beh])
                y_dFF = np.mean(yarray_dFF, axis=0)
                yerror_dFF = np.std(yarray_dFF, axis=0)/np.sqrt(len(yarray_dFF))

                yarray_zscore = np.array(dict_of_means['zscore'][beh])
                y_zscore = np.mean(yarray_zscore, axis=0)
                yerror_zscore = np.std(yarray_zscore, axis=0)/np.sqrt(len(yarray_zscore))
 
                yarray_zscore_snip = np.array(dict_of_means['zscore_snip'][beh])
                y_zscore_snip = np.mean(yarray_zscore_snip, axis=0)
                yerror_zscore_snip = np.std(yarray_zscore_snip, axis=0)/np.sqrt(len(yarray_zscore_snip))

                # Put the data in the dictionaries
                dict_ratmeans['dFF'][beh]['mean']=y_dFF
                dict_ratmeans['dFF'][beh]['sem']=yerror_dFF
                dict_ratmeans['zscore'][beh]['mean']=y_zscore
                dict_ratmeans['zscore'][beh]['sem']=yerror_zscore
                dict_ratmeans['zscore_snip'][beh]['mean']=y_zscore_snip
                dict_ratmeans['zscore_snip'][beh]['sem']=yerror_zscore_snip
    
    print("result_snipper_GFP done")
    return dict_ratmeans

# Make a definition for comparing GCAMP signals from light snips
def compare_behavior_snipper_plusGFP (dictionary1,dictionary2,dictionary3,dictionary4,condition1,condition2,condition3,condition4,
                                       beh_list=list_beh_tdt_plus,sniptime_pre=2,exclude_outliers=False,graphtitle=None):
    """
    NOTE -> If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dictionary1 : dictionary
        Add 1st dictionary of data you want to add to the figure (e.g. CTR)
    dictionary2 : dictionary
        Add 2nd dictionary of data you want to add to the figure (e.g. HFHS)
    dictionary3 : dictionary
        Add 3rd dictionary of data you want to add to the figure (e.g. CAF)
    dictionary4 : dictionary
        Add 4rd dictionary of data you want to add to the figure (e.g. GFP)
    condition1 : string
        Add the label for dict1
    condition2 : string
        Add the label for dict2
    condition3 : string
        Add the label for dict3
    condition4 : string
        Add the label for dict4
    beh_list : list -> Default is list_beh_tdt
        Add the list with behaviors that need to be analyzed
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the number of seconds you snipped before and after the behavior
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    Figure
    Creates a figure of the mean signals of the dFF signals for the period of determined snips around behaviors 
    and compares in one figure, including GFP signal.
    """
    
    print("Start compare_behavior_snipper_plusGFP")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    for beh in beh_list:
        x='Start %s'%beh
        if x in dictionary1['dFF'].keys():
            if x in dictionary2['dFF'].keys():
                if x in dictionary3['dFF'].keys():
                    if x in dictionary4['dFF'].keys():
                        length1=len(dictionary1['dFF']['Start %s'%beh]['mean'])
                        length2=len(dictionary2['dFF']['Start %s'%beh]['mean'])
                        length3=len(dictionary3['dFF']['Start %s'%beh]['mean'])
                        length4=len(dictionary4['dFF']['Start %s'%beh]['mean'])
                        minlength=min(length1,length2,length3,length4)
                    
                        # Get fs from dictionary of processed data
                        for rat,value in my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'].items():        
                            fs=my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'][rat]['fs']
                            x = np.linspace(1, minlength, minlength)/fs - sniptime_pre
    
                    # Make a peri-event stimulus plot and heatmap
                    if graphtitle == None:
                        pass
                    else:
                        # Change directory to figure save location
                        if not os.path.isdir(directory_graph+directory_TDT_behavior):
                            os.mkdir(directory_graph+directory_TDT_behavior)
                        if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscore"):
                            os.mkdir(directory_graph+directory_TDT_behavior+"/zscore")
                        if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscoresnips"):
                            os.mkdir(directory_graph+directory_TDT_behavior+"/zscoresnips")

                        os.chdir(directory_graph+directory_TDT_behavior)
                        if any(dictionary1['dFF']['Start %s'%beh]['mean']):
                            fig1 = plt.figure(figsize=(8,6))
                            ax = fig1.add_subplot(111)
                            xx =[-2,-1,0,1,2,3,4,5]
                            if beh=='Carry food':
                                yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                            else:
                                yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                            p1, = ax.plot(x, dictionary1['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                            ax.fill_between(x, np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                                  np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                                  color=color_CTR_shadow, alpha=0.4)
                            p2, = ax.plot(x, dictionary2['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                            ax.fill_between(x, np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_HFHS_shadow, alpha=0.4)
                            p3, = ax.plot(x, dictionary3['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                            ax.fill_between(x, np.array( dictionary3['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary3['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_CAF_shadow, alpha=0.4)
                            p4, = ax.plot(x, dictionary4['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_GFP, label=condition4)
                            ax.fill_between(x, np.array( dictionary4['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary4['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary4['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary4['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_GFP_shadow, alpha=0.4)
                            # Plotting the zero line
                            ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                            ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                            ax.set_xticks(xx)
                            ax.set_yticks(yy)
                            ax.set_xlabel('Seconds',fontsize=16)
                            ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
                            # ax.set_title('%s - %s'%(graphtitle, beh))
                            # ax.legend(handles=[p1, p2, p3, p4],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                            plt.savefig("dFF GFP %s %s.png"%(beh,graphtitle))
                            plt.close(fig1)

                        os.chdir(directory_graph+directory_TDT_behavior+"/zscore")
                        if any(dictionary1['zscore']['Start %s'%beh]['mean']):
                            fig2 = plt.figure(figsize=(8,6))
                            ax = fig2.add_subplot(111)
                            xx =[-2,-1,0,1,2,3,4,5]
                            if beh=='Carry food':
                                zz =[-4,-2,0,2,4,6,8]
                            elif beh =='Anogenital sniffing':
                                zz =[-16,-12,-8,-4,0,4,8,12]
                            elif beh =='Approach reward':
                                zz =[-4,-2,0,2,4,6,8,10]
                            elif beh =='Eating':
                                zz =[-5,-4,-3,-2,-1,0,1,2,3,4,5]
                            elif beh =='Ejaculation (received)':
                                zz =[-8,-4,0,4,8,12]
                            elif beh =='Intromission (received)':
                                zz =[-6,-4,-2,0,2,4,6,8]
                            elif beh =='Mount (received)':
                                zz =[-4,-2,0,2,4,6,8]
                            elif beh =='Exploring environment (+rearing)':
                                zz =[-3,-2,-1,0,4,2,3,4]
                            elif beh =='Lordosis':
                                zz =[-4,-2,0,2,4,6,8,10]
                            elif beh =='Paracopulatory':
                                zz =[-4,-2,0,2,4,6]
                            elif beh =='Selfgrooming':
                                zz =[-8,-6,-4,-2,0,2,4]
                            elif beh =='Sniffing reward':
                                zz =[-6,-4,-2,0,2,4,6,8]
                            else:
                                zz =[-3,-2,-1,0,1,2,3]
                            p1, = ax.plot(x, dictionary1['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                            ax.fill_between(x, np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                                  np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                                  color=color_CTR_shadow, alpha=0.4)
                            p2, = ax.plot(x, dictionary2['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                            ax.fill_between(x, np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_HFHS_shadow, alpha=0.4)
                            p3, = ax.plot(x, dictionary3['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                            ax.fill_between(x, np.array( dictionary3['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary3['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_CAF_shadow, alpha=0.4)
                            p4, = ax.plot(x, dictionary4['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_GFP, label=condition4)
                            ax.fill_between(x, np.array( dictionary4['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary4['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary4['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary4['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_GFP_shadow, alpha=0.4)
                            # Plotting the zero line
                            ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                            ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                            ax.set_xticks(xx)
                            ax.set_yticks(zz)
                            ax.set_xlabel('Seconds',fontsize=16)
                            ax.set_ylabel('z-score',fontsize=16)
                            # ax.set_title('%s - %s'%(graphtitle, beh))
                            # ax.legend(handles=[p1, p2, p3, p4],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                            plt.savefig("zscore GFP %s %s.png"%(beh,graphtitle))
                            plt.close(fig2)

                        os.chdir(directory_graph+directory_TDT_behavior+"/zscoresnips")
                        if any(dictionary1['zscore_snip']['Start %s'%beh]['mean']):
                            fig3 = plt.figure(figsize=(8,6))
                            ax = fig3.add_subplot(111)
                            xx =[-2,-1,0,1,2,3,4,5]
                            # if beh=='Carry food':
                            #     yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                            # else:
                            #     yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                            p1, = ax.plot(x, dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                            ax.fill_between(x, np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                                  np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                                  color=color_CTR_shadow, alpha=0.4)
                            p2, = ax.plot(x, dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                            ax.fill_between(x, np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_HFHS_shadow, alpha=0.4)
                            p3, = ax.plot(x, dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                            ax.fill_between(x, np.array( dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_CAF_shadow, alpha=0.4)
                            p4, = ax.plot(x, dictionary4['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_GFP, label=condition4)
                            ax.fill_between(x, np.array( dictionary4['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary4['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       np.array( dictionary4['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary4['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                       color=color_GFP_shadow, alpha=0.4)
                            # Plotting the zero line
                            ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                            ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                            ax.set_xticks(xx)
                            # ax.set_yticks(zz)
                            ax.set_xlabel('Seconds',fontsize=16)
                            ax.set_ylabel('z-score',fontsize=16)
                            # ax.set_title('%s - %s'%(graphtitle, beh))
                            # ax.legend(handles=[p1, p2, p3, p4],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                            plt.savefig("z_snip GFP %s %s.png"%(beh,graphtitle))
                            plt.close(fig3)

    print("compare_behavior_snipper_plusGFP done")
    
# Make a definition for comparing GCAMP signals from light snips
def compare_behavior_snipper (dictionary1,dictionary2,dictionary3,condition1,condition2,condition3,
                                       beh_list=list_beh_tdt_plus,sniptime_pre=2,exclude_outliers=False,graphtitle=None):
    """
    NOTE -> If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dictionary1 : dictionary
        Add 1st dictionary of data you want to add to the figure (e.g. CTR)
    dictionary2 : dictionary
        Add 2nd dictionary of data you want to add to the figure (e.g. HFHS)
    dictionary3 : dictionary
        Add 3rd dictionary of data you want to add to the figure (e.g. CAF)
    condition1 : string
        Add the label for dict1
    condition2 : string
        Add the label for dict2
    condition3 : string
        Add the label for dict3
    beh_list : list -> Default is list_beh_tdt
        Add the list with behaviors that need to be analyzed
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the number of seconds you snipped before and after the behavior
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    Figure
    Creates a figure of the mean signals of the dFF signals for the period of determined snips around behaviors 
    and compares in one figure, excluding GFP signal.
    """
    
    print("Start compare_behavior_snipper")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    for beh in beh_list:
        x='Start %s'%beh
        if x in dictionary1['dFF'].keys():
            if x in dictionary2['dFF'].keys():
                if x in dictionary3['dFF'].keys():
                    length1=len(dictionary1['dFF']['Start %s'%beh]['mean'])
                    length2=len(dictionary2['dFF']['Start %s'%beh]['mean'])
                    length3=len(dictionary3['dFF']['Start %s'%beh]['mean'])
                    minlength=min(length1,length2,length3)
                    
                    # Get fs from dictionary of processed data
                    for rat,value in my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'].items():        
                        fs=my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'][rat]['fs']
                        x = np.linspace(1, minlength, minlength)/fs - sniptime_pre

                # Make a peri-event stimulus plot and heatmap
                if graphtitle == None:
                    pass
                else:
                    # Change directory to figure save location
                    if not os.path.isdir(directory_graph+directory_TDT_behavior):
                        os.mkdir(directory_graph+directory_TDT_behavior)
                    if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscore"):
                        os.mkdir(directory_graph+directory_TDT_behavior+"/zscore")
                    if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscoresnips"):
                        os.mkdir(directory_graph+directory_TDT_behavior+"/zscoresnips")

                    os.chdir(directory_graph+directory_TDT_behavior)
                    if any(dictionary1['dFF']['Start %s'%beh]['mean']):
                        fig1 = plt.figure(figsize=(8,6))
                        ax = fig1.add_subplot(111)
                        xx =[-2,-1,0,1,2,3,4,5]
                        if beh=='Carry food':
                            yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                        else:
                            yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                        p1, = ax.plot(x, dictionary1['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                        ax.fill_between(x, np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                              np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                              color=color_CTR_shadow, alpha=0.4)
                        p2, = ax.plot(x, dictionary2['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                        ax.fill_between(x, np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_HFHS_shadow, alpha=0.4)
                        p3, = ax.plot(x, dictionary3['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                        ax.fill_between(x, np.array( dictionary3['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary3['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_CAF_shadow, alpha=0.4)
                        # Plotting the zero line
                        ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                        ax.set_xticks(xx)
                        ax.set_yticks(yy)
                        ax.set_xlabel('Seconds',fontsize=16)
                        ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
                        # ax.set_title('%s - %s'%(graphtitle, beh))
                        # ax.legend(handles=[p1, p2, p3],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                        plt.savefig("dFF HFHS %s %s.png"%(beh,graphtitle))
                        plt.close(fig1)

                    os.chdir(directory_graph+directory_TDT_behavior+"/zscore")
                    if any(dictionary1['zscore']['Start %s'%beh]['mean']):
                        fig2 = plt.figure(figsize=(8,6))
                        ax = fig2.add_subplot(111)
                        xx =[-2,-1,0,1,2,3,4,5]
                        if beh=='Carry food':
                            zz =[-4,-2,0,2,4,6,8]
                        elif beh =='Approach reward':
                            zz =[-4,-2,0,2,4,6,8,10]
                        elif beh =='Eating':
                            zz =[-5,-4,-3,-2,-1,0,1,2,3,4,5]
                        elif beh =='Ejaculation (received)':
                            zz =[-8,-4,0,4,8,12]
                        elif beh =='Intromission (received)':
                            zz =[-6,-4,-2,0,2,4,6,8]
                        elif beh =='Mount (received)':
                            zz =[-4,-2,0,2,4,6,8]
                        elif beh =='Exploring environment (+rearing)':
                            zz =[-3,-2,-1,0,4,2,3,4]
                        elif beh =='Lordosis':
                            zz =[-4,-2,0,2,4,6,8,10]
                        elif beh =='Paracopulatory':
                            zz =[-4,-2,0,2,4,6]
                        elif beh =='Selfgrooming':
                            zz =[-8,-6,-4,-2,0,2,4]
                        elif beh =='Sniffing reward':
                            zz =[-6,-4,-2,0,2,4,6,8]
                        else:
                            zz =[-3,-2,-1,0,1,2,3]
                        p1, = ax.plot(x, dictionary1['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                        ax.fill_between(x, np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                              np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                              color=color_CTR_shadow, alpha=0.4)
                        p2, = ax.plot(x, dictionary2['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                        ax.fill_between(x, np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_HFHS_shadow, alpha=0.4)
                        p3, = ax.plot(x, dictionary3['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                        ax.fill_between(x, np.array( dictionary3['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary3['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_CAF_shadow, alpha=0.4)
                        # Plotting the zero line
                        ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                        ax.set_xticks(xx)
                        ax.set_yticks(zz)
                        ax.set_xlabel('Seconds',fontsize=16)
                        ax.set_ylabel('z-score',fontsize=16)
                        # ax.set_title('%s - %s'%(graphtitle, beh))
                        # ax.legend(handles=[p1, p2, p3],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                        plt.savefig("zscore HFHS %s %s.png"%(beh,graphtitle))
                        plt.close(fig2)

                    os.chdir(directory_graph+directory_TDT_behavior+"/zscoresnips")
                    if any(dictionary1['zscore_snip']['Start %s'%beh]['mean']):
                        fig3 = plt.figure(figsize=(8,6))
                        ax = fig3.add_subplot(111)
                        xx =[-2,-1,0,1,2,3,4,5]
                        # if beh=='Carry food':
                        #     yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                        # else:
                        #     yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                        p1, = ax.plot(x, dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                        ax.fill_between(x, np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                              np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                              color=color_CTR_shadow, alpha=0.4)
                        p2, = ax.plot(x, dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_HFHS, label=condition2)
                        ax.fill_between(x, np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_HFHS_shadow, alpha=0.4)
                        p3, = ax.plot(x, dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition3)
                        ax.fill_between(x, np.array( dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary3['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                   np.array( dictionary3['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary3['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                   color=color_CAF_shadow, alpha=0.4)
                        # Plotting the zero line
                        ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                        ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                        ax.set_xticks(xx)
                        # ax.set_yticks(zz)
                        ax.set_xlabel('Seconds',fontsize=16)
                        ax.set_ylabel('z-score',fontsize=16)
                        # ax.set_title('%s - %s'%(graphtitle, beh))
                        # ax.legend(handles=[p1, p2, p3],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                        plt.savefig("Z_snip HFHS %s %s.png"%(beh,graphtitle))
                        plt.close(fig3)

    print("compare_behavior_snipper done")
    
# Make a definition for comparing GCAMP signals from light snips
def compare_behavior_snipper_CAF (dictionary1,dictionary2,condition1,condition2,
                                       beh_list=list_beh_tdt_plus,sniptime_pre=2,exclude_outliers=False,graphtitle=None):
    """
    NOTE -> If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dictionary1 : dictionary
        Add 1st dictionary of data you want to add to the figure (e.g. CTR)
    dictionary2 : dictionary
        Add 2nd dictionary of data you want to add to the figure (e.g. HFHS)
    condition1 : string
        Add the label for dict1
    condition2 : string
        Add the label for dict2
    beh_list : list
        Add the list with behaviors that need to be analyzed
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime_pre : integer -> Default = 2
        Add the number of seconds you snipped before and after the behavior
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    Figure
    Creates a figure of the mean signals of the dFF signals for the period of determined snips around behaviors 
    and compares in one figure, excluding HFHS and GFP signal.
    """
    
    print("Start compare_behavior_snipper_CAF")
    

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    for beh in beh_list:
        x='Start %s'%beh
        if x in dictionary1['dFF'].keys():
            if x in dictionary2['dFF'].keys():
                length1=len(dictionary1['dFF']['Start %s'%beh]['mean'])
                length2=len(dictionary2['dFF']['Start %s'%beh]['mean'])
                minlength=min(length1,length2)
                
                # Get fs from dictionary of processed data
                for rat,value in my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'].items():        
                    fs=my_dict_process['dict_dFF_GCaMP6_CAF_PRIMREWARD_1'][rat]['fs']
                    x = np.linspace(1, minlength, minlength)/fs - sniptime_pre

            # Make a peri-event stimulus plot and heatmap
            if graphtitle == None:
                pass
            else:
                # Change directory to figure save location
                if not os.path.isdir(directory_graph+directory_TDT_behavior):
                    os.mkdir(directory_graph+directory_TDT_behavior)
                if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscore"):
                    os.mkdir(directory_graph+directory_TDT_behavior+"/zscore")
                if not os.path.isdir(directory_graph+directory_TDT_behavior+"/zscoresnips"):
                    os.mkdir(directory_graph+directory_TDT_behavior+"/zscoresnips")

                os.chdir(directory_graph+directory_TDT_behavior)
                if any(dictionary1['dFF']['Start %s'%beh]['mean']):
                    fig1 = plt.figure(figsize=(8,6))
                    ax = fig1.add_subplot(111)
                    xx =[-2,-1,0,1,2,3,4,5]
                    if beh=='Carry food':
                        yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                    else:
                        yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                    p1, = ax.plot(x, dictionary1['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                    ax.fill_between(x, np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength]), 
                                          np.array( dictionary1['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['dFF']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                          color=color_CTR_shadow, alpha=0.4)
                    p2, = ax.plot(x, dictionary2['dFF']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition2)
                    ax.fill_between(x, np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                               np.array( dictionary2['dFF']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['dFF']['Start %s'%beh]['sem'][:minlength]), 
                               color=color_CAF_shadow, alpha=0.4)
                    # Plotting the zero line
                    ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                    ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                    ax.set_xticks(xx)
                    ax.set_yticks(yy)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel(r'$\Delta$F/F',fontsize=16)
                    # ax.set_title('%s - %s'%(graphtitle, beh))
                    # ax.legend(handles=[p1, p2],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                    plt.savefig("dFF CAF %s %s.png"%(beh,graphtitle))
                    plt.close(fig1)

                os.chdir(directory_graph+directory_TDT_behavior+"/zscore")
                if any(dictionary1['zscore']['Start %s'%beh]['mean']):
                    fig2 = plt.figure(figsize=(8,6))
                    ax = fig2.add_subplot(111)
                    xx =[-2,-1,0,1,2,3,4,5]
                    if beh=='Carry food':
                        zz =[-4,-2,0,2,4,6,8]
                    elif beh =='Approach reward':
                        zz =[-4,-2,0,2,4,6,8,10]
                    elif beh =='Eating':
                        zz =[-5,-4,-3,-2,-1,0,1,2,3,4,5]
                    elif beh =='Ejaculation (received)':
                        zz =[-8,-4,0,4,8,12]
                    elif beh =='Intromission (received)':
                        zz =[-6,-4,-2,0,2,4,6,8]
                    elif beh =='Mount (received)':
                        zz =[-4,-2,0,2,4,6,8]
                    elif beh =='Exploring environment (+rearing)':
                        zz =[-3,-2,-1,0,4,2,3,4]
                    elif beh =='Lordosis':
                        zz =[-4,-2,0,2,4,6,8,10]
                    elif beh =='Paracopulatory':
                        zz =[-4,-2,0,2,4,6]
                    elif beh =='Selfgrooming':
                        zz =[-8,-6,-4,-2,0,2,4]
                    elif beh =='Sniffing reward':
                        zz =[-6,-4,-2,0,2,4,6,8]
                    else:
                        zz =[-3,-2,-1,0,1,2,3]
                    p1, = ax.plot(x, dictionary1['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                    ax.fill_between(x, np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength]), 
                                          np.array( dictionary1['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                          color=color_CTR_shadow, alpha=0.4)
                    p2, = ax.plot(x, dictionary2['zscore']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition2)
                    ax.fill_between(x, np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                               np.array( dictionary2['zscore']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore']['Start %s'%beh]['sem'][:minlength]), 
                               color=color_CAF_shadow, alpha=0.4)
                    # Plotting the zero line
                    ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                    ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                    ax.set_xticks(xx)
                    ax.set_yticks(zz)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel('z-score',fontsize=16)
                    # ax.set_title('%s - %s'%(graphtitle, beh))
                    # ax.legend(handles=[p1, p2],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                    plt.savefig("zscore CAF %s %s.png"%(beh,graphtitle))
                    plt.close(fig2)

                os.chdir(directory_graph+directory_TDT_behavior+"/zscoresnips")
                if any(dictionary1['zscore_snip']['Start %s'%beh]['mean']):
                    fig3 = plt.figure(figsize=(8,6))
                    ax = fig3.add_subplot(111)
                    xx =[-2,-1,0,1,2,3,4,5]
                    # if beh=='Carry food':
                    #     yy =[-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]
                    # else:
                    #     yy =[-8,-6,-4,-2,0,2,4,6,8,10]
                    p1, = ax.plot(x, dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CTR, label=condition1)
                    ax.fill_between(x, np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                                          np.array( dictionary1['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary1['zscore_snip']['Start %s'%beh]['sem'][:minlength][:minlength]), 
                                          color=color_CTR_shadow, alpha=0.4)
                    p2, = ax.plot(x, dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength], linewidth=1, color=color_CAF, label=condition2)
                    ax.fill_between(x, np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])-np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                               np.array( dictionary2['zscore_snip']['Start %s'%beh]['mean'][:minlength])+np.array( dictionary2['zscore_snip']['Start %s'%beh]['sem'][:minlength]), 
                               color=color_CAF_shadow, alpha=0.4)
                    # Plotting the zero line
                    ax.axvline(x=0, linewidth=2, color=color_zeroline, )
                    ax.axhline(y=0, linewidth=0.5, color=color_zeroline,zorder=4)
                    ax.set_xticks(xx)
                    # ax.set_yticks(zz)
                    ax.set_xlabel('Seconds',fontsize=16)
                    ax.set_ylabel('z-score',fontsize=16)
                    # ax.set_title('%s - %s'%(graphtitle, beh))
                    # ax.legend(handles=[p1, p2],loc="upper left",fontsize=16);#)#, bbox_to_anchor=(1.1, 1.05));
                    plt.savefig("Z_snip CAF %s %s.png"%(beh,graphtitle))
                    plt.close(fig3)

    print("compare_behavior_snipper_CAF done")


# Make a definition for the AUC of behavior snips
def AUC_light_snipper(diet,test,testsession,virus="GCaMP6",exclude_outliers=False,correction=True):
    """
    NOTE ->     If you get an error, check the dictionary used for fs

    Parameters
    ----------
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    virus : string
        Add which virus you want to analyze -> Default = 'GCaMP6'
        e.g. "GCaMP6" or "GFP"
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    correction : boolean
        Add whether or not to correct for baseline
        -> Default is True

    Returns
    -------
    dict_tdt_AUC : dictionary
    Dictionary of the AUC of mean signals of the dFF signals for the period of determined snips around light and door opening
    If you get an error, check the dictionary used for fs
    """
    
    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary_analysis = my_dict_process[d]

    # Make empty dictionaries
    dict_tdt_AUC={}
    list_AUC=['AUC_pre','AUC_light','AUC_post']
    for i in list_AUC:
        dict_tdt_AUC[i]={}

    # Get dFF,time and fs from dictionary of processed data
    for rat,value in dictionary_analysis.items():        
        if rat not in list_signal_artifact_excl:
            print("Start AUC_light_snipper %s"%(rat))
            if exclude_outliers == False:
                dFF=dictionary_analysis[rat]['dFF']
                time=dictionary_analysis[rat]['time']
            else: 
                dFF=dictionary_analysis[rat]['dFF_cor']
                time=dictionary_analysis[rat]['time_cor']
            
            fs=dictionary_analysis[rat]['fs']
            LIGHT=dictionary_analysis[rat]['LIGHT_on']
    
            # Make an empty dictionary
            dict_tdt_AUC[i][rat]={}
    
            # Run over every lights on
            if LIGHT > 100:
                # First make a continous time series of behavior events (epocs) and plot
                LIGHT_MARK = LIGHT
    
                # Now make snips of the data
                TRANGE_pre = [-10*np.floor(fs), np.floor(fs)]
                TRANGE_light = [np.floor(fs),np.floor(fs)*10]
                TRANGE_post = [np.floor(fs)*10, 20*np.floor(fs)]
                TRANGE_BASELINE = [-10*np.floor(fs), np.floor(fs)]
    
                # time span for peri-event filtering, PRE and POST, in samples
                array_ind = []
                pre_stim = []
                light_stim = []
                door_stim = []
                end_stim = []
                pre_BASELINE= []
                post_BASELINE= []
                dFF_snips_pre_cor = []
                dFF_snips_light_cor = []
                dFF_snips_post_cor = []
                
                # find first time index after event onset
                array_ind.append(np.where(time > LIGHT_MARK)[0][0])
                # find index corresponding to pre and post stim durations
                pre_stim.append(array_ind[-1] + TRANGE_pre[0])
                light_stim.append(array_ind[-1])
                door_stim.append(array_ind[-1] + TRANGE_post[0])
                end_stim.append(array_ind[-1] + TRANGE_post[-1])
    
                pre_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[0])
                post_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[-1])
                BASELINE=dFF[int(pre_BASELINE[-1]):int(post_BASELINE[-1])]
                mean_BASELINE=np.mean(BASELINE)
    
                dFF_snips_pre1=(dFF[int(pre_stim[-1]):int(light_stim[-1])])
                dFF_snips_light1=(dFF[int(light_stim[-1]):int(door_stim[-1])])
                dFF_snips_post1=(dFF[int(door_stim[-1]):int(end_stim[-1])])
                
                dFF_snips_pre_cor.append(np.subtract(dFF_snips_pre1,mean_BASELINE))
                dFF_snips_light_cor.append(np.subtract(dFF_snips_light1,mean_BASELINE))
                dFF_snips_post_cor.append(np.subtract(dFF_snips_post1,mean_BASELINE))
                
                if correction==True:
                    dFF_snips_pre=dFF_snips_pre_cor
                    dFF_snips_light=dFF_snips_light_cor
                    dFF_snips_post=dFF_snips_post_cor
                else:
                    dFF_snips_pre=dFF_snips_pre1
                    dFF_snips_light=dFF_snips_light1
                    dFF_snips_post=dFF_snips_post1
                    
                # Calculate AUC
                AUC_dFF_snips_pre = trapz(dFF_snips_pre)                    
                AUC_dFF_snips_light = trapz(dFF_snips_light)                    
                AUC_dFF_snips_post = trapz(dFF_snips_post)                    
               
                # Put the data in the dictionaries
                dict_tdt_AUC['AUC_pre'][rat]=AUC_dFF_snips_pre
                dict_tdt_AUC['AUC_light'][rat]=AUC_dFF_snips_light
                dict_tdt_AUC['AUC_post'][rat]=AUC_dFF_snips_post
                    
    print("AUC_light_snipper done")
    return dict_tdt_AUC

# Make a definition for the mean behavior snips per rat
def AUC_result_light_snipper(test,testsession,exclude_outliers=False,graphtitle=None):
    """
    Parameters
    ----------
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None

    Returns
    -------
    Graph
    Graphs of the mean signals of the AUC for the period of determined snips around light and door 
    per rat and combines rats in one figure
    """
    print("Start AUC_result_light_snipper")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    if exclude_outliers==False:
        dict_AUC_CTR="AUC_CTR_"+str(test)+"_"+str(testsession)  
        dict_AUC_HFHS="AUC_HFHS_"+str(test)+"_"+str(testsession)  
        dict_AUC_CAF="AUC_CAF_"+str(test)+"_"+str(testsession)  
    else:
        dict_AUC_CTR="AUC_CTR_COR_"+str(test)+"_"+str(testsession)  
        dict_AUC_HFHS="AUC_HFHS_COR_"+str(test)+"_"+str(testsession)  
        dict_AUC_CAF="AUC_CAF_COR_"+str(test)+"_"+str(testsession)  

    dictionary_CTR= eval(dict_AUC_CTR)
    dictionary_CAF= eval(dict_AUC_CAF)
    dictionary_HFHS= eval(dict_AUC_HFHS)
    
    list_diet=['CTR','HFHS','CAF']
    list_AUC=['AUC_pre','AUC_light','AUC_post']

    dict_AUC_means={}  
    dict_AUC_ratmeans={}
    for d in list_diet:
        dict_AUC_means[d]={}  
        dict_AUC_ratmeans[d]={}

        for moment in list_AUC:
            dict_AUC_means[d][moment]=[]
            dict_AUC_ratmeans[d][moment]=[]
            
    # for m,ids in dictionary_CTR.items():
    #     for rat, value in ids.items():
    for v in dictionary_CTR['AUC_pre'].values():
        dict_AUC_means['CTR']['AUC_pre'].append(v)
    for v in dictionary_HFHS['AUC_pre'].values():
        dict_AUC_means['HFHS']['AUC_pre'].append(v)
    for v in dictionary_CAF['AUC_pre'].values():
        dict_AUC_means['CAF']['AUC_pre'].append(v)

    for v in dictionary_CTR['AUC_light'].values():
        dict_AUC_means['CTR']['AUC_light'].append(v)
    for v in dictionary_HFHS['AUC_light'].values():
        dict_AUC_means['HFHS']['AUC_light'].append(v)
    for v in dictionary_CAF['AUC_light'].values():
        dict_AUC_means['CAF']['AUC_light'].append(v)

    for v in dictionary_CTR['AUC_post'].values():
        dict_AUC_means['CTR']['AUC_post'].append(v)
    for v in dictionary_HFHS['AUC_post'].values():
        dict_AUC_means['HFHS']['AUC_post'].append(v)
    for v in dictionary_CAF['AUC_post'].values():
        dict_AUC_means['CAF']['AUC_post'].append(v)


    dict_AUC_ratmeans['CTR']['AUC_pre']=int(np.mean(dict_AUC_means['CTR']['AUC_pre'], axis=0))
    dict_AUC_ratmeans['CTR']['AUC_light']=int(np.mean(dict_AUC_means['CTR']['AUC_light'], axis=0))
    dict_AUC_ratmeans['CTR']['AUC_post']=int(np.mean(dict_AUC_means['CTR']['AUC_post'], axis=0))

    dict_AUC_ratmeans['HFHS']['AUC_pre']=int(np.mean(dict_AUC_means['HFHS']['AUC_pre'], axis=0))
    dict_AUC_ratmeans['HFHS']['AUC_light']=int(np.mean(dict_AUC_means['HFHS']['AUC_light'], axis=0))
    dict_AUC_ratmeans['HFHS']['AUC_post']=int(np.mean(dict_AUC_means['HFHS']['AUC_post'], axis=0))

    dict_AUC_ratmeans['CAF']['AUC_pre']=int(np.mean(dict_AUC_means['CAF']['AUC_pre'], axis=0))
    dict_AUC_ratmeans['CAF']['AUC_light']=int(np.mean(dict_AUC_means['CAF']['AUC_light'], axis=0))
    dict_AUC_ratmeans['CAF']['AUC_post']=int(np.mean(dict_AUC_means['CAF']['AUC_post'], axis=0))

    # sem=int(np.std(dict_AUC_means['CTR']['AUC_pre'], axis=0))
    # Make a barplot
    if graphtitle == None:
        pass
    else:
        if not os.path.isdir(directory_graph+directory_TDT_lightdoor_AUC):
            os.mkdir(directory_graph+directory_TDT_lightdoor_AUC)
        os.chdir(directory_graph+directory_TDT_lightdoor_AUC)
        
        # Plot the data in bar charts with individual datapoints
        # Set position of bar on X axis - MAKE SURE IT MATCHES YOUR NUMBER OF GROUPS
        # set width of bar
        # sns.set(style="ticks", rc=custom_params)
        barWidth = 0.8
        x1 = ['Pre']
        x2 = ['Light']
        x3 = ['Post']
        yy =[-100,-50,0,50,100,150,200]
            
        x_scatter1=len(dict_AUC_means['CTR']['AUC_pre'])
        x_scatter2=len(dict_AUC_means['HFHS']['AUC_pre'])
        x_scatter3=len(dict_AUC_means['CAF']['AUC_pre'])
        
        fig, axs = plt.subplots(1,3, figsize=(6,4), sharex=True, sharey=True)#, constrained_layout = True)

        axs[0].bar(x1, dict_AUC_ratmeans['CTR']['AUC_pre'], color=color_AUC_CTR_pre, width=barWidth, edgecolor='white', label='Pre',zorder=2)
        axs[0].scatter(x_scatter1*x1, dict_AUC_means['CTR']['AUC_pre'], color=color_AUC_CTR_pre_scatter, alpha=.9,zorder=3)
        axs[0].bar(x2, dict_AUC_ratmeans['CTR']['AUC_light'], color=color_AUC_CTR_light, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[0].scatter(x_scatter1*x2, dict_AUC_means['CTR']['AUC_light'], color=color_AUC_CTR_light_scatter, alpha=.9,zorder=3)
        axs[0].bar(x3, dict_AUC_ratmeans['CTR']['AUC_post'], color=color_AUC_CTR_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[0].scatter(x_scatter1*x3, dict_AUC_means['CTR']['AUC_post'],color=color_AUC_CTR_post_scatter,  alpha=.9,zorder=3)
        axs[0].set_title('CTR')
        axs[0].set_ylabel('AUC')
        # axs[0].set_yticks(yy)

        # Plotting the zero line
        axs[0].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)

        axs[1].bar(x1, dict_AUC_ratmeans['HFHS']['AUC_pre'], color=color_AUC_HFHS_pre , width=barWidth, edgecolor='white', label='Pre',zorder=2)
        axs[1].scatter(x_scatter2*x1, dict_AUC_means['HFHS']['AUC_pre'],color=color_AUC_HFHS_pre_scatter, alpha=.9,zorder=3)
        axs[1].bar(x2, dict_AUC_ratmeans['HFHS']['AUC_light'], color=color_AUC_HFHS_light, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[1].scatter(x_scatter2*x2, dict_AUC_means['HFHS']['AUC_light'], color=color_AUC_HFHS_light_scatter,alpha=.9,zorder=3)
        axs[1].bar(x3, dict_AUC_ratmeans['HFHS']['AUC_post'], color=color_AUC_HFHS_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[1].scatter(x_scatter2*x3, dict_AUC_means['HFHS']['AUC_post'], color=color_AUC_HFHS_post_scatter,alpha=.9,zorder=3)
        axs[1].set_title('HFHS')
        # axs[1].set_yticks(yy)
        axs[1].spines['left'].set_visible(False)                
        axs[1].tick_params(left=False)              
        axs[1].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)
       
        axs[2].bar(x1, dict_AUC_ratmeans['CAF']['AUC_pre'], color=color_AUC_CAF_pre, width=barWidth, edgecolor='white', label='Pre',zorder=2)
        axs[2].scatter(x_scatter3*x1, dict_AUC_means['CAF']['AUC_pre'], color=color_AUC_CAF_pre_scatter, alpha=.9,zorder=3)
        axs[2].bar(x2, dict_AUC_ratmeans['CAF']['AUC_light'], color=color_AUC_CAF_light, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[2].scatter(x_scatter3*x2, dict_AUC_means['CAF']['AUC_light'], color=color_AUC_CAF_light_scatter, alpha=.9,zorder=3)
        axs[2].bar(x3, dict_AUC_ratmeans['CAF']['AUC_post'], color=color_AUC_CAF_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
        axs[2].scatter(x_scatter3*x3, dict_AUC_means['CAF']['AUC_post'],color=color_AUC_CAF_post_scatter,  alpha=.9,zorder=3)
        axs[2].set_title('CAF')
        # axs[2].set_yticks(yy)
        axs[2].spines['left'].set_visible(False)                
        axs[2].tick_params(left=False)              
        axs[2].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)

        # fig.suptitle('%s%s'%(test,testsession))

        plt.savefig('%s lightdoor %s%s.png'%(graphtitle,test,testsession))
        plt.close(fig)
        # Change directory back
        os.chdir(directory)

    return dict_AUC_ratmeans
    print("AUC_result_light_snipper done")

# Make a definition for the AUC of behavior snips
def AUC_behavior_snipper(dataframe,diet,test,testsession,virus='GCaMP6',correction=True,
                          beh_list=list_beh_tdt_plus,excluding_behaviors='exclude',exclude_outliers=False,
                         list_relevant_behaviors=list_relevant_behaviors,sniptime=2):
    """
    NOTE ->     If you get an error, check the dictionary used for fs

    Parameters
    ----------
    dataframe : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_P,data_R
    diet : string
        Add the diet you want to analyze
        e.g. "CAF", "CTR, "HFHS""
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    beh_list : list -> Default = list_beh_tdt
        Add the list with behaviors that need to be analyzed -> Default is list_beh_tdt
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    virus : string
        Add which virus you want to analyze -> Default = 'GCaMP6'
        e.g. "GCaMP6" or "GFP"
    correction : boolean -> Default is True
        Add whether or not to correct for baseline
    excluding_behaviors : string -> Default = 'exclude'
        Add "exclude" if you want the delete the behaviors before which another behavior has taken place
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    list_relevant_behaviors : list -> Default = list_relevant_behaviors
        If you have "exclude", add a list with the behaviors that cannot happen before the behavior you explore
        Note -> if you don't exclude, just name a random list. This variable will then not be used.
    sniptime : integer
        Add the number of seconds you want the snip to start before and after the event-> Default = 2
    Returns
    -------
    dict_tdt_AUC
    Dictionary of the AUC of mean signals of the dFF signals for the period of determined snips around behaviors
    """
    
    d="dict_dFF_"+str(virus)+"_"+str(diet)+"_"+str(test)+"_"+str(testsession)      
    for key,dicts in my_dict_process.items():
        dictionary_analysis = my_dict_process[d]

    if excluding_behaviors== "exclude":
        dict_start_beh=make_dict_start_behavior_excl(dataframe,diet,test,testsession,virus=virus)
        dict_end_beh=make_dict_end_behavior_excl(dataframe,diet,test,testsession,virus=virus)
    else:        
        dict_start_beh=make_dict_start_behavior(dataframe,diet,test,testsession,virus=virus)
        dict_end_beh=make_dict_end_behavior(dataframe,diet,test,testsession,virus=virus)

    # Make empty dictionaries
    dict_tdt_AUC={}
    list_AUC=['AUC_pre','AUC_post']
    for i in list_AUC:
        dict_tdt_AUC[i]={}
        for rat,value in dictionary_analysis.items():  
            for beh in beh_list:
                # Only continue if the dictionairy contains numbers of events:
                if dict_start_beh[rat][beh]:
                    dict_tdt_AUC[i][beh]={}
                    dict_tdt_AUC[i][beh][rat]=[]
    

    # Get dFF,time and fs from dictionary of processed data
    for rat,value in dictionary_analysis.items():  
        if rat not in list_signal_artifact_excl:
            print("Start AUC_behavior_snipper %s"%(rat))
            if exclude_outliers == False:
                dFF=dictionary_analysis[rat]['dFF']
                time=dictionary_analysis[rat]['time']
            else: 
                dFF=dictionary_analysis[rat]['dFF_cor']
                time=np.array(dictionary_analysis[rat]['time_cor'])
    
            fs=dictionary_analysis[rat]['fs']
            maxtime=np.max(time[-1])
            
            for beh in beh_list:
                # Only continue if the dictionairy contains numbers of events:
                if dict_start_beh[rat][beh]:
                    # First make a continous time series of behavior events (epocs) and plot
                    BEH_on = dict_start_beh[rat][beh]
                    
                    # Now make snips of the data
                    BASELINE_START = baseline_start
                    BASELINE_END = baseline_end
                    TRANGE_pre = [-sniptime*np.floor(fs), np.floor(fs)]
                    TRANGE_post = [np.floor(fs), np.floor(fs)*sniptime]
                    TRANGE_BASELINE = [BASELINE_START*np.floor(fs), BASELINE_END*np.floor(fs)]
    
                    # time span for peri-event filtering, PRE and POST, in samples
                    array_ind = []
                    pre_stim = []
                    start_stim = []
                    end_stim = []
                    start_BASELINE= []
                    end_BASELINE= []
                    dFF_snips_pre_cor=[]
                    dFF_snips_post_cor=[]
                    
                    AUC_dFF_snips_pre=[]
                    AUC_dFF_snips_post=[]
                
                    #If the event cannot include pre-time seconds before event, exclude it from the data analysis
                    for on in BEH_on:
                        if on < maxtime:
                            # find first time index after event onset
                            array_ind.append(np.where(time > on)[0][0])
                            # find index corresponding to pre and post stim durations
                            pre_stim.append(array_ind[-1] + TRANGE_pre[0])
                            start_stim.append(array_ind[-1])
                            end_stim.append(array_ind[-1] + TRANGE_post[-1])
                            
                            start_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[0])
                            end_BASELINE.append(array_ind[-1] + TRANGE_BASELINE[-1])
                            
                            BASELINE=dFF[int(start_BASELINE[-1]):int(end_BASELINE[-1])]
                            mean_BASELINE=np.mean(BASELINE)
                            
                            dFF_snips_pre1=(dFF[int(pre_stim[-1]):int(start_stim[-1])])
                            dFF_snips_post1=(dFF[int(start_stim[-1]):int(end_stim[-1])])
                            
                            dFF_snips_pre_cor.append(np.subtract(dFF_snips_pre1,mean_BASELINE))
                            dFF_snips_post_cor.append(np.subtract(dFF_snips_post1,mean_BASELINE))
            
                    if correction==True:
                        dFF_snips_pre=dFF_snips_pre_cor
                        dFF_snips_post=dFF_snips_post_cor
                    else:
                        dFF_snips_pre=dFF_snips_pre1
                        dFF_snips_post=dFF_snips_post1
    
                    # Remove the snips that are shorter in size
                    if dFF_snips_pre:
                        max1 = np.max([np.size(x) for x in dFF_snips_pre])
                        max2 = np.max([np.size(x) for x in dFF_snips_post])
                        
                        dFF_snips_pre=[snip for snip in dFF_snips_pre if (np.size(snip)==max1 and np.size(snip)==max2)]                    
                        dFF_snips_post=[snip for snip in dFF_snips_post if (np.size(snip)==max1 and np.size(snip)==max2)]                    
            
                        # Calculate AUC
                        AUC_pre=[trapz(snip) for snip in dFF_snips_pre]             
                        AUC_post=[trapz(snip) for snip in dFF_snips_post]             
        
                        AUC_dFF_snips_pre.append(AUC_pre)
                        AUC_dFF_snips_post.append(AUC_post)
                        
                        mean_pre=np.nanmean(AUC_dFF_snips_pre, axis=1)
                        mean_post=np.nanmean(AUC_dFF_snips_post, axis=1)
        
                        # Put the data in the dictionaries
                        dict_tdt_AUC['AUC_pre'][beh][rat]=mean_pre
                        dict_tdt_AUC['AUC_post'][beh][rat]=mean_post
                    
    print("AUC_behavior_snipper done")
    return dict_tdt_AUC


#######################################################################################################
#######################################################################################################
#####################  RESULTS  #######################################################################
#######################################################################################################
#######################################################################################################

###################################################################################################
################## GRAPHS WITHOUT OUTLIERS - ALL BEHAVIORS INCLUDED - IN RESULTS COR FOLDER ########################################################
###################################################################################################

###################################################################################################
################## LIGHTDOOR ########################################################
###################################################################################################

# Calculate the means of door and light -> some parameter could be changed, 
# e.g. output could be set to output='zscore'
RESULTS_COR_LIGHT_CAF_PRIM_1=result_lightdoor_snipper("CAF","PRIMREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_PRIM_1=result_lightdoor_snipper("HFHS","PRIMREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_PRIM_1=result_lightdoor_snipper("CTR","PRIMREWARD",1,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_PRIM_3=result_lightdoor_snipper("CAF","PRIMREWARD",3,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_PRIM_3=result_lightdoor_snipper("HFHS","PRIMREWARD",3,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_PRIM_3=result_lightdoor_snipper("CTR","PRIMREWARD",3,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_PRIM_5=result_lightdoor_snipper("CAF","PRIMREWARD",5,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_PRIM_5=result_lightdoor_snipper("HFHS","PRIMREWARD",5,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_PRIM_5=result_lightdoor_snipper("CTR","PRIMREWARD",5,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_SEC_1=result_lightdoor_snipper("CAF","SECREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_SEC_1=result_lightdoor_snipper("HFHS","SECREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_SEC_1=result_lightdoor_snipper("CTR","SECREWARD",1,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_SEC_2=result_lightdoor_snipper("CAF","SECREWARD",2,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_SEC_2=result_lightdoor_snipper("HFHS","SECREWARD",2,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_SEC_2=result_lightdoor_snipper("CTR","SECREWARD",2,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_SEC_3=result_lightdoor_snipper("CAF","SECREWARD",3,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_SEC_3=result_lightdoor_snipper("HFHS","SECREWARD",3,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_SEC_3=result_lightdoor_snipper("CTR","SECREWARD",3,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_PRIMREV_1=result_lightdoor_snipper("CAF","PRIMREWARD_rev",1,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_PRIMREV_1=result_lightdoor_snipper("HFHS","PRIMREWARD_rev",1,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_PRIMREV_1=result_lightdoor_snipper("CTR","PRIMREWARD_rev",1,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_PRIMREV_3=result_lightdoor_snipper("CAF","PRIMREWARD_rev",3,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_PRIMREV_3=result_lightdoor_snipper("HFHS","PRIMREWARD_rev",3,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_PRIMREV_3=result_lightdoor_snipper("CTR","PRIMREWARD_rev",3,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_SECREV_1=result_lightdoor_snipper("CAF","SECREWARD_rev",1,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_SECREV_1=result_lightdoor_snipper("HFHS","SECREWARD_rev",1,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_SECREV_1=result_lightdoor_snipper("CTR","SECREWARD_rev",1,exclude_outliers=True)

RESULTS_COR_LIGHT_CAF_DISREWARD_1=result_lightdoor_snipper("CAF","DISREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_HFHS_DISREWARD_1=result_lightdoor_snipper("HFHS","DISREWARD",1,exclude_outliers=True)
RESULTS_COR_LIGHT_CTR_DISREWARD_1=result_lightdoor_snipper("CTR","DISREWARD",1,exclude_outliers=True)

# # Make graphs for the comparisons -> some parameter could be changed, e.g. output could be set to output='zscore'
LIGHT_COR_PRIMREW1= compare_light_snipper(RESULTS_COR_LIGHT_CTR_PRIM_1,RESULTS_COR_LIGHT_HFHS_PRIM_1,RESULTS_COR_LIGHT_CAF_PRIM_1,"CTR","HFHS","CAF",graphtitle="PRIMREW1_cor",exclude_outliers=True)
LIGHT_COR_PRIMREW3= compare_light_snipper(RESULTS_COR_LIGHT_CTR_PRIM_3,RESULTS_COR_LIGHT_HFHS_PRIM_3,RESULTS_COR_LIGHT_CAF_PRIM_3,"CTR","HFHS","CAF",graphtitle="PRIMREW3_cor",exclude_outliers=True)
LIGHT_COR_PRIMREW5= compare_light_snipper(RESULTS_COR_LIGHT_CTR_PRIM_5,RESULTS_COR_LIGHT_HFHS_PRIM_5,RESULTS_COR_LIGHT_CAF_PRIM_5,"CTR","HFHS","CAF",graphtitle="PRIMREW5_cor",exclude_outliers=True)

LIGHT_COR_SECREW1= compare_light_snipper(RESULTS_COR_LIGHT_CTR_SEC_1,RESULTS_COR_LIGHT_HFHS_SEC_1,RESULTS_COR_LIGHT_CAF_SEC_1,"CTR","HFHS","CAF",graphtitle="SECREW1_cor",exclude_outliers=True)
LIGHT_COR_SECREW2= compare_light_snipper(RESULTS_COR_LIGHT_CTR_SEC_2,RESULTS_COR_LIGHT_HFHS_SEC_2,RESULTS_COR_LIGHT_CAF_SEC_2,"CTR","HFHS","CAF",graphtitle="SECREW2_cor",exclude_outliers=True)
LIGHT_COR_SECREW3= compare_light_snipper(RESULTS_COR_LIGHT_CTR_SEC_3,RESULTS_COR_LIGHT_HFHS_SEC_3,RESULTS_COR_LIGHT_CAF_SEC_3,"CTR","HFHS","CAF",graphtitle="SECREW3_cor",exclude_outliers=True)

LIGHT_COR_PRIMREWREV1= compare_light_snipper(RESULTS_COR_LIGHT_CTR_PRIMREV_1,RESULTS_COR_LIGHT_HFHS_PRIMREV_1,RESULTS_COR_LIGHT_CAF_PRIMREV_1,"CTR","HFHS","CAF",graphtitle="revPRIMREW1_cor",exclude_outliers=True)
LIGHT_COR_PRIMREWREV3= compare_light_snipper(RESULTS_COR_LIGHT_CTR_PRIMREV_3,RESULTS_COR_LIGHT_HFHS_PRIMREV_3,RESULTS_COR_LIGHT_CAF_PRIMREV_3,"CTR","HFHS","CAF",graphtitle="revPRIMREW3_cor",exclude_outliers=True)
LIGHT_COR_SECREWREV1= compare_light_snipper(RESULTS_COR_LIGHT_CTR_SECREV_1,RESULTS_COR_LIGHT_HFHS_SECREV_1,RESULTS_COR_LIGHT_CAF_SECREV_1,"CTR","HFHS","CAF",graphtitle="revSECREW1_cor",exclude_outliers=True)

LIGHT_COR_DISREW1= compare_light_snipper(RESULTS_COR_LIGHT_CTR_DISREWARD_1,RESULTS_COR_LIGHT_HFHS_DISREWARD_1,RESULTS_COR_LIGHT_CAF_DISREWARD_1,"CTR","HFHS","CAF",graphtitle="STDCHOW_cor",exclude_outliers=True)

# For only CTR and CAF
LIGHT_COR_PRIMREW1= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_PRIM_1,RESULTS_COR_LIGHT_CAF_PRIM_1,"CTR","CAF",graphtitle="PRIMREW1_cor",exclude_outliers=True)
LIGHT_COR_PRIMREW3= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_PRIM_3,RESULTS_COR_LIGHT_CAF_PRIM_3,"CTR","CAF",graphtitle="PRIMREW3_cor",exclude_outliers=True)
LIGHT_COR_PRIMREW5= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_PRIM_5,RESULTS_COR_LIGHT_CAF_PRIM_5,"CTR","CAF",graphtitle="PRIMREW5_cor",exclude_outliers=True)

LIGHT_COR_SECREW1= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_SEC_1,RESULTS_COR_LIGHT_CAF_SEC_1,"CTR","CAF",graphtitle="SECREW1_cor",exclude_outliers=True)
LIGHT_COR_SECREW2= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_SEC_2,RESULTS_COR_LIGHT_CAF_SEC_2,"CTR","CAF",graphtitle="SECREW2_cor",exclude_outliers=True)
LIGHT_COR_SECREW3= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_SEC_3,RESULTS_COR_LIGHT_CAF_SEC_3,"CTR","CAF",graphtitle="SECREW3_cor",exclude_outliers=True)

LIGHT_COR_PRIMREWREV1= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_PRIMREV_1,RESULTS_COR_LIGHT_CAF_PRIMREV_1,"CTR","CAF",graphtitle="revPRIMREW1_cor",exclude_outliers=True)
LIGHT_COR_PRIMREWREV3= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_PRIMREV_3,RESULTS_COR_LIGHT_CAF_PRIMREV_3,"CTR","CAF",graphtitle="revPRIMREW3_cor",exclude_outliers=True)
LIGHT_COR_SECREWREV1= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_SECREV_1,RESULTS_COR_LIGHT_CAF_SECREV_1,"CTR","CAF",graphtitle="revSECREW1_cor",exclude_outliers=True)

LIGHT_COR_DISREW1= compare_light_snipper_2cond(RESULTS_COR_LIGHT_CTR_DISREWARD_1,RESULTS_COR_LIGHT_CAF_DISREWARD_1,"CTR","CAF",graphtitle="STDCHOW_cor",exclude_outliers=True)
#############
# # Make graphs to compare sex and food -> some parameter could be changed, e.g. output could be set to output='zscore'
# LIGHT_COR_PRIMSEC1_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison1_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC1_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_1,RESULTS_LIGHT_CAF_SEC_1,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison1_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC1_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_HFHS_SEC_1,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison1_cor",exclude_outliers=True)

# LIGHT_COR_PRIMSEC3_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison3_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC3_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_5,RESULTS_LIGHT_CAF_SEC_3,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison3_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC3_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_5,RESULTS_LIGHT_HFHS_SEC_3,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison3_cor",exclude_outliers=True)

# # Make graphs to compare sex and food -> some parameter could be changed, e.g. output could be set to output='zscore'
# LIGHT_COR_PRIMSEC1_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_3,RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison1_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC1_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_1,RESULTS_LIGHT_CAF_SEC_1,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison1_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC1_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_HFHS_SEC_1,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison1_cor",exclude_outliers=True)

# LIGHT_COR_PRIMSEC3_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison3_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC3_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_5,RESULTS_LIGHT_CAF_SEC_3,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison3_cor",exclude_outliers=True)
# LIGHT_COR_PRIMSEC3_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_5,RESULTS_LIGHT_HFHS_SEC_3,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison3_cor",exclude_outliers=True)

##################################
# Calculate AUC Light-door
AUC_CAF_COR_PRIMREWARD_1=AUC_light_snipper("CAF","PRIMREWARD",1,exclude_outliers=True)
AUC_CTR_COR_PRIMREWARD_1=AUC_light_snipper("CTR","PRIMREWARD",1,exclude_outliers=True)
AUC_HFHS_COR_PRIMREWARD_1=AUC_light_snipper("HFHS","PRIMREWARD",1,exclude_outliers=True)

AUC_CAF_COR_PRIMREWARD_3=AUC_light_snipper("CAF","PRIMREWARD",3,exclude_outliers=True)
AUC_CTR_COR_PRIMREWARD_3=AUC_light_snipper("CTR","PRIMREWARD",3,exclude_outliers=True)
AUC_HFHS_COR_PRIMREWARD_3=AUC_light_snipper("HFHS","PRIMREWARD",3,exclude_outliers=True)

AUC_CAF_COR_PRIMREWARD_5=AUC_light_snipper("CAF","PRIMREWARD",5,exclude_outliers=True)
AUC_CTR_COR_PRIMREWARD_5=AUC_light_snipper("CTR","PRIMREWARD",5,exclude_outliers=True)
AUC_HFHS_COR_PRIMREWARD_5=AUC_light_snipper("HFHS","PRIMREWARD",5,exclude_outliers=True)

AUC_CAF_COR_SECREWARD_1=AUC_light_snipper("CAF","SECREWARD",1,exclude_outliers=True)
AUC_CTR_COR_SECREWARD_1=AUC_light_snipper("CTR","SECREWARD",1,exclude_outliers=True)
AUC_HFHS_COR_SECREWARD_1=AUC_light_snipper("HFHS","SECREWARD",1,exclude_outliers=True)

AUC_CAF_COR_SECREWARD_2=AUC_light_snipper("CAF","SECREWARD",2,exclude_outliers=True)
AUC_CTR_COR_SECREWARD_2=AUC_light_snipper("CTR","SECREWARD",2,exclude_outliers=True)
AUC_HFHS_COR_SECREWARD_2=AUC_light_snipper("HFHS","SECREWARD",2,exclude_outliers=True)

AUC_CAF_COR_SECREWARD_3=AUC_light_snipper("CAF","SECREWARD",3,exclude_outliers=True)
AUC_CTR_COR_SECREWARD_3=AUC_light_snipper("CTR","SECREWARD",3,exclude_outliers=True)
AUC_HFHS_COR_SECREWARD_3=AUC_light_snipper("HFHS","SECREWARD",3,exclude_outliers=True)

AUC_CAF_COR_DISREWARD_1=AUC_light_snipper("CAF","DISREWARD",1,exclude_outliers=True)
AUC_CTR_COR_DISREWARD_1=AUC_light_snipper("CTR","DISREWARD",1,exclude_outliers=True)
AUC_HFHS_COR_DISREWARD_1=AUC_light_snipper("HFHS","DISREWARD",1,exclude_outliers=True)

AUC_CAF_COR_PRIMREWARD_rev_1=AUC_light_snipper("CAF","PRIMREWARD_rev",1,exclude_outliers=True)
AUC_CTR_COR_PRIMREWARD_rev_1=AUC_light_snipper("CTR","PRIMREWARD_rev",1,exclude_outliers=True)
AUC_HFHS_COR_PRIMREWARD_rev_1=AUC_light_snipper("HFHS","PRIMREWARD_rev",1,exclude_outliers=True)

AUC_CAF_COR_PRIMREWARD_rev_3=AUC_light_snipper("CAF","PRIMREWARD_rev",3,exclude_outliers=True)
AUC_CTR_COR_PRIMREWARD_rev_3=AUC_light_snipper("CTR","PRIMREWARD_rev",3,exclude_outliers=True)
AUC_HFHS_COR_PRIMREWARD_rev_3=AUC_light_snipper("HFHS","PRIMREWARD_rev",3,exclude_outliers=True)

AUC_CAF_COR_SECREWARD_rev_1=AUC_light_snipper("CAF","SECREWARD_rev",1,exclude_outliers=True)
AUC_CTR_COR_SECREWARD_rev_1=AUC_light_snipper("CTR","SECREWARD_rev",1,exclude_outliers=True)
AUC_HFHS_COR_SECREWARD_rev_1=AUC_light_snipper("HFHS","SECREWARD_rev",1,exclude_outliers=True)

AUC_RESULTS_COR_PRIMREWARD_1=AUC_result_light_snipper("PRIMREWARD",1,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_PRIMREWARD_3=AUC_result_light_snipper("PRIMREWARD",3,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_PRIMREWARD_5=AUC_result_light_snipper("PRIMREWARD",5,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_SECREWARD_1=AUC_result_light_snipper("SECREWARD",1,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_SECREWARD_2=AUC_result_light_snipper("SECREWARD",2,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_SECREWARD_3=AUC_result_light_snipper("SECREWARD",3,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_DISREWARD_1=AUC_result_light_snipper("DISREWARD",1,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_PRIMREWARD_rev_1=AUC_result_light_snipper("PRIMREWARD_rev",1,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_PRIMREWARD_rev_3=AUC_result_light_snipper("PRIMREWARD_rev",3,graphtitle='AUC_cor',exclude_outliers=True)
AUC_RESULTS_COR_SECREWARD_rev_1=AUC_result_light_snipper("SECREWARD_rev",1,graphtitle='AUC_cor',exclude_outliers=True)


###################################################################################################
################## BEHAVIOR ########################################################
###################################################################################################

# # Make dictionaries and/or graphs of the snips of behavior
# # # Fill in the dataframe needed, the sniptime pre and post and a graphtitle (if wanted)
# # -> some parameter could be changed, e.g. output could be set to output='zscore'
# # dict_T_CAF_PRIM1_COR=behavior_snipper(data_T,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_PRIM1_COR=behavior_snipper(data_B,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_PRIM1_COR=behavior_snipper(data_I,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_PRIM1_COR=behavior_snipper(data_A,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_PRIM1_COR=behavior_snipper(data_P,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_PRIM1_COR=behavior_snipper(data_R,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_PRIM1_COR=behavior_snipper(data_T,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_PRIM1_COR=behavior_snipper(data_B,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_PRIM1_COR=behavior_snipper(data_I,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_PRIM1_COR=behavior_snipper(data_A,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_PRIM1_COR=behavior_snipper(data_P,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_PRIM1_COR=behavior_snipper(data_R,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_PRIM1_COR=behavior_snipper(data_T,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_PRIM1_COR=behavior_snipper(data_B,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_PRIM1_COR=behavior_snipper(data_I,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_PRIM1_COR=behavior_snipper(data_A,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_PRIM1_COR=behavior_snipper(data_P,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_PRIM1_COR=behavior_snipper(data_R,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_PRIM3_COR=behavior_snipper(data_T,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_PRIM3_COR=behavior_snipper(data_B,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_PRIM3_COR=behavior_snipper(data_I,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_PRIM3_COR=behavior_snipper(data_A,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_PRIM3_COR=behavior_snipper(data_P,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_PRIM3_COR=behavior_snipper(data_R,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_PRIM3_COR=behavior_snipper(data_T,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_PRIM3_COR=behavior_snipper(data_B,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_PRIM3_COR=behavior_snipper(data_I,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_PRIM3_COR=behavior_snipper(data_A,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_PRIM3_COR=behavior_snipper(data_P,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_PRIM3_COR=behavior_snipper(data_R,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_PRIM3_COR=behavior_snipper(data_T,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_PRIM3_COR=behavior_snipper(data_B,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_PRIM3_COR=behavior_snipper(data_I,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_PRIM3_COR=behavior_snipper(data_A,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_PRIM3_COR=behavior_snipper(data_P,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_PRIM3_COR=behavior_snipper(data_R,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_PRIM5_COR=behavior_snipper(data_T,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_PRIM5_COR=behavior_snipper(data_B,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_PRIM5_COR=behavior_snipper(data_I,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_PRIM5_COR=behavior_snipper(data_A,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_PRIM5_COR=behavior_snipper(data_P,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_PRIM5_COR=behavior_snipper(data_R,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  

# # # dict_T_CTR_PRIM5_COR=behavior_snipper(data_T,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_PRIM5_COR=behavior_snipper(data_B,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_PRIM5_COR=behavior_snipper(data_I,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_PRIM5_COR=behavior_snipper(data_A,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_PRIM5_COR=behavior_snipper(data_P,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_PRIM5_COR=behavior_snipper(data_R,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  

# # # dict_T_HFHS_PRIM5_COR=behavior_snipper(data_T,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_PRIM5_COR=behavior_snipper(data_B,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_PRIM5_COR=behavior_snipper(data_I,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_PRIM5_COR=behavior_snipper(data_A,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_PRIM5_COR=behavior_snipper(data_P,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_PRIM5_COR=behavior_snipper(data_R,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  

# # Secondary reward behavioral data
# # dict_T_CAF_SEC1_COR=behavior_snipper(data_T,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_SEC1_COR=behavior_snipper(data_B,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_SEC1_COR=behavior_snipper(data_I,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_SEC1_COR=behavior_snipper(data_A,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_SEC1_COR=behavior_snipper(data_P,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_SEC1_COR=behavior_snipper(data_R,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_SEC1_COR=behavior_snipper(data_T,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_SEC1_COR=behavior_snipper(data_B,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_SEC1_COR=behavior_snipper(data_I,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_SEC1_COR=behavior_snipper(data_A,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_SEC1_COR=behavior_snipper(data_P,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_SEC1_COR=behavior_snipper(data_R,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_SEC1_COR=behavior_snipper(data_T,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_SEC1_COR=behavior_snipper(data_B,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_SEC1_COR=behavior_snipper(data_I,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_SEC1_COR=behavior_snipper(data_A,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_SEC1_COR=behavior_snipper(data_P,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_SEC1_COR=behavior_snipper(data_R,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_SEC2_COR=behavior_snipper(data_T,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_SEC2_COR=behavior_snipper(data_B,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_SEC2_COR=behavior_snipper(data_I,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_SEC2_COR=behavior_snipper(data_A,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_SEC2_COR=behavior_snipper(data_P,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_SEC2_COR=behavior_snipper(data_R,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_SEC2_COR=behavior_snipper(data_T,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_SEC2_COR=behavior_snipper(data_B,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_SEC2_COR=behavior_snipper(data_I,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_SEC2_COR=behavior_snipper(data_A,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_SEC2_COR=behavior_snipper(data_P,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_SEC2_COR=behavior_snipper(data_R,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_SEC2_COR=behavior_snipper(data_T,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_SEC2_COR=behavior_snipper(data_B,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_SEC2_COR=behavior_snipper(data_I,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_SEC2_COR=behavior_snipper(data_A,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_SEC2_COR=behavior_snipper(data_P,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_SEC2_COR=behavior_snipper(data_R,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_SEC3_COR=behavior_snipper(data_T,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_SEC3_COR=behavior_snipper(data_B,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_SEC3_COR=behavior_snipper(data_I,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_SEC3_COR=behavior_snipper(data_A,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_SEC3_COR=behavior_snipper(data_P,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_SEC3_COR=behavior_snipper(data_R,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_SEC3_COR=behavior_snipper(data_T,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_SEC3_COR=behavior_snipper(data_B,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_SEC3_COR=behavior_snipper(data_I,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_SEC3_COR=behavior_snipper(data_A,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_SEC3_COR=behavior_snipper(data_P,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_SEC3_COR=behavior_snipper(data_R,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_SEC3_COR=behavior_snipper(data_T,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_SEC3_COR=behavior_snipper(data_B,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_SEC3_COR=behavior_snipper(data_I,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_SEC3_COR=behavior_snipper(data_A,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_SEC3_COR=behavior_snipper(data_P,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_SEC3_COR=behavior_snipper(data_R,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

# # Calculate behavior DISreward
# # dict_T_CAF_DIS1_COR=behavior_snipper(data_T,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_DIS1_COR=behavior_snipper(data_B,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_DIS1_COR=behavior_snipper(data_I,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_DIS1_COR=behavior_snipper(data_A,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_DIS1_COR=behavior_snipper(data_P,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_DIS1_COR=behavior_snipper(data_R,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_DIS1_COR=behavior_snipper(data_T,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_DIS1_COR=behavior_snipper(data_B,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_DIS1_COR=behavior_snipper(data_I,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_DIS1_COR=behavior_snipper(data_A,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_DIS1_COR=behavior_snipper(data_P,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_DIS1_COR=behavior_snipper(data_R,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_DIS1_COR=behavior_snipper(data_T,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_DIS1_COR=behavior_snipper(data_B,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_DIS1_COR=behavior_snipper(data_I,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_DIS1_COR=behavior_snipper(data_A,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_DIS1_COR=behavior_snipper(data_P,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_DIS1_COR=behavior_snipper(data_R,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

# # Calculate behavior PRIM_rev1
# # dict_T_CAF_PRIM_rev1_COR=behavior_snipper(data_T,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_PRIM_rev1_COR=behavior_snipper(data_B,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_PRIM_rev1_COR=behavior_snipper(data_I,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_PRIM_rev1_COR=behavior_snipper(data_A,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_PRIM_rev1_COR=behavior_snipper(data_P,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_PRIM_rev1_COR=behavior_snipper(data_R,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_PRIM_rev1_COR=behavior_snipper(data_T,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_PRIM_rev1_COR=behavior_snipper(data_B,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_PRIM_rev1_COR=behavior_snipper(data_I,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_PRIM_rev1_COR=behavior_snipper(data_A,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_PRIM_rev1_COR=behavior_snipper(data_P,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_PRIM_rev1_COR=behavior_snipper(data_R,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_PRIM_rev1_COR=behavior_snipper(data_T,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_PRIM_rev1_COR=behavior_snipper(data_B,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_PRIM_rev1_COR=behavior_snipper(data_I,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_PRIM_rev1_COR=behavior_snipper(data_A,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_PRIM_rev1_COR=behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_PRIM_rev1_COR=behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_PRIM_rev3_COR=behavior_snipper(data_T,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_PRIM_rev3_COR=behavior_snipper(data_B,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_PRIM_rev3_COR=behavior_snipper(data_I,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_PRIM_rev3_COR=behavior_snipper(data_A,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_PRIM_rev3_COR=behavior_snipper(data_P,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_PRIM_rev3_COR=behavior_snipper(data_R,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_PRIM_rev3_COR=behavior_snipper(data_T,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_PRIM_rev3_COR=behavior_snipper(data_B,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_PRIM_rev3_COR=behavior_snipper(data_I,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_PRIM_rev3_COR=behavior_snipper(data_A,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_PRIM_rev3_COR=behavior_snipper(data_P,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_PRIM_rev3_COR=behavior_snipper(data_R,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_PRIM_rev1_COR=behavior_snipper(data_T,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_PRIM_rev3_COR=behavior_snipper(data_B,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_PRIM_rev3_COR=behavior_snipper(data_I,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_PRIM_rev3_COR=behavior_snipper(data_A,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_PRIM_rev3_COR=behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_PRIM_rev3_COR=behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CAF_SEC_rev1_COR=behavior_snipper(data_T,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CAF_SEC_rev1_COR=behavior_snipper(data_B,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CAF_SEC_rev1_COR=behavior_snipper(data_I,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CAF_SEC_rev1_COR=behavior_snipper(data_A,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CAF_SEC_rev1_COR=behavior_snipper(data_P,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CAF_SEC_rev1_COR=behavior_snipper(data_R,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_CTR_SEC_rev1_COR=behavior_snipper(data_T,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_CTR_SEC_rev1_COR=behavior_snipper(data_B,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_CTR_SEC_rev1_COR=behavior_snipper(data_I,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_CTR_SEC_rev1_COR=behavior_snipper(data_A,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_CTR_SEC_rev1_COR=behavior_snipper(data_P,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_CTR_SEC_rev1_COR=behavior_snipper(data_R,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

# # dict_T_HFHS_SEC_rev1_COR=behavior_snipper(data_T,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')
# dict_B_HFHS_SEC_rev1_COR=behavior_snipper(data_B,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_I_HFHS_SEC_rev1_COR=behavior_snipper(data_I,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_A_HFHS_SEC_rev1_COR=behavior_snipper(data_A,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_P_HFHS_SEC_rev1_COR=behavior_snipper(data_P,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
# dict_R_HFHS_SEC_rev1_COR=behavior_snipper(data_R,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

########################################################################################################################
########## MAKE MEANS OF RATS OF BEHAVIORAL SNIPPERS####################################################################
########################################################################################################################
# Make dictionaries of GCAMP means of all rats and/or graphs
# Fill in the dictionary linked to the dataset, the sniptime pre and post and a graphtitle (if wanted,output='zscore')
# -> some parameter could be changed, e.g. output could be set to output='zscore'
# result_COR_T_CAF_PRIM1=result_snipper(data_T,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_CAF_PRIM1=result_snipper(data_B,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')  
result_COR_I_CAF_PRIM1=result_snipper(data_I,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')  
result_COR_A_CAF_PRIM1=result_snipper(data_A,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')  
result_COR_P_CAF_PRIM1=result_snipper(data_P,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_PRIM1=result_snipper(data_R,"CAF","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_PRIM1=result_snipper(data_T,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_CTR_PRIM1=result_snipper(data_B,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_PRIM1=result_snipper(data_I,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_PRIM1=result_snipper(data_A,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_PRIM1=result_snipper(data_P,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_PRIM1=result_snipper(data_R,"CTR","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_PRIM1=result_snipper(data_T,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_PRIM1=result_snipper(data_B,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_PRIM1=result_snipper(data_I,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_PRIM1=result_snipper(data_A,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_PRIM1=result_snipper(data_P,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_PRIM1=result_snipper(data_R,"HFHS","PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_PRIM3=result_snipper(data_T,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_PRIM3=result_snipper(data_B,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_PRIM3=result_snipper(data_I,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_PRIM3=result_snipper(data_A,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_PRIM3=result_snipper(data_P,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_PRIM3=result_snipper(data_R,"CAF","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_PRIM3=result_snipper(data_T,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_PRIM3=result_snipper(data_B,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_PRIM3=result_snipper(data_I,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_PRIM3=result_snipper(data_A,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_PRIM3=result_snipper(data_P,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_PRIM3=result_snipper(data_R,"CTR","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_PRIM3=result_snipper(data_T,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_PRIM3=result_snipper(data_B,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_PRIM3=result_snipper(data_I,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_PRIM3=result_snipper(data_A,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_PRIM3=result_snipper(data_P,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_PRIM3=result_snipper(data_R,"HFHS","PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_PRIM5=result_snipper(data_T,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_PRIM5=result_snipper(data_B,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_PRIM5=result_snipper(data_I,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_PRIM5=result_snipper(data_A,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_PRIM5=result_snipper(data_P,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_PRIM5=result_snipper(data_R,"CAF","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_PRIM5=result_snipper(data_T,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_PRIM5=result_snipper(data_B,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_PRIM5=result_snipper(data_I,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_PRIM5=result_snipper(data_A,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_PRIM5=result_snipper(data_P,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_PRIM5=result_snipper(data_R,"CTR","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_PRIM5=result_snipper(data_T,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_PRIM5=result_snipper(data_B,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_PRIM5=result_snipper(data_I,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_PRIM5=result_snipper(data_A,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_PRIM5=result_snipper(data_P,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_PRIM5=result_snipper(data_R,"HFHS","PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_SEC1=result_snipper(data_T,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_SEC1=result_snipper(data_B,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_SEC1=result_snipper(data_I,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_SEC1=result_snipper(data_A,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_SEC1=result_snipper(data_P,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_SEC1=result_snipper(data_R,"CAF","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_SEC1=result_snipper(data_T,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_SEC1=result_snipper(data_B,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_SEC1=result_snipper(data_I,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_SEC1=result_snipper(data_A,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_SEC1=result_snipper(data_P,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_SEC1=result_snipper(data_R,"CTR","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_SEC1=result_snipper(data_T,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_SEC1=result_snipper(data_B,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_SEC1=result_snipper(data_I,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_SEC1=result_snipper(data_A,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_SEC1=result_snipper(data_P,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_SEC1=result_snipper(data_R,"HFHS","SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_SEC2=result_snipper(data_T,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_SEC2=result_snipper(data_B,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_SEC2=result_snipper(data_I,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_SEC2=result_snipper(data_A,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_SEC2=result_snipper(data_P,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_SEC2=result_snipper(data_R,"CAF","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_SEC2=result_snipper(data_T,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_SEC2=result_snipper(data_B,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_SEC2=result_snipper(data_I,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_SEC2=result_snipper(data_A,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_SEC2=result_snipper(data_P,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_SEC2=result_snipper(data_R,"CTR","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_SEC2=result_snipper(data_T,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_SEC2=result_snipper(data_B,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_SEC2=result_snipper(data_I,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_SEC2=result_snipper(data_A,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_SEC2=result_snipper(data_P,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_SEC2=result_snipper(data_R,"HFHS","SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_SEC3=result_snipper(data_T,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_SEC3=result_snipper(data_B,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_SEC3=result_snipper(data_I,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_SEC3=result_snipper(data_A,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_SEC3=result_snipper(data_P,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_SEC3=result_snipper(data_R,"CAF","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_SEC3=result_snipper(data_T,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_SEC3=result_snipper(data_B,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_SEC3=result_snipper(data_I,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_SEC3=result_snipper(data_A,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_SEC3=result_snipper(data_P,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_SEC3=result_snipper(data_R,"CTR","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_SEC3=result_snipper(data_T,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_SEC3=result_snipper(data_B,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_SEC3=result_snipper(data_I,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_SEC3=result_snipper(data_A,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_SEC3=result_snipper(data_P,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_SEC3=result_snipper(data_R,"HFHS","SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_PRIM_rev1=result_snipper(data_T,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_PRIM_rev1=result_snipper(data_B,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_PRIM_rev1=result_snipper(data_I,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_PRIM_rev1=result_snipper(data_A,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_PRIM_rev1=result_snipper(data_P,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_PRIM_rev1=result_snipper(data_R,"CAF","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_PRIM_rev1=result_snipper(data_T,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_PRIM_rev1=result_snipper(data_B,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_PRIM_rev1=result_snipper(data_I,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_PRIM_rev1=result_snipper(data_A,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_PRIM_rev1=result_snipper(data_P,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_PRIM_rev1=result_snipper(data_R,"CTR","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_PRIM_rev1=result_snipper(data_T,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_PRIM_rev1=result_snipper(data_B,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_PRIM_rev1=result_snipper(data_I,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_PRIM_rev1=result_snipper(data_A,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_PRIM_rev1=result_snipper(data_P,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_PRIM_rev1=result_snipper(data_R,"HFHS","PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_PRIM_rev3=result_snipper(data_T,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_PRIM_rev3=result_snipper(data_B,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_PRIM_rev3=result_snipper(data_I,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_PRIM_rev3=result_snipper(data_A,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_PRIM_rev3=result_snipper(data_P,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_PRIM_rev3=result_snipper(data_R,"CAF","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_PRIM_rev3=result_snipper(data_T,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_PRIM_rev3=result_snipper(data_B,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_PRIM_rev3=result_snipper(data_I,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_PRIM_rev3=result_snipper(data_A,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_PRIM_rev3=result_snipper(data_P,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_PRIM_rev3=result_snipper(data_R,"CTR","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_PRIM_rev3=result_snipper(data_T,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_PRIM_rev3=result_snipper(data_B,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_PRIM_rev3=result_snipper(data_I,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_PRIM_rev3=result_snipper(data_A,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_PRIM_rev3=result_snipper(data_P,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_PRIM_rev3=result_snipper(data_R,"HFHS","PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_SEC_rev1=result_snipper(data_T,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_SEC_rev1=result_snipper(data_B,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_SEC_rev1=result_snipper(data_I,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_SEC_rev1=result_snipper(data_A,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_SEC_rev1=result_snipper(data_P,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_SEC_rev1=result_snipper(data_R,"CAF","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_SEC_rev1=result_snipper(data_T,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_SEC_rev1=result_snipper(data_B,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_SEC_rev1=result_snipper(data_I,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_SEC_rev1=result_snipper(data_A,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_SEC_rev1=result_snipper(data_P,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_SEC_rev1=result_snipper(data_R,"CTR","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_SEC_rev1=result_snipper(data_T,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_SEC_rev1=result_snipper(data_B,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_SEC_rev1=result_snipper(data_I,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_SEC_rev1=result_snipper(data_A,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_SEC_rev1=result_snipper(data_P,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_SEC_rev1=result_snipper(data_R,"HFHS","SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CAF_DIS1=result_snipper(data_T,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CAF_DIS1=result_snipper(data_B,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CAF_DIS1=result_snipper(data_I,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CAF_DIS1=result_snipper(data_A,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CAF_DIS1=result_snipper(data_P,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CAF_DIS1=result_snipper(data_R,"CAF","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_CTR_DIS1=result_snipper(data_T,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_CTR_DIS1=result_snipper(data_B,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_CTR_DIS1=result_snipper(data_I,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_CTR_DIS1=result_snipper(data_A,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_CTR_DIS1=result_snipper(data_P,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_CTR_DIS1=result_snipper(data_R,"CTR","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

# result_COR_T_HFHS_DIS1=result_snipper(data_T,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_B_HFHS_DIS1=result_snipper(data_B,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='B_excl ')   
result_COR_I_HFHS_DIS1=result_snipper(data_I,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='I_excl ')   
result_COR_A_HFHS_DIS1=result_snipper(data_A,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='A_excl ')   
result_COR_P_HFHS_DIS1=result_snipper(data_P,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='P_excl ')   
result_COR_R_HFHS_DIS1=result_snipper(data_R,"HFHS","DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')#,graphtitle='R_excl ')   

#################GFP##################
# # # # Fill in the dictionary linked to the dataset, the sniptime pre and post and a graphtitle (if wanted)
# -> some parameter could be changed, e.g. output could be set to output='zscore'
result_COR_T_GFP_PRIM1=result_snipper_GFP(data_T,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_PRIM1=result_snipper_GFP(data_B,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_PRIM1=result_snipper_GFP(data_I,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_PRIM1=result_snipper_GFP(data_A,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_PRIM1=result_snipper_GFP(data_P,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_PRIM1=result_snipper_GFP(data_R,"PRIMREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

result_COR_T_GFP_PRIM3=result_snipper_GFP(data_T,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_PRIM3=result_snipper_GFP(data_B,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_PRIM3=result_snipper_GFP(data_I,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_PRIM3=result_snipper_GFP(data_A,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_PRIM3=result_snipper_GFP(data_P,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_PRIM3=result_snipper_GFP(data_R,"PRIMREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

result_COR_T_GFP_PRIM5=result_snipper_GFP(data_T,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_PRIM5=result_snipper_GFP(data_B,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_PRIM5=result_snipper_GFP(data_I,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_PRIM5=result_snipper_GFP(data_A,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_PRIM5=result_snipper_GFP(data_P,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_PRIM5=result_snipper_GFP(data_R,"PRIMREWARD",5,exclude_outliers=True, excluding_behaviors='include')  

result_COR_T_GFP_SEC1=result_snipper_GFP(data_T,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_SEC1=result_snipper_GFP(data_B,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_SEC1=result_snipper_GFP(data_I,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_SEC1=result_snipper_GFP(data_A,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_SEC1=result_snipper_GFP(data_P,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_SEC1=result_snipper_GFP(data_R,"SECREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

result_COR_T_GFP_SEC2=result_snipper_GFP(data_T,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_SEC2=result_snipper_GFP(data_B,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_SEC2=result_snipper_GFP(data_I,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_SEC2=result_snipper_GFP(data_A,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_SEC2=result_snipper_GFP(data_P,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_SEC2=result_snipper_GFP(data_R,"SECREWARD",2,exclude_outliers=True, excluding_behaviors='include')  

result_COR_T_GFP_SEC3=result_snipper_GFP(data_T,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_B_GFP_SEC3=result_snipper_GFP(data_B,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_SEC3=result_snipper_GFP(data_I,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_SEC3=result_snipper_GFP(data_A,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_SEC3=result_snipper_GFP(data_P,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_SEC3=result_snipper_GFP(data_R,"SECREWARD",3,exclude_outliers=True, excluding_behaviors='include')  

result_COR_B_GFP_DIS1=result_snipper_GFP(data_B,"DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_DIS1=result_snipper_GFP(data_I,"DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_DIS1=result_snipper_GFP(data_A,"DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_DIS1=result_snipper_GFP(data_P,"DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_DIS1=result_snipper_GFP(data_R,"DISREWARD",1,exclude_outliers=True, excluding_behaviors='include')  

result_COR_B_GFP_PRIM_rev1=result_snipper_GFP(data_B,"PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_PRIM_rev1=result_snipper_GFP(data_I,"PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_PRIM_rev1=result_snipper_GFP(data_A,"PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_PRIM_rev1=result_snipper_GFP(data_P,"PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_PRIM_rev1=result_snipper_GFP(data_R,"PRIMREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

result_COR_B_GFP_PRIM_rev3=result_snipper_GFP(data_B,"PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_PRIM_rev3=result_snipper_GFP(data_I,"PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_PRIM_rev3=result_snipper_GFP(data_A,"PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_PRIM_rev3=result_snipper_GFP(data_P,"PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_PRIM_rev3=result_snipper_GFP(data_R,"PRIMREWARD_rev",3,exclude_outliers=True, excluding_behaviors='include')  

result_COR_B_GFP_SEC_rev1=result_snipper_GFP(data_B,"SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_I_GFP_SEC_rev1=result_snipper_GFP(data_I,"SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_A_GFP_SEC_rev1=result_snipper_GFP(data_A,"SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_P_GFP_SEC_rev1=result_snipper_GFP(data_P,"SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  
result_COR_R_GFP_SEC_rev1=result_snipper_GFP(data_R,"SECREWARD_rev",1,exclude_outliers=True, excluding_behaviors='include')  

###################################
# Compare the different treatment groups per behavior
# -> some parameter could be changed, e.g. output could be set to output='zscore'
PRIMREW1_R_COR=compare_behavior_snipper(result_COR_R_CTR_PRIM1,result_COR_R_HFHS_PRIM1,result_COR_R_CAF_PRIM1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward")
PRIMREW3_R_COR=compare_behavior_snipper(result_COR_R_CTR_PRIM3,result_COR_R_HFHS_PRIM3,result_COR_R_CAF_PRIM3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward")
PRIMREW5_R_COR=compare_behavior_snipper(result_COR_R_CTR_PRIM5,result_COR_R_HFHS_PRIM5,result_COR_R_CAF_PRIM5,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW5_COR_incl",exclude_outliers=True)#"5th primary reward")
SECREW1_R_COR=compare_behavior_snipper(result_COR_R_CTR_SEC1,result_COR_R_HFHS_SEC1,result_COR_R_CAF_SEC1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward")
SECREW2_R_COR=compare_behavior_snipper(result_COR_R_CTR_SEC2,result_COR_R_HFHS_SEC2,result_COR_R_CAF_SEC2,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW2_COR_incl",exclude_outliers=True)#"2nd secondary reward")
SECREW3_R_COR=compare_behavior_snipper(result_COR_R_CTR_SEC3,result_COR_R_HFHS_SEC3,result_COR_R_CAF_SEC3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW3_COR_incl",exclude_outliers=True)#"3rd secondary reward")
DISREW1_R_COR=compare_behavior_snipper(result_COR_R_CTR_DIS1,result_COR_R_HFHS_DIS1,result_COR_R_CAF_DIS1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow")
PRIMREW_rev1_R_COR=compare_behavior_snipper(result_COR_R_CTR_PRIM_rev1,result_COR_R_HFHS_PRIM_rev1,result_COR_R_CAF_PRIM_rev1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward after reversal")
PRIMREW_rev3_R_COR=compare_behavior_snipper(result_COR_R_CTR_PRIM_rev3,result_COR_R_HFHS_PRIM_rev3,result_COR_R_CAF_PRIM_rev3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward after reversal")
SECREW_rev1_R_COR=compare_behavior_snipper(result_COR_R_CTR_SEC_rev1,result_COR_R_HFHS_SEC_rev1,result_COR_R_CAF_SEC_rev1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward after reversal")

PRIMREW1_P_COR=compare_behavior_snipper(result_COR_P_CTR_PRIM1,result_COR_P_HFHS_PRIM1,result_COR_P_CAF_PRIM1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward")
PRIMREW3_P_COR=compare_behavior_snipper(result_COR_P_CTR_PRIM3,result_COR_P_HFHS_PRIM3,result_COR_P_CAF_PRIM3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward")
PRIMREW5_P_COR=compare_behavior_snipper(result_COR_P_CTR_PRIM5,result_COR_P_HFHS_PRIM5,result_COR_P_CAF_PRIM5,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW5_COR_incl",exclude_outliers=True)#"5th primary (pre)reward")
SECREW1_P_COR=compare_behavior_snipper(result_COR_P_CTR_SEC1,result_COR_P_HFHS_SEC1,result_COR_P_CAF_SEC1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward")
SECREW2_P_COR=compare_behavior_snipper(result_COR_P_CTR_SEC2,result_COR_P_HFHS_SEC2,result_COR_P_CAF_SEC2,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW2_COR_incl",exclude_outliers=True)#"2nd secondary (pre)reward")
SECREW3_P_COR=compare_behavior_snipper(result_COR_P_CTR_SEC3,result_COR_P_HFHS_SEC3,result_COR_P_CAF_SEC3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW3_COR_incl",exclude_outliers=True)#"3rd secondary (pre)reward")
DISREW1_P_COR=compare_behavior_snipper(result_COR_P_CTR_DIS1,result_COR_P_HFHS_DIS1,result_COR_P_CAF_DIS1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow (pre)")
PRIMREW_rev1_P_COR=compare_behavior_snipper(result_COR_P_CTR_PRIM_rev1,result_COR_P_HFHS_PRIM_rev1,result_COR_P_CAF_PRIM_rev1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward after reversal")
PRIMREW_rev3_P_COR=compare_behavior_snipper(result_COR_P_CTR_PRIM_rev3,result_COR_P_HFHS_PRIM_rev3,result_COR_P_CAF_PRIM_rev3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward after reversal")
SECREW_rev1_P_COR=compare_behavior_snipper(result_COR_P_CTR_SEC_rev1,result_COR_P_HFHS_SEC_rev1,result_COR_P_CAF_SEC_rev1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward after reversal")

# Compare the different treatment groups per behavior for only CAF and CTR
PRIMREW1_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_PRIM1,result_COR_R_CAF_PRIM1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward")
PRIMREW3_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_PRIM3,result_COR_R_CAF_PRIM3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward")
PRIMREW5_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_PRIM5,result_COR_R_CAF_PRIM5,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW5_COR_incl",exclude_outliers=True)#"5th primary reward")
SECREW1_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_SEC1,result_COR_R_CAF_SEC1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward")
SECREW2_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_SEC2,result_COR_R_CAF_SEC2,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW2_COR_incl",exclude_outliers=True)#"2nd secondary reward")
SECREW3_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_SEC3,result_COR_R_CAF_SEC3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW3_COR_incl",exclude_outliers=True)#"3rd secondary reward")
DISREW1_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_DIS1,result_COR_R_CAF_DIS1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow")
PRIMREW_rev1_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_PRIM_rev1,result_COR_R_CAF_PRIM_rev1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward after reversal")
PRIMREW_rev3_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_PRIM_rev3,result_COR_R_CAF_PRIM_rev3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward after reversal")
SECREW_rev1_R_CAF_COR=compare_behavior_snipper_CAF(result_COR_R_CTR_SEC_rev1,result_COR_R_CAF_SEC_rev1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward after reversal")

PRIMREW1_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_PRIM1,result_COR_P_CAF_PRIM1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward")
PRIMREW3_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_PRIM3,result_COR_P_CAF_PRIM3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward")
PRIMREW5_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_PRIM5,result_COR_P_CAF_PRIM5,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW5_COR_incl",exclude_outliers=True)#"5th primary (pre)reward")
SECREW1_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_SEC1,result_COR_P_CAF_SEC1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward")
SECREW2_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_SEC2,result_COR_P_CAF_SEC2,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW2_COR_incl",exclude_outliers=True)#"2nd secondary (pre)reward")
SECREW3_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_SEC3,result_COR_P_CAF_SEC3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW3_COR_incl",exclude_outliers=True)#"3rd secondary (pre)reward")
DISREW1_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_DIS1,result_COR_P_CAF_DIS1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow (pre)")
PRIMREW_rev1_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_PRIM_rev1,result_COR_P_CAF_PRIM_rev1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward after reversal")
PRIMREW_rev3_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_PRIM_rev3,result_COR_P_CAF_PRIM_rev3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward after reversal")
SECREW_rev1_P_CAF_COR=compare_behavior_snipper_CAF(result_COR_P_CTR_SEC_rev1,result_COR_P_CAF_SEC_rev1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward after reversal")

# Compare the different treatment groups per behavior with GFP
# -> some parameter could be changed, e.g. output could be set to output='zscore'
PRIMREW1_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_PRIM1,result_COR_R_HFHS_PRIM1,result_COR_R_CAF_PRIM1,result_COR_R_GFP_PRIM1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward")
PRIMREW3_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_PRIM3,result_COR_R_HFHS_PRIM3,result_COR_R_CAF_PRIM3,result_COR_R_GFP_PRIM3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward")
PRIMREW5_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_PRIM5,result_COR_R_HFHS_PRIM5,result_COR_R_CAF_PRIM5,result_COR_R_GFP_PRIM5,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW5_COR_incl",exclude_outliers=True)#"5th primary reward")
SECREW1_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_SEC1,result_COR_R_HFHS_SEC1,result_COR_R_CAF_SEC1,result_COR_R_GFP_SEC1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward")
SECREW2_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_SEC2,result_COR_R_HFHS_SEC2,result_COR_R_CAF_SEC2,result_COR_R_GFP_SEC2,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW2_COR_incl",exclude_outliers=True)#"1st secondary reward")
SECREW3_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_SEC3,result_COR_R_HFHS_SEC3,result_COR_R_CAF_SEC3,result_COR_R_GFP_SEC3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW3_COR_incl",exclude_outliers=True)#"1st secondary reward")
DISREW1_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_DIS1,result_COR_R_HFHS_DIS1,result_COR_R_CAF_DIS1,result_COR_R_GFP_DIS1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow")
PRIMREW_rev1_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_PRIM_rev1,result_COR_R_HFHS_PRIM_rev1,result_COR_R_CAF_PRIM_rev1,result_COR_R_GFP_PRIM_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary reward after reversal")
PRIMREW_rev3_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_PRIM_rev3,result_COR_R_HFHS_PRIM_rev3,result_COR_R_CAF_PRIM_rev3,result_COR_R_GFP_PRIM_rev3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary reward after reversal")
SECREW_rev1_R_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_R_CTR_SEC_rev1,result_COR_R_HFHS_SEC_rev1,result_COR_R_CAF_SEC_rev1,result_COR_R_GFP_SEC_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary reward after reversal")

PRIMREW1_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_PRIM1,result_COR_P_HFHS_PRIM1,result_COR_P_CAF_PRIM1,result_COR_P_GFP_PRIM1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward")
PRIMREW3_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_PRIM3,result_COR_P_HFHS_PRIM3,result_COR_P_CAF_PRIM3,result_COR_P_GFP_PRIM3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward")
PRIMREW5_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_PRIM5,result_COR_P_HFHS_PRIM5,result_COR_P_CAF_PRIM5,result_COR_P_GFP_PRIM5,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_COR_incl",exclude_outliers=True)#"5th primary (pre)reward")
SECREW1_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_SEC1,result_COR_P_HFHS_SEC1,result_COR_P_CAF_SEC1,result_COR_P_GFP_SEC1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward")
SECREW2_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_SEC2,result_COR_P_HFHS_SEC2,result_COR_P_CAF_SEC2,result_COR_P_GFP_SEC2,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward")
SECREW3_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_SEC3,result_COR_P_HFHS_SEC3,result_COR_P_CAF_SEC3,result_COR_P_GFP_SEC3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward")
DISREW1_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_DIS1,result_COR_P_HFHS_DIS1,result_COR_P_CAF_DIS1,result_COR_P_GFP_DIS1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_STDCHOW_COR_incl",exclude_outliers=True)#"standard chow (pre)")
PRIMREW_rev1_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_PRIM_rev1,result_COR_P_HFHS_PRIM_rev1,result_COR_P_CAF_PRIM_rev1,result_COR_P_GFP_PRIM_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_COR_incl",exclude_outliers=True)#"1st primary (pre)reward after reversal")
PRIMREW_rev3_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_PRIM_rev3,result_COR_P_HFHS_PRIM_rev3,result_COR_P_CAF_PRIM_rev3,result_COR_P_GFP_PRIM_rev3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_COR_incl",exclude_outliers=True)#"3rd primary (pre)reward after reversal")
SECREW_rev1_P_GFP_COR=compare_behavior_snipper_plusGFP(result_COR_P_CTR_SEC_rev1,result_COR_P_HFHS_SEC_rev1,result_COR_P_CAF_SEC_rev1,result_COR_P_GFP_SEC_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revSECREW1_COR_incl",exclude_outliers=True)#"1st secondary (pre)reward after reversal")                          'Mount (received)','Paracopulatory','Rejection','Selfgrooming','Sniffing reward']

###################################################################################################
################## AUC GRAPHS WITH INCLUDED BEHAVIORS!!! (BUT EXCLUDING OUTLIERS IN DFF SIGNAL ########################################################
###################################################################################################

# AUC behavior snipper
AUC_CAF_COR_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD1_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD1_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD2_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD2_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD2_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD3_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD3_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD3_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_DISREWARD1_R=AUC_behavior_snipper(data_R,"CAF","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_DISREWARD1_R=AUC_behavior_snipper(data_R,"CTR","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_DISREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",5,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD1_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD1_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD2_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD2_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD2_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",2,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD3_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD3_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD3_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",3,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD_rev",1,excluding_behaviors='include',exclude_outliers=True)  

AUC_CAF_COR_DISREWARD1_P=AUC_behavior_snipper(data_P,"CAF","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_CTR_COR_DISREWARD1_P=AUC_behavior_snipper(data_P,"CTR","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  
AUC_HFHS_COR_DISREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","DISREWARD",1,excluding_behaviors='include',exclude_outliers=True)  

###################################################################################################
################## GRAPHS WITH DFF OUTLIERS - IN RESULTS FOLDER ########################################################
###################################################################################################

###################################################################################################
################## GRAPHS WITH DFF AND ALL INCLUDED BEHAVIORS - ########################################################
###################################################################################################

###################################################################################################
################## LIGHTDOOR ########################################################
###################################################################################################

# # Calculate the means of door and light -> some parameter could be changed, 
# # e.g. output could be set to output='zscore'
# RESULTS_LIGHT_CAF_PRIM_1=result_lightdoor_snipper("CAF","PRIMREWARD",1)
# RESULTS_LIGHT_HFHS_PRIM_1=result_lightdoor_snipper("HFHS","PRIMREWARD",1)
# RESULTS_LIGHT_CTR_PRIM_1=result_lightdoor_snipper("CTR","PRIMREWARD",1)

# RESULTS_LIGHT_CAF_PRIM_3=result_lightdoor_snipper("CAF","PRIMREWARD",3)
# RESULTS_LIGHT_HFHS_PRIM_3=result_lightdoor_snipper("HFHS","PRIMREWARD",3)
# RESULTS_LIGHT_CTR_PRIM_3=result_lightdoor_snipper("CTR","PRIMREWARD",3)

# RESULTS_LIGHT_CAF_PRIM_5=result_lightdoor_snipper("CAF","PRIMREWARD",5)
# RESULTS_LIGHT_HFHS_PRIM_5=result_lightdoor_snipper("HFHS","PRIMREWARD",5)
# RESULTS_LIGHT_CTR_PRIM_5=result_lightdoor_snipper("CTR","PRIMREWARD",5)

# RESULTS_LIGHT_CAF_SEC_1=result_lightdoor_snipper("CAF","SECREWARD",1)
# RESULTS_LIGHT_HFHS_SEC_1=result_lightdoor_snipper("HFHS","SECREWARD",1)
# RESULTS_LIGHT_CTR_SEC_1=result_lightdoor_snipper("CTR","SECREWARD",1)

# RESULTS_LIGHT_CAF_SEC_2=result_lightdoor_snipper("CAF","SECREWARD",2)
# RESULTS_LIGHT_HFHS_SEC_2=result_lightdoor_snipper("HFHS","SECREWARD",2)
# RESULTS_LIGHT_CTR_SEC_2=result_lightdoor_snipper("CTR","SECREWARD",2)

# RESULTS_LIGHT_CAF_SEC_3=result_lightdoor_snipper("CAF","SECREWARD",3)
# RESULTS_LIGHT_HFHS_SEC_3=result_lightdoor_snipper("HFHS","SECREWARD",3)
# RESULTS_LIGHT_CTR_SEC_3=result_lightdoor_snipper("CTR","SECREWARD",3)

# RESULTS_LIGHT_CAF_PRIMREV_1=result_lightdoor_snipper("CAF","PRIMREWARD_rev",1)
# RESULTS_LIGHT_HFHS_PRIMREV_1=result_lightdoor_snipper("HFHS","PRIMREWARD_rev",1)
# RESULTS_LIGHT_CTR_PRIMREV_1=result_lightdoor_snipper("CTR","PRIMREWARD_rev",1)

# RESULTS_LIGHT_CAF_PRIMREV_3=result_lightdoor_snipper("CAF","PRIMREWARD_rev",3)
# RESULTS_LIGHT_HFHS_PRIMREV_3=result_lightdoor_snipper("HFHS","PRIMREWARD_rev",3)
# RESULTS_LIGHT_CTR_PRIMREV_3=result_lightdoor_snipper("CTR","PRIMREWARD_rev",3)

# RESULTS_LIGHT_CAF_SECREV_1=result_lightdoor_snipper("CAF","SECREWARD_rev",1)
# RESULTS_LIGHT_HFHS_SECREV_1=result_lightdoor_snipper("HFHS","SECREWARD_rev",1)
# RESULTS_LIGHT_CTR_SECREV_1=result_lightdoor_snipper("CTR","SECREWARD_rev",1)

# RESULTS_LIGHT_CAF_DISREWARD_1=result_lightdoor_snipper("CAF","DISREWARD",1)
# RESULTS_LIGHT_HFHS_DISREWARD_1=result_lightdoor_snipper("HFHS","DISREWARD",1)
# RESULTS_LIGHT_CTR_DISREWARD_1=result_lightdoor_snipper("CTR","DISREWARD",1)

# # # Make graphs for the comparisons -> some parameter could be changed, e.g. output could be set to output='zscore'
# LIGHT_PRIMREW1= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1,"CTR","HFHS","CAF",graphtitle="PRIMREW1")
# LIGHT_PRIMREW3= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_3,RESULTS_LIGHT_HFHS_PRIM_3,RESULTS_LIGHT_CAF_PRIM_3,"CTR","HFHS","CAF",graphtitle="PRIMREW3")
# LIGHT_PRIMREW5= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_HFHS_PRIM_5,RESULTS_LIGHT_CAF_PRIM_5,"CTR","HFHS","CAF",graphtitle="PRIMREW5")

# LIGHT_SECREW1= compare_light_snipper(RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_HFHS_SEC_1,RESULTS_LIGHT_CAF_SEC_1,"CTR","HFHS","CAF",graphtitle="SECREW1")
# LIGHT_SECREW2= compare_light_snipper(RESULTS_LIGHT_CTR_SEC_2,RESULTS_LIGHT_HFHS_SEC_2,RESULTS_LIGHT_CAF_SEC_2,"CTR","HFHS","CAF",graphtitle="SECREW2")
# LIGHT_SECREW3= compare_light_snipper(RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_HFHS_SEC_3,RESULTS_LIGHT_CAF_SEC_3,"CTR","HFHS","CAF",graphtitle="SECREW3")

# LIGHT_PRIMREWREV1= compare_light_snipper(RESULTS_LIGHT_CTR_PRIMREV_1,RESULTS_LIGHT_HFHS_PRIMREV_1,RESULTS_LIGHT_CAF_PRIMREV_1,"CTR","HFHS","CAF",graphtitle="revPRIMREW1")
# LIGHT_PRIMREWREV3= compare_light_snipper(RESULTS_LIGHT_CTR_PRIMREV_3,RESULTS_LIGHT_HFHS_PRIMREV_3,RESULTS_LIGHT_CAF_PRIMREV_3,"CTR","HFHS","CAF",graphtitle="revPRIMREW3")
# LIGHT_SECREWREV1= compare_light_snipper(RESULTS_LIGHT_CTR_SECREV_1,RESULTS_LIGHT_HFHS_SECREV_1,RESULTS_LIGHT_CAF_SECREV_1,"CTR","HFHS","CAF",graphtitle="revSECREW1")

# LIGHT_DISREW1= compare_light_snipper(RESULTS_LIGHT_CTR_DISREWARD_1,RESULTS_LIGHT_HFHS_DISREWARD_1,RESULTS_LIGHT_CAF_DISREWARD_1,"CTR","HFHS","CAF",graphtitle="STDCHOW")

# # For only CTR and CAF
# LIGHT_PRIMREW1= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_CAF_PRIM_1,"CTR","CAF",graphtitle="PRIMREW1")
# LIGHT_PRIMREW3= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_PRIM_3,RESULTS_LIGHT_CAF_PRIM_3,"CTR","CAF",graphtitle="PRIMREW3")
# LIGHT_PRIMREW5= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_CAF_PRIM_5,"CTR","CAF",graphtitle="PRIMREW5")

# LIGHT_SECREW1= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_CAF_SEC_1,"CTR","CAF",graphtitle="SECREW1")
# LIGHT_SECREW2= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_SEC_2,RESULTS_LIGHT_CAF_SEC_2,"CTR","CAF",graphtitle="SECREW2")
# LIGHT_SECREW3= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_CAF_SEC_3,"CTR","CAF",graphtitle="SECREW3")

# LIGHT_PRIMREWREV1= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_PRIMREV_1,RESULTS_LIGHT_CAF_PRIMREV_1,"CTR","CAF",graphtitle="revPRIMREW1")
# LIGHT_PRIMREWREV3= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_PRIMREV_3,RESULTS_LIGHT_CAF_PRIMREV_3,"CTR","CAF",graphtitle="revPRIMREW3")
# LIGHT_SECREWREV1= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_SECREV_1,RESULTS_LIGHT_CAF_SECREV_1,"CTR","CAF",graphtitle="revSECREW1")

# LIGHT_DISREW1= compare_light_snipper_2cond(RESULTS_LIGHT_CTR_DISREWARD_1,RESULTS_LIGHT_CAF_DISREWARD_1,"CTR","CAF",graphtitle="STDCHOW")

# # Make graphs to compare sex and food -> some parameter could be changed, e.g. output could be set to output='zscore'
# LIGHT_PRIMSEC1_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_1,RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison1")
# LIGHT_PRIMSEC1_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_1,RESULTS_LIGHT_CAF_SEC_1,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison1")
# LIGHT_PRIMSEC1_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_HFHS_SEC_1,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison1")

# LIGHT_PRIMSEC3_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison3")
# LIGHT_PRIMSEC3_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_5,RESULTS_LIGHT_CAF_SEC_3,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison3")
# LIGHT_PRIMSEC3_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_5,RESULTS_LIGHT_HFHS_SEC_3,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison3")

# # Make graphs to compare sex and food -> some parameter could be changed, e.g. output could be set to output='zscore'
# LIGHT_PRIMSEC1_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_3,RESULTS_LIGHT_CTR_SEC_1,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison1")
# LIGHT_PRIMSEC1_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_1,RESULTS_LIGHT_CAF_SEC_1,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison1")
# LIGHT_PRIMSEC1_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_1,RESULTS_LIGHT_HFHS_SEC_1,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison1")

# LIGHT_PRIMSEC3_CTR= compare_light_snipper(RESULTS_LIGHT_CTR_PRIM_5,RESULTS_LIGHT_CTR_SEC_3,RESULTS_LIGHT_CTR_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CTR_comparison3")
# LIGHT_PRIMSEC3_CAF= compare_light_snipper(RESULTS_LIGHT_CAF_PRIM_5,RESULTS_LIGHT_CAF_SEC_3,RESULTS_LIGHT_CAF_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_CAF_comparison3")
# LIGHT_PRIMSEC3_HFHS= compare_light_snipper(RESULTS_LIGHT_HFHS_PRIM_5,RESULTS_LIGHT_HFHS_SEC_3,RESULTS_LIGHT_HFHS_DISREWARD_1,"Primary","Secondary","Chow",graphtitle="Reward_HFHS_comparison3")

# ##################################
# # Calculate AUC Light-door
# AUC_CAF_PRIMREWARD_1=AUC_light_snipper("CAF","PRIMREWARD",1)
# AUC_CTR_PRIMREWARD_1=AUC_light_snipper("CTR","PRIMREWARD",1)
# AUC_HFHS_PRIMREWARD_1=AUC_light_snipper("HFHS","PRIMREWARD",1)

# AUC_CAF_PRIMREWARD_3=AUC_light_snipper("CAF","PRIMREWARD",3)
# AUC_CTR_PRIMREWARD_3=AUC_light_snipper("CTR","PRIMREWARD",3)
# AUC_HFHS_PRIMREWARD_3=AUC_light_snipper("HFHS","PRIMREWARD",3)

# AUC_CAF_PRIMREWARD_5=AUC_light_snipper("CAF","PRIMREWARD",5)
# AUC_CTR_PRIMREWARD_5=AUC_light_snipper("CTR","PRIMREWARD",5)
# AUC_HFHS_PRIMREWARD_5=AUC_light_snipper("HFHS","PRIMREWARD",5)

# AUC_CAF_SECREWARD_1=AUC_light_snipper("CAF","SECREWARD",1)
# AUC_CTR_SECREWARD_1=AUC_light_snipper("CTR","SECREWARD",1)
# AUC_HFHS_SECREWARD_1=AUC_light_snipper("HFHS","SECREWARD",1)

# AUC_CAF_SECREWARD_2=AUC_light_snipper("CAF","SECREWARD",2)
# AUC_CTR_SECREWARD_2=AUC_light_snipper("CTR","SECREWARD",2)
# AUC_HFHS_SECREWARD_2=AUC_light_snipper("HFHS","SECREWARD",2)

# AUC_CAF_SECREWARD_3=AUC_light_snipper("CAF","SECREWARD",3)
# AUC_CTR_SECREWARD_3=AUC_light_snipper("CTR","SECREWARD",3)
# AUC_HFHS_SECREWARD_3=AUC_light_snipper("HFHS","SECREWARD",3)

# AUC_CAF_DISREWARD_1=AUC_light_snipper("CAF","DISREWARD",1)
# AUC_CTR_DISREWARD_1=AUC_light_snipper("CTR","DISREWARD",1)
# AUC_HFHS_DISREWARD_1=AUC_light_snipper("HFHS","DISREWARD",1)

# AUC_CAF_PRIMREWARD_rev_1=AUC_light_snipper("CAF","PRIMREWARD_rev",1)
# AUC_CTR_PRIMREWARD_rev_1=AUC_light_snipper("CTR","PRIMREWARD_rev",1)
# AUC_HFHS_PRIMREWARD_rev_1=AUC_light_snipper("HFHS","PRIMREWARD_rev",1)

# AUC_CAF_PRIMREWARD_rev_3=AUC_light_snipper("CAF","PRIMREWARD_rev",3)
# AUC_CTR_PRIMREWARD_rev_3=AUC_light_snipper("CTR","PRIMREWARD_rev",3)
# AUC_HFHS_PRIMREWARD_rev_3=AUC_light_snipper("HFHS","PRIMREWARD_rev",3)

# AUC_CAF_SECREWARD_rev_1=AUC_light_snipper("CAF","SECREWARD_rev",1)
# AUC_CTR_SECREWARD_rev_1=AUC_light_snipper("CTR","SECREWARD_rev",1)
# AUC_HFHS_SECREWARD_rev_1=AUC_light_snipper("HFHS","SECREWARD_rev",1)

# AUC_RESULTS_PRIMREWARD_1=AUC_result_light_snipper("PRIMREWARD",1,graphtitle='AUC')
# AUC_RESULTS_PRIMREWARD_3=AUC_result_light_snipper("PRIMREWARD",3,graphtitle='AUC')
# AUC_RESULTS_PRIMREWARD_5=AUC_result_light_snipper("PRIMREWARD",5,graphtitle='AUC')
# AUC_RESULTS_SECREWARD_1=AUC_result_light_snipper("SECREWARD",1,graphtitle='AUC')
# AUC_RESULTS_SECREWARD_2=AUC_result_light_snipper("SECREWARD",2,graphtitle='AUC')
# AUC_RESULTS_SECREWARD_3=AUC_result_light_snipper("SECREWARD",3,graphtitle='AUC')
# AUC_RESULTS_DISREWARD_1=AUC_result_light_snipper("DISREWARD",1,graphtitle='AUC')
# AUC_RESULTS_PRIMREWARD_rev_1=AUC_result_light_snipper("PRIMREWARD_rev",1,graphtitle='AUC')
# AUC_RESULTS_PRIMREWARD_rev_3=AUC_result_light_snipper("PRIMREWARD_rev",3,graphtitle='AUC')
# AUC_RESULTS_SECREWARD_rev_1=AUC_result_light_snipper("SECREWARD_rev",1,graphtitle='AUC')

# ###################################################################################################
# ################## BEHAVIOR ########################################################
# ###################################################################################################

# # # Make dictionaries and/or graphs of the snips of behavior
# # # # Fill in the dataframe needed, the sniptime pre and post and a graphtitle (if wanted)
# # # -> some parameter could be changed, e.g. output could be set to output='zscore'
# # # dict_T_CAF_PRIM1=behavior_snipper(data_T,"CAF","PRIMREWARD",1, excluding_behaviors='include')
# # dict_B_CAF_PRIM1=behavior_snipper(data_B,"CAF","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_I_CAF_PRIM1=behavior_snipper(data_I,"CAF","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_A_CAF_PRIM1=behavior_snipper(data_A,"CAF","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_P_CAF_PRIM1=behavior_snipper(data_P,"CAF","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_R_CAF_PRIM1=behavior_snipper(data_R,"CAF","PRIMREWARD",1, excluding_behaviors='include')  

# # # dict_T_CTR_PRIM1=behavior_snipper(data_T,"CTR","PRIMREWARD",1, excluding_behaviors='include')
# # dict_B_CTR_PRIM1=behavior_snipper(data_B,"CTR","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_I_CTR_PRIM1=behavior_snipper(data_I,"CTR","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_A_CTR_PRIM1=behavior_snipper(data_A,"CTR","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_P_CTR_PRIM1=behavior_snipper(data_P,"CTR","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_R_CTR_PRIM1=behavior_snipper(data_R,"CTR","PRIMREWARD",1, excluding_behaviors='include')  

# # # dict_T_HFHS_PRIM1=behavior_snipper(data_T,"HFHS","PRIMREWARD",1, excluding_behaviors='include')
# # dict_B_HFHS_PRIM1=behavior_snipper(data_B,"HFHS","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_I_HFHS_PRIM1=behavior_snipper(data_I,"HFHS","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_A_HFHS_PRIM1=behavior_snipper(data_A,"HFHS","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_P_HFHS_PRIM1=behavior_snipper(data_P,"HFHS","PRIMREWARD",1, excluding_behaviors='include')  
# # dict_R_HFHS_PRIM1=behavior_snipper(data_R,"HFHS","PRIMREWARD",1, excluding_behaviors='include')  

# # # dict_T_CAF_PRIM3=behavior_snipper(data_T,"CAF","PRIMREWARD",3, excluding_behaviors='include')
# # dict_B_CAF_PRIM3=behavior_snipper(data_B,"CAF","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_I_CAF_PRIM3=behavior_snipper(data_I,"CAF","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_A_CAF_PRIM3=behavior_snipper(data_A,"CAF","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_P_CAF_PRIM3=behavior_snipper(data_P,"CAF","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_R_CAF_PRIM3=behavior_snipper(data_R,"CAF","PRIMREWARD",3, excluding_behaviors='include')  

# # # dict_T_CTR_PRIM3=behavior_snipper(data_T,"CTR","PRIMREWARD",3, excluding_behaviors='include')
# # dict_B_CTR_PRIM3=behavior_snipper(data_B,"CTR","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_I_CTR_PRIM3=behavior_snipper(data_I,"CTR","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_A_CTR_PRIM3=behavior_snipper(data_A,"CTR","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_P_CTR_PRIM3=behavior_snipper(data_P,"CTR","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_R_CTR_PRIM3=behavior_snipper(data_R,"CTR","PRIMREWARD",3, excluding_behaviors='include')  

# # # dict_T_HFHS_PRIM3=behavior_snipper(data_T,"HFHS","PRIMREWARD",3, excluding_behaviors='include')
# # dict_B_HFHS_PRIM3=behavior_snipper(data_B,"HFHS","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_I_HFHS_PRIM3=behavior_snipper(data_I,"HFHS","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_A_HFHS_PRIM3=behavior_snipper(data_A,"HFHS","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_P_HFHS_PRIM3=behavior_snipper(data_P,"HFHS","PRIMREWARD",3, excluding_behaviors='include')  
# # dict_R_HFHS_PRIM3=behavior_snipper(data_R,"HFHS","PRIMREWARD",3, excluding_behaviors='include')  

# # # dict_T_CAF_PRIM5=behavior_snipper(data_T,"CAF","PRIMREWARD",5, excluding_behaviors='include')
# # dict_B_CAF_PRIM5=behavior_snipper(data_B,"CAF","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_I_CAF_PRIM5=behavior_snipper(data_I,"CAF","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_A_CAF_PRIM5=behavior_snipper(data_A,"CAF","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_P_CAF_PRIM5=behavior_snipper(data_P,"CAF","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_R_CAF_PRIM5=behavior_snipper(data_R,"CAF","PRIMREWARD",5, excluding_behaviors='include')  

# # # # dict_T_CTR_PRIM5=behavior_snipper(data_T,"CTR","PRIMREWARD",5, excluding_behaviors='include')
# # dict_B_CTR_PRIM5=behavior_snipper(data_B,"CTR","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_I_CTR_PRIM5=behavior_snipper(data_I,"CTR","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_A_CTR_PRIM5=behavior_snipper(data_A,"CTR","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_P_CTR_PRIM5=behavior_snipper(data_P,"CTR","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_R_CTR_PRIM5=behavior_snipper(data_R,"CTR","PRIMREWARD",5, excluding_behaviors='include')  

# # # # dict_T_HFHS_PRIM5=behavior_snipper(data_T,"HFHS","PRIMREWARD",5, excluding_behaviors='include')
# # dict_B_HFHS_PRIM5=behavior_snipper(data_B,"HFHS","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_I_HFHS_PRIM5=behavior_snipper(data_I,"HFHS","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_A_HFHS_PRIM5=behavior_snipper(data_A,"HFHS","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_P_HFHS_PRIM5=behavior_snipper(data_P,"HFHS","PRIMREWARD",5, excluding_behaviors='include')  
# # dict_R_HFHS_PRIM5=behavior_snipper(data_R,"HFHS","PRIMREWARD",5, excluding_behaviors='include')  

# # # Secondary reward behavioral data
# # # dict_T_CAF_SEC1=behavior_snipper(data_T,"CAF","SECREWARD",1, excluding_behaviors='include')
# # dict_B_CAF_SEC1=behavior_snipper(data_B,"CAF","SECREWARD",1, excluding_behaviors='include')  
# # dict_I_CAF_SEC1=behavior_snipper(data_I,"CAF","SECREWARD",1, excluding_behaviors='include')  
# # dict_A_CAF_SEC1=behavior_snipper(data_A,"CAF","SECREWARD",1, excluding_behaviors='include')  
# # dict_P_CAF_SEC1=behavior_snipper(data_P,"CAF","SECREWARD",1, excluding_behaviors='include')  
# # dict_R_CAF_SEC1=behavior_snipper(data_R,"CAF","SECREWARD",1, excluding_behaviors='include')  

# # # dict_T_CTR_SEC1=behavior_snipper(data_T,"CTR","SECREWARD",1, excluding_behaviors='include')
# # dict_B_CTR_SEC1=behavior_snipper(data_B,"CTR","SECREWARD",1, excluding_behaviors='include')  
# # dict_I_CTR_SEC1=behavior_snipper(data_I,"CTR","SECREWARD",1, excluding_behaviors='include')  
# # dict_A_CTR_SEC1=behavior_snipper(data_A,"CTR","SECREWARD",1, excluding_behaviors='include')  
# # dict_P_CTR_SEC1=behavior_snipper(data_P,"CTR","SECREWARD",1, excluding_behaviors='include')  
# # dict_R_CTR_SEC1=behavior_snipper(data_R,"CTR","SECREWARD",1, excluding_behaviors='include')  

# # # dict_T_HFHS_SEC1=behavior_snipper(data_T,"HFHS","SECREWARD",1, excluding_behaviors='include')
# # dict_B_HFHS_SEC1=behavior_snipper(data_B,"HFHS","SECREWARD",1, excluding_behaviors='include')  
# # dict_I_HFHS_SEC1=behavior_snipper(data_I,"HFHS","SECREWARD",1, excluding_behaviors='include')  
# # dict_A_HFHS_SEC1=behavior_snipper(data_A,"HFHS","SECREWARD",1, excluding_behaviors='include')  
# # dict_P_HFHS_SEC1=behavior_snipper(data_P,"HFHS","SECREWARD",1, excluding_behaviors='include')  
# # dict_R_HFHS_SEC1=behavior_snipper(data_R,"HFHS","SECREWARD",1, excluding_behaviors='include')  

# # # dict_T_CAF_SEC2=behavior_snipper(data_T,"CAF","SECREWARD",2, excluding_behaviors='include')
# # dict_B_CAF_SEC2=behavior_snipper(data_B,"CAF","SECREWARD",2, excluding_behaviors='include')  
# # dict_I_CAF_SEC2=behavior_snipper(data_I,"CAF","SECREWARD",2, excluding_behaviors='include')  
# # dict_A_CAF_SEC2=behavior_snipper(data_A,"CAF","SECREWARD",2, excluding_behaviors='include')  
# # dict_P_CAF_SEC2=behavior_snipper(data_P,"CAF","SECREWARD",2, excluding_behaviors='include')  
# # dict_R_CAF_SEC2=behavior_snipper(data_R,"CAF","SECREWARD",2, excluding_behaviors='include')  

# # # dict_T_CTR_SEC2=behavior_snipper(data_T,"CTR","SECREWARD",2, excluding_behaviors='include')
# # dict_B_CTR_SEC2=behavior_snipper(data_B,"CTR","SECREWARD",2, excluding_behaviors='include')  
# # dict_I_CTR_SEC2=behavior_snipper(data_I,"CTR","SECREWARD",2, excluding_behaviors='include')  
# # dict_A_CTR_SEC2=behavior_snipper(data_A,"CTR","SECREWARD",2, excluding_behaviors='include')  
# # dict_P_CTR_SEC2=behavior_snipper(data_P,"CTR","SECREWARD",2, excluding_behaviors='include')  
# # dict_R_CTR_SEC2=behavior_snipper(data_R,"CTR","SECREWARD",2, excluding_behaviors='include')  

# # # dict_T_HFHS_SEC2=behavior_snipper(data_T,"HFHS","SECREWARD",2, excluding_behaviors='include')
# # dict_B_HFHS_SEC2=behavior_snipper(data_B,"HFHS","SECREWARD",2, excluding_behaviors='include')  
# # dict_I_HFHS_SEC2=behavior_snipper(data_I,"HFHS","SECREWARD",2, excluding_behaviors='include')  
# # dict_A_HFHS_SEC2=behavior_snipper(data_A,"HFHS","SECREWARD",2, excluding_behaviors='include')  
# # dict_P_HFHS_SEC2=behavior_snipper(data_P,"HFHS","SECREWARD",2, excluding_behaviors='include')  
# # dict_R_HFHS_SEC2=behavior_snipper(data_R,"HFHS","SECREWARD",2, excluding_behaviors='include')  

# # # dict_T_CAF_SEC3=behavior_snipper(data_T,"CAF","SECREWARD",3, excluding_behaviors='include')
# # dict_B_CAF_SEC3=behavior_snipper(data_B,"CAF","SECREWARD",3, excluding_behaviors='include')  
# # dict_I_CAF_SEC3=behavior_snipper(data_I,"CAF","SECREWARD",3, excluding_behaviors='include')  
# # dict_A_CAF_SEC3=behavior_snipper(data_A,"CAF","SECREWARD",3, excluding_behaviors='include')  
# # dict_P_CAF_SEC3=behavior_snipper(data_P,"CAF","SECREWARD",3, excluding_behaviors='include')  
# # dict_R_CAF_SEC3=behavior_snipper(data_R,"CAF","SECREWARD",3, excluding_behaviors='include')  

# # # dict_T_CTR_SEC3=behavior_snipper(data_T,"CTR","SECREWARD",3, excluding_behaviors='include')
# # dict_B_CTR_SEC3=behavior_snipper(data_B,"CTR","SECREWARD",3, excluding_behaviors='include')  
# # dict_I_CTR_SEC3=behavior_snipper(data_I,"CTR","SECREWARD",3, excluding_behaviors='include')  
# # dict_A_CTR_SEC3=behavior_snipper(data_A,"CTR","SECREWARD",3, excluding_behaviors='include')  
# # dict_P_CTR_SEC3=behavior_snipper(data_P,"CTR","SECREWARD",3, excluding_behaviors='include')  
# # dict_R_CTR_SEC3=behavior_snipper(data_R,"CTR","SECREWARD",3, excluding_behaviors='include')  

# # # dict_T_HFHS_SEC3=behavior_snipper(data_T,"HFHS","SECREWARD",3, excluding_behaviors='include')
# # dict_B_HFHS_SEC3=behavior_snipper(data_B,"HFHS","SECREWARD",3, excluding_behaviors='include')  
# # dict_I_HFHS_SEC3=behavior_snipper(data_I,"HFHS","SECREWARD",3, excluding_behaviors='include')  
# # dict_A_HFHS_SEC3=behavior_snipper(data_A,"HFHS","SECREWARD",3, excluding_behaviors='include')  
# # dict_P_HFHS_SEC3=behavior_snipper(data_P,"HFHS","SECREWARD",3, excluding_behaviors='include')  
# # dict_R_HFHS_SEC3=behavior_snipper(data_R,"HFHS","SECREWARD",3, excluding_behaviors='include')  

# # # Calculate behavior DISreward
# # # dict_T_CAF_DIS1=behavior_snipper(data_T,"CAF","DISREWARD",1, excluding_behaviors='include')
# # dict_B_CAF_DIS1=behavior_snipper(data_B,"CAF","DISREWARD",1, excluding_behaviors='include')  
# # dict_I_CAF_DIS1=behavior_snipper(data_I,"CAF","DISREWARD",1, excluding_behaviors='include')  
# # dict_A_CAF_DIS1=behavior_snipper(data_A,"CAF","DISREWARD",1, excluding_behaviors='include')  
# # dict_P_CAF_DIS1=behavior_snipper(data_P,"CAF","DISREWARD",1, excluding_behaviors='include')  
# # dict_R_CAF_DIS1=behavior_snipper(data_R,"CAF","DISREWARD",1, excluding_behaviors='include')  

# # # dict_T_CTR_DIS1=behavior_snipper(data_T,"CTR","DISREWARD",1, excluding_behaviors='include')
# # dict_B_CTR_DIS1=behavior_snipper(data_B,"CTR","DISREWARD",1, excluding_behaviors='include')  
# # dict_I_CTR_DIS1=behavior_snipper(data_I,"CTR","DISREWARD",1, excluding_behaviors='include')  
# # dict_A_CTR_DIS1=behavior_snipper(data_A,"CTR","DISREWARD",1, excluding_behaviors='include')  
# # dict_P_CTR_DIS1=behavior_snipper(data_P,"CTR","DISREWARD",1, excluding_behaviors='include')  
# # dict_R_CTR_DIS1=behavior_snipper(data_R,"CTR","DISREWARD",1, excluding_behaviors='include')  

# # # dict_T_HFHS_DIS1=behavior_snipper(data_T,"HFHS","DISREWARD",1, excluding_behaviors='include')
# # dict_B_HFHS_DIS1=behavior_snipper(data_B,"HFHS","DISREWARD",1, excluding_behaviors='include')  
# # dict_I_HFHS_DIS1=behavior_snipper(data_I,"HFHS","DISREWARD",1, excluding_behaviors='include')  
# # dict_A_HFHS_DIS1=behavior_snipper(data_A,"HFHS","DISREWARD",1, excluding_behaviors='include')  
# # dict_P_HFHS_DIS1=behavior_snipper(data_P,"HFHS","DISREWARD",1, excluding_behaviors='include')  
# # dict_R_HFHS_DIS1=behavior_snipper(data_R,"HFHS","DISREWARD",1, excluding_behaviors='include')  

# # # Calculate behavior PRIM_rev1
# # # dict_T_CAF_PRIM_rev1=behavior_snipper(data_T,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')
# # dict_B_CAF_PRIM_rev1=behavior_snipper(data_B,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_CAF_PRIM_rev1=behavior_snipper(data_I,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_CAF_PRIM_rev1=behavior_snipper(data_A,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_CAF_PRIM_rev1=behavior_snipper(data_P,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_CAF_PRIM_rev1=behavior_snipper(data_R,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')  

# # # dict_T_CTR_PRIM_rev1=behavior_snipper(data_T,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')
# # dict_B_CTR_PRIM_rev1=behavior_snipper(data_B,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_CTR_PRIM_rev1=behavior_snipper(data_I,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_CTR_PRIM_rev1=behavior_snipper(data_A,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_CTR_PRIM_rev1=behavior_snipper(data_P,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_CTR_PRIM_rev1=behavior_snipper(data_R,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')  

# # # dict_T_HFHS_PRIM_rev1=behavior_snipper(data_T,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')
# # dict_B_HFHS_PRIM_rev1=behavior_snipper(data_B,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_HFHS_PRIM_rev1=behavior_snipper(data_I,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_HFHS_PRIM_rev1=behavior_snipper(data_A,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_HFHS_PRIM_rev1=behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_HFHS_PRIM_rev1=behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')  

# # # dict_T_CAF_PRIM_rev3=behavior_snipper(data_T,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')
# # dict_B_CAF_PRIM_rev3=behavior_snipper(data_B,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_I_CAF_PRIM_rev3=behavior_snipper(data_I,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_A_CAF_PRIM_rev3=behavior_snipper(data_A,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_P_CAF_PRIM_rev3=behavior_snipper(data_P,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_R_CAF_PRIM_rev3=behavior_snipper(data_R,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')  

# # # dict_T_CTR_PRIM_rev3=behavior_snipper(data_T,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')
# # dict_B_CTR_PRIM_rev3=behavior_snipper(data_B,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_I_CTR_PRIM_rev3=behavior_snipper(data_I,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_A_CTR_PRIM_rev3=behavior_snipper(data_A,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_P_CTR_PRIM_rev3=behavior_snipper(data_P,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_R_CTR_PRIM_rev3=behavior_snipper(data_R,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')  

# # # dict_T_HFHS_PRIM_rev1=behavior_snipper(data_T,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')
# # dict_B_HFHS_PRIM_rev3=behavior_snipper(data_B,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_I_HFHS_PRIM_rev3=behavior_snipper(data_I,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_A_HFHS_PRIM_rev3=behavior_snipper(data_A,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_P_HFHS_PRIM_rev3=behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')  
# # dict_R_HFHS_PRIM_rev3=behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')  

# # # dict_T_CAF_SEC_rev1=behavior_snipper(data_T,"CAF","SECREWARD_rev",1, excluding_behaviors='include')
# # dict_B_CAF_SEC_rev1=behavior_snipper(data_B,"CAF","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_CAF_SEC_rev1=behavior_snipper(data_I,"CAF","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_CAF_SEC_rev1=behavior_snipper(data_A,"CAF","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_CAF_SEC_rev1=behavior_snipper(data_P,"CAF","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_CAF_SEC_rev1=behavior_snipper(data_R,"CAF","SECREWARD_rev",1, excluding_behaviors='include')  

# # # dict_T_CTR_SEC_rev1=behavior_snipper(data_T,"CTR","SECREWARD_rev",1, excluding_behaviors='include')
# # dict_B_CTR_SEC_rev1=behavior_snipper(data_B,"CTR","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_CTR_SEC_rev1=behavior_snipper(data_I,"CTR","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_CTR_SEC_rev1=behavior_snipper(data_A,"CTR","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_CTR_SEC_rev1=behavior_snipper(data_P,"CTR","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_CTR_SEC_rev1=behavior_snipper(data_R,"CTR","SECREWARD_rev",1, excluding_behaviors='include')  

# # # dict_T_HFHS_SEC_rev1=behavior_snipper(data_T,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')
# # dict_B_HFHS_SEC_rev1=behavior_snipper(data_B,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_I_HFHS_SEC_rev1=behavior_snipper(data_I,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_A_HFHS_SEC_rev1=behavior_snipper(data_A,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_P_HFHS_SEC_rev1=behavior_snipper(data_P,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')  
# # dict_R_HFHS_SEC_rev1=behavior_snipper(data_R,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')  

# ########################################################################################################################
# ########## MAKE MEANS OF RATS OF BEHAVIORAL SNIPPERS####################################################################
# ########################################################################################################################
# # Make dictionaries of GCAMP means of all rats and/or graphs
# # Fill in the dictionary linked to the dataset, the sniptime pre and post and a graphtitle (if wanted,output='zscore')
# # -> some parameter could be changed, e.g. output could be set to output='zscore'
# # result_T_CAF_PRIM1=result_snipper(data_T,"CAF","PRIMREWARD",1, excluding_behaviors='include')  
# result_B_CAF_PRIM1=result_snipper(data_B,"CAF","PRIMREWARD",1)#,graphtitle='B_incl ')  
# result_I_CAF_PRIM1=result_snipper(data_I,"CAF","PRIMREWARD",1)#,graphtitle='I_incl ')  
# result_A_CAF_PRIM1=result_snipper(data_A,"CAF","PRIMREWARD",1)#,graphtitle='A_incl ')  
# result_P_CAF_PRIM1=result_snipper(data_P,"CAF","PRIMREWARD",1)#,graphtitle='P_incl ')   
# result_R_CAF_PRIM1=result_snipper(data_R,"CAF","PRIMREWARD",1)#,graphtitle='R_incl ')   

# # result_T_CTR_PRIM1=result_snipper(data_T,"CTR","PRIMREWARD",1, excluding_behaviors='include')  
# result_B_CTR_PRIM1=result_snipper(data_B,"CTR","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_PRIM1=result_snipper(data_I,"CTR","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_PRIM1=result_snipper(data_A,"CTR","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_PRIM1=result_snipper(data_P,"CTR","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_PRIM1=result_snipper(data_R,"CTR","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_PRIM1=result_snipper(data_T,"HFHS","PRIMREWARD",1)#,graphtitle='B_incl ')   
# result_B_HFHS_PRIM1=result_snipper(data_B,"HFHS","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_PRIM1=result_snipper(data_I,"HFHS","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_PRIM1=result_snipper(data_A,"HFHS","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_PRIM1=result_snipper(data_P,"HFHS","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_PRIM1=result_snipper(data_R,"HFHS","PRIMREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_PRIM3=result_snipper(data_T,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_PRIM3=result_snipper(data_B,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_PRIM3=result_snipper(data_I,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_PRIM3=result_snipper(data_A,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_PRIM3=result_snipper(data_P,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_PRIM3=result_snipper(data_R,"CAF","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_PRIM3=result_snipper(data_T,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_PRIM3=result_snipper(data_B,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_PRIM3=result_snipper(data_I,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_PRIM3=result_snipper(data_A,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_PRIM3=result_snipper(data_P,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_PRIM3=result_snipper(data_R,"CTR","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_PRIM3=result_snipper(data_T,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_PRIM3=result_snipper(data_B,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_PRIM3=result_snipper(data_I,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_PRIM3=result_snipper(data_A,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_PRIM3=result_snipper(data_P,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_PRIM3=result_snipper(data_R,"HFHS","PRIMREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_PRIM5=result_snipper(data_T,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_PRIM5=result_snipper(data_B,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_PRIM5=result_snipper(data_I,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_PRIM5=result_snipper(data_A,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_PRIM5=result_snipper(data_P,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_PRIM5=result_snipper(data_R,"CAF","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_PRIM5=result_snipper(data_T,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_PRIM5=result_snipper(data_B,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_PRIM5=result_snipper(data_I,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_PRIM5=result_snipper(data_A,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_PRIM5=result_snipper(data_P,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_PRIM5=result_snipper(data_R,"CTR","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_PRIM5=result_snipper(data_T,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_PRIM5=result_snipper(data_B,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_PRIM5=result_snipper(data_I,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_PRIM5=result_snipper(data_A,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_PRIM5=result_snipper(data_P,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_PRIM5=result_snipper(data_R,"HFHS","PRIMREWARD",5, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_SEC1=result_snipper(data_T,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_SEC1=result_snipper(data_B,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_SEC1=result_snipper(data_I,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_SEC1=result_snipper(data_A,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_SEC1=result_snipper(data_P,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_SEC1=result_snipper(data_R,"CAF","SECREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_SEC1=result_snipper(data_T,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_SEC1=result_snipper(data_B,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_SEC1=result_snipper(data_I,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_SEC1=result_snipper(data_A,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_SEC1=result_snipper(data_P,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_SEC1=result_snipper(data_R,"CTR","SECREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_SEC1=result_snipper(data_T,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_SEC1=result_snipper(data_B,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_SEC1=result_snipper(data_I,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_SEC1=result_snipper(data_A,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_SEC1=result_snipper(data_P,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_SEC1=result_snipper(data_R,"HFHS","SECREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_SEC2=result_snipper(data_T,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_SEC2=result_snipper(data_B,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_SEC2=result_snipper(data_I,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_SEC2=result_snipper(data_A,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_SEC2=result_snipper(data_P,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_SEC2=result_snipper(data_R,"CAF","SECREWARD",2, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_SEC2=result_snipper(data_T,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_SEC2=result_snipper(data_B,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_SEC2=result_snipper(data_I,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_SEC2=result_snipper(data_A,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_SEC2=result_snipper(data_P,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_SEC2=result_snipper(data_R,"CTR","SECREWARD",2, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_SEC2=result_snipper(data_T,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_SEC2=result_snipper(data_B,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_SEC2=result_snipper(data_I,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_SEC2=result_snipper(data_A,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_SEC2=result_snipper(data_P,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_SEC2=result_snipper(data_R,"HFHS","SECREWARD",2, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_SEC3=result_snipper(data_T,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_SEC3=result_snipper(data_B,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_SEC3=result_snipper(data_I,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_SEC3=result_snipper(data_A,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_SEC3=result_snipper(data_P,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_SEC3=result_snipper(data_R,"CAF","SECREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_SEC3=result_snipper(data_T,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_SEC3=result_snipper(data_B,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_SEC3=result_snipper(data_I,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_SEC3=result_snipper(data_A,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_SEC3=result_snipper(data_P,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_SEC3=result_snipper(data_R,"CTR","SECREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_SEC3=result_snipper(data_T,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_SEC3=result_snipper(data_B,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_SEC3=result_snipper(data_I,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_SEC3=result_snipper(data_A,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_SEC3=result_snipper(data_P,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_SEC3=result_snipper(data_R,"HFHS","SECREWARD",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_PRIM_rev1=result_snipper(data_T,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_PRIM_rev1=result_snipper(data_B,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_PRIM_rev1=result_snipper(data_I,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_PRIM_rev1=result_snipper(data_A,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_PRIM_rev1=result_snipper(data_P,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_PRIM_rev1=result_snipper(data_R,"CAF","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_PRIM_rev1=result_snipper(data_T,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_PRIM_rev1=result_snipper(data_B,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_PRIM_rev1=result_snipper(data_I,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_PRIM_rev1=result_snipper(data_A,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_PRIM_rev1=result_snipper(data_P,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_PRIM_rev1=result_snipper(data_R,"CTR","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_PRIM_rev1=result_snipper(data_T,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_PRIM_rev1=result_snipper(data_B,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_PRIM_rev1=result_snipper(data_I,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_PRIM_rev1=result_snipper(data_A,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_PRIM_rev1=result_snipper(data_P,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_PRIM_rev1=result_snipper(data_R,"HFHS","PRIMREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_PRIM_rev3=result_snipper(data_T,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_PRIM_rev3=result_snipper(data_B,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_PRIM_rev3=result_snipper(data_I,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_PRIM_rev3=result_snipper(data_A,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_PRIM_rev3=result_snipper(data_P,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_PRIM_rev3=result_snipper(data_R,"CAF","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_PRIM_rev3=result_snipper(data_T,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_PRIM_rev3=result_snipper(data_B,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_PRIM_rev3=result_snipper(data_I,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_PRIM_rev3=result_snipper(data_A,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_PRIM_rev3=result_snipper(data_P,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_PRIM_rev3=result_snipper(data_R,"CTR","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_PRIM_rev3=result_snipper(data_T,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_PRIM_rev3=result_snipper(data_B,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_PRIM_rev3=result_snipper(data_I,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_PRIM_rev3=result_snipper(data_A,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_PRIM_rev3=result_snipper(data_P,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_PRIM_rev3=result_snipper(data_R,"HFHS","PRIMREWARD_rev",3, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_SEC_rev1=result_snipper(data_T,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_SEC_rev1=result_snipper(data_B,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_SEC_rev1=result_snipper(data_I,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_SEC_rev1=result_snipper(data_A,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_SEC_rev1=result_snipper(data_P,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_SEC_rev1=result_snipper(data_R,"CAF","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_SEC_rev1=result_snipper(data_T,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_SEC_rev1=result_snipper(data_B,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_SEC_rev1=result_snipper(data_I,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_SEC_rev1=result_snipper(data_A,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_SEC_rev1=result_snipper(data_P,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_SEC_rev1=result_snipper(data_R,"CTR","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_SEC_rev1=result_snipper(data_T,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_SEC_rev1=result_snipper(data_B,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_SEC_rev1=result_snipper(data_I,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_SEC_rev1=result_snipper(data_A,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_SEC_rev1=result_snipper(data_P,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_SEC_rev1=result_snipper(data_R,"HFHS","SECREWARD_rev",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CAF_DIS1=result_snipper(data_T,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CAF_DIS1=result_snipper(data_B,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CAF_DIS1=result_snipper(data_I,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CAF_DIS1=result_snipper(data_A,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CAF_DIS1=result_snipper(data_P,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CAF_DIS1=result_snipper(data_R,"CAF","DISREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_CTR_DIS1=result_snipper(data_T,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_CTR_DIS1=result_snipper(data_B,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_CTR_DIS1=result_snipper(data_I,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_CTR_DIS1=result_snipper(data_A,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_CTR_DIS1=result_snipper(data_P,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_CTR_DIS1=result_snipper(data_R,"CTR","DISREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# # result_T_HFHS_DIS1=result_snipper(data_T,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_B_HFHS_DIS1=result_snipper(data_B,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='B_incl ')   
# result_I_HFHS_DIS1=result_snipper(data_I,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='I_incl ')   
# result_A_HFHS_DIS1=result_snipper(data_A,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='A_incl ')   
# result_P_HFHS_DIS1=result_snipper(data_P,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='P_incl ')   
# result_R_HFHS_DIS1=result_snipper(data_R,"HFHS","DISREWARD",1, excluding_behaviors='include')#,graphtitle='R_incl ')   

# #################GFP##################
# # # # # Fill in the dictionary linked to the dataset, the sniptime pre and post and a graphtitle (if wanted)
# # -> some parameter could be changed, e.g. output could be set to output='zscore'
# result_T_GFP_PRIM1=result_snipper_GFP(data_T,"PRIMREWARD",1, excluding_behaviors='include')  
# result_B_GFP_PRIM1=result_snipper_GFP(data_B,"PRIMREWARD",1, excluding_behaviors='include')  
# result_I_GFP_PRIM1=result_snipper_GFP(data_I,"PRIMREWARD",1, excluding_behaviors='include')  
# result_A_GFP_PRIM1=result_snipper_GFP(data_A,"PRIMREWARD",1, excluding_behaviors='include')  
# result_P_GFP_PRIM1=result_snipper_GFP(data_P,"PRIMREWARD",1, excluding_behaviors='include')  
# result_R_GFP_PRIM1=result_snipper_GFP(data_R,"PRIMREWARD",1, excluding_behaviors='include')  

# result_T_GFP_PRIM3=result_snipper_GFP(data_T,"PRIMREWARD",3, excluding_behaviors='include')  
# result_B_GFP_PRIM3=result_snipper_GFP(data_B,"PRIMREWARD",3, excluding_behaviors='include')  
# result_I_GFP_PRIM3=result_snipper_GFP(data_I,"PRIMREWARD",3, excluding_behaviors='include')  
# result_A_GFP_PRIM3=result_snipper_GFP(data_A,"PRIMREWARD",3, excluding_behaviors='include')  
# result_P_GFP_PRIM3=result_snipper_GFP(data_P,"PRIMREWARD",3, excluding_behaviors='include')  
# result_R_GFP_PRIM3=result_snipper_GFP(data_R,"PRIMREWARD",3, excluding_behaviors='include')  

# result_T_GFP_PRIM5=result_snipper_GFP(data_T,"PRIMREWARD",5, excluding_behaviors='include')  
# result_B_GFP_PRIM5=result_snipper_GFP(data_B,"PRIMREWARD",5, excluding_behaviors='include')  
# result_I_GFP_PRIM5=result_snipper_GFP(data_I,"PRIMREWARD",5, excluding_behaviors='include')  
# result_A_GFP_PRIM5=result_snipper_GFP(data_A,"PRIMREWARD",5, excluding_behaviors='include')  
# result_P_GFP_PRIM5=result_snipper_GFP(data_P,"PRIMREWARD",5, excluding_behaviors='include')  
# result_R_GFP_PRIM5=result_snipper_GFP(data_R,"PRIMREWARD",5, excluding_behaviors='include')  

# result_T_GFP_SEC1=result_snipper_GFP(data_T,"SECREWARD",1, excluding_behaviors='include')  
# result_B_GFP_SEC1=result_snipper_GFP(data_B,"SECREWARD",1, excluding_behaviors='include')  
# result_I_GFP_SEC1=result_snipper_GFP(data_I,"SECREWARD",1, excluding_behaviors='include')  
# result_A_GFP_SEC1=result_snipper_GFP(data_A,"SECREWARD",1, excluding_behaviors='include')  
# result_P_GFP_SEC1=result_snipper_GFP(data_P,"SECREWARD",1, excluding_behaviors='include')  
# result_R_GFP_SEC1=result_snipper_GFP(data_R,"SECREWARD",1, excluding_behaviors='include')  

# result_T_GFP_SEC2=result_snipper_GFP(data_T,"SECREWARD",2, excluding_behaviors='include')  
# result_B_GFP_SEC2=result_snipper_GFP(data_B,"SECREWARD",2, excluding_behaviors='include')  
# result_I_GFP_SEC2=result_snipper_GFP(data_I,"SECREWARD",2, excluding_behaviors='include')  
# result_A_GFP_SEC2=result_snipper_GFP(data_A,"SECREWARD",2, excluding_behaviors='include')  
# result_P_GFP_SEC2=result_snipper_GFP(data_P,"SECREWARD",2, excluding_behaviors='include')  
# result_R_GFP_SEC2=result_snipper_GFP(data_R,"SECREWARD",2, excluding_behaviors='include')  

# result_T_GFP_SEC3=result_snipper_GFP(data_T,"SECREWARD",3, excluding_behaviors='include')  
# result_B_GFP_SEC3=result_snipper_GFP(data_B,"SECREWARD",3, excluding_behaviors='include')  
# result_I_GFP_SEC3=result_snipper_GFP(data_I,"SECREWARD",3, excluding_behaviors='include')  
# result_A_GFP_SEC3=result_snipper_GFP(data_A,"SECREWARD",3, excluding_behaviors='include')  
# result_P_GFP_SEC3=result_snipper_GFP(data_P,"SECREWARD",3, excluding_behaviors='include')  
# result_R_GFP_SEC3=result_snipper_GFP(data_R,"SECREWARD",3, excluding_behaviors='include')  

# result_B_GFP_DIS1=result_snipper_GFP(data_B,"DISREWARD",1, excluding_behaviors='include')  
# result_I_GFP_DIS1=result_snipper_GFP(data_I,"DISREWARD",1, excluding_behaviors='include')  
# result_A_GFP_DIS1=result_snipper_GFP(data_A,"DISREWARD",1, excluding_behaviors='include')  
# result_P_GFP_DIS1=result_snipper_GFP(data_P,"DISREWARD",1, excluding_behaviors='include')  
# result_R_GFP_DIS1=result_snipper_GFP(data_R,"DISREWARD",1, excluding_behaviors='include')  

# result_B_GFP_PRIM_rev1=result_snipper_GFP(data_B,"PRIMREWARD_rev",1, excluding_behaviors='include')  
# result_I_GFP_PRIM_rev1=result_snipper_GFP(data_I,"PRIMREWARD_rev",1, excluding_behaviors='include')  
# result_A_GFP_PRIM_rev1=result_snipper_GFP(data_A,"PRIMREWARD_rev",1, excluding_behaviors='include')  
# result_P_GFP_PRIM_rev1=result_snipper_GFP(data_P,"PRIMREWARD_rev",1, excluding_behaviors='include')  
# result_R_GFP_PRIM_rev1=result_snipper_GFP(data_R,"PRIMREWARD_rev",1, excluding_behaviors='include')  

# result_B_GFP_PRIM_rev3=result_snipper_GFP(data_B,"PRIMREWARD_rev",3, excluding_behaviors='include')  
# result_I_GFP_PRIM_rev3=result_snipper_GFP(data_I,"PRIMREWARD_rev",3, excluding_behaviors='include')  
# result_A_GFP_PRIM_rev3=result_snipper_GFP(data_A,"PRIMREWARD_rev",3, excluding_behaviors='include')  
# result_P_GFP_PRIM_rev3=result_snipper_GFP(data_P,"PRIMREWARD_rev",3, excluding_behaviors='include')  
# result_R_GFP_PRIM_rev3=result_snipper_GFP(data_R,"PRIMREWARD_rev",3, excluding_behaviors='include')  

# result_B_GFP_SEC_rev1=result_snipper_GFP(data_B,"SECREWARD_rev",1, excluding_behaviors='include')  
# result_I_GFP_SEC_rev1=result_snipper_GFP(data_I,"SECREWARD_rev",1, excluding_behaviors='include')  
# result_A_GFP_SEC_rev1=result_snipper_GFP(data_A,"SECREWARD_rev",1, excluding_behaviors='include')  
# result_P_GFP_SEC_rev1=result_snipper_GFP(data_P,"SECREWARD_rev",1, excluding_behaviors='include')  
# result_R_GFP_SEC_rev1=result_snipper_GFP(data_R,"SECREWARD_rev",1, excluding_behaviors='include')  

# ###################################
# # Compare the different treatment groups per behavior
# # -> some parameter could be changed, e.g. output could be set to output='zscore'
# PRIMREW1_R= compare_behavior_snipper(result_R_CTR_PRIM1,result_R_HFHS_PRIM1,result_R_CAF_PRIM1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW1_incl")#"1st primary reward")
# PRIMREW3_R= compare_behavior_snipper(result_R_CTR_PRIM3,result_R_HFHS_PRIM3,result_R_CAF_PRIM3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW3_incl")#"3rd primary reward")
# PRIMREW5_R= compare_behavior_snipper(result_R_CTR_PRIM5,result_R_HFHS_PRIM5,result_R_CAF_PRIM5,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW5_incl")#"5th primary reward")
# SECREW1_R= compare_behavior_snipper(result_R_CTR_SEC1,result_R_HFHS_SEC1,result_R_CAF_SEC1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW1_incl")#"1st secondary reward")
# SECREW2_R= compare_behavior_snipper(result_R_CTR_SEC2,result_R_HFHS_SEC2,result_R_CAF_SEC2,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW2_incl")#"2nd secondary reward")
# SECREW3_R= compare_behavior_snipper(result_R_CTR_SEC3,result_R_HFHS_SEC3,result_R_CAF_SEC3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_SECREW3_incl")#"3rd secondary reward")
# DISREW1_R= compare_behavior_snipper(result_R_CTR_DIS1,result_R_HFHS_DIS1,result_R_CAF_DIS1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_STDCHOW_incl")#"standard chow")
# PRIMREW_rev1_R= compare_behavior_snipper(result_R_CTR_PRIM_rev1,result_R_HFHS_PRIM_rev1,result_R_CAF_PRIM_rev1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW1_incl")#"1st primary reward after reversal")
# PRIMREW_rev3_R= compare_behavior_snipper(result_R_CTR_PRIM_rev3,result_R_HFHS_PRIM_rev3,result_R_CAF_PRIM_rev3,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW3_incl")#"3rd primary reward after reversal")
# SECREW_rev1_R= compare_behavior_snipper(result_R_CTR_SEC_rev1,result_R_HFHS_SEC_rev1,result_R_CAF_SEC_rev1,"CTR","HFHS","CAF",list_interest_beh_reward,graphtitle="R_revSECREW1_incl")#"1st secondary reward after reversal")

# PRIMREW1_P= compare_behavior_snipper(result_P_CTR_PRIM1,result_P_HFHS_PRIM1,result_P_CAF_PRIM1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW1_incl")#"1st primary (pre)reward")
# PRIMREW3_P= compare_behavior_snipper(result_P_CTR_PRIM3,result_P_HFHS_PRIM3,result_P_CAF_PRIM3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW3_incl")#"3rd primary (pre)reward")
# PRIMREW5_P= compare_behavior_snipper(result_P_CTR_PRIM5,result_P_HFHS_PRIM5,result_P_CAF_PRIM5,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW5_incl")#"5th primary (pre)reward")
# SECREW1_P= compare_behavior_snipper(result_P_CTR_SEC1,result_P_HFHS_SEC1,result_P_CAF_SEC1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW1_incl")#"1st secondary (pre)reward")
# SECREW2_P= compare_behavior_snipper(result_P_CTR_SEC2,result_P_HFHS_SEC2,result_P_CAF_SEC2,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW2_incl")#"2nd secondary (pre)reward")
# SECREW3_P= compare_behavior_snipper(result_P_CTR_SEC3,result_P_HFHS_SEC3,result_P_CAF_SEC3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_SECREW3_incl")#"3rd secondary (pre)reward")
# DISREW1_P= compare_behavior_snipper(result_P_CTR_DIS1,result_P_HFHS_DIS1,result_P_CAF_DIS1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_STDCHOW_incl")#"standard chow (pre)")
# PRIMREW_rev1_P= compare_behavior_snipper(result_P_CTR_PRIM_rev1,result_P_HFHS_PRIM_rev1,result_P_CAF_PRIM_rev1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_incl")#"1st primary (pre)reward after reversal")
# PRIMREW_rev3_P= compare_behavior_snipper(result_P_CTR_PRIM_rev3,result_P_HFHS_PRIM_rev3,result_P_CAF_PRIM_rev3,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_incl")#"3rd primary (pre)reward after reversal")
# SECREW_rev1_P= compare_behavior_snipper(result_P_CTR_SEC_rev1,result_P_HFHS_SEC_rev1,result_P_CAF_SEC_rev1,"CTR","HFHS","CAF",list_interest_beh_prereward,graphtitle="P_revSECREW1_incl")#"1st secondary (pre)reward after reversal")

# # Compare the different treatment groups per behavior for only CAF and CTR
# PRIMREW1_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_PRIM1,result_R_CAF_PRIM1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW1_incl")#"1st primary reward")
# PRIMREW3_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_PRIM3,result_R_CAF_PRIM3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW3_incl")#"3rd primary reward")
# PRIMREW5_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_PRIM5,result_R_CAF_PRIM5,"CTR","CAF",list_interest_beh_reward,graphtitle="R_PRIMREW5_incl")#"5th primary reward")
# SECREW1_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_SEC1,result_R_CAF_SEC1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW1_incl")#"1st secondary reward")
# SECREW2_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_SEC2,result_R_CAF_SEC2,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW2_incl")#"2nd secondary reward")
# SECREW3_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_SEC3,result_R_CAF_SEC3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_SECREW3_incl")#"3rd secondary reward")
# DISREW1_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_DIS1,result_R_CAF_DIS1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_STDCHOW_incl")#"standard chow")
# PRIMREW_rev1_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_PRIM_rev1,result_R_CAF_PRIM_rev1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW1_incl")#"1st primary reward after reversal")
# PRIMREW_rev3_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_PRIM_rev3,result_R_CAF_PRIM_rev3,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revPRIMREW3_incl")#"3rd primary reward after reversal")
# SECREW_rev1_R_CAF= compare_behavior_snipper_CAF(result_R_CTR_SEC_rev1,result_R_CAF_SEC_rev1,"CTR","CAF",list_interest_beh_reward,graphtitle="R_revSECREW1_incl")#"1st secondary reward after reversal")

# PRIMREW1_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_PRIM1,result_P_CAF_PRIM1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW1_incl")#"1st primary (pre)reward")
# PRIMREW3_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_PRIM3,result_P_CAF_PRIM3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW3_incl")#"3rd primary (pre)reward")
# PRIMREW5_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_PRIM5,result_P_CAF_PRIM5,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_PRIMREW5_incl")#"5th primary (pre)reward")
# SECREW1_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_SEC1,result_P_CAF_SEC1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW1_incl")#"1st secondary (pre)reward")
# SECREW2_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_SEC2,result_P_CAF_SEC2,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW2_incl")#"2nd secondary (pre)reward")
# SECREW3_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_SEC3,result_P_CAF_SEC3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_SECREW3_incl")#"3rd secondary (pre)reward")
# DISREW1_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_DIS1,result_P_CAF_DIS1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_STDCHOW_incl")#"standard chow (pre)")
# PRIMREW_rev1_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_PRIM_rev1,result_P_CAF_PRIM_rev1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_incl")#"1st primary (pre)reward after reversal")
# PRIMREW_rev3_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_PRIM_rev3,result_P_CAF_PRIM_rev3,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_incl")#"3rd primary (pre)reward after reversal")
# SECREW_rev1_P_CAF= compare_behavior_snipper_CAF(result_P_CTR_SEC_rev1,result_P_CAF_SEC_rev1,"CTR","CAF",list_interest_beh_prereward,graphtitle="P_revSECREW1_incl")#"1st secondary (pre)reward after reversal")

# # Compare the different treatment groups per behavior with GFP
# # -> some parameter could be changed, e.g. output could be set to output='zscore'
# PRIMREW1_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_PRIM1,result_R_HFHS_PRIM1,result_R_CAF_PRIM1,result_R_GFP_PRIM1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW1_incl")#"1st primary reward")
# PRIMREW3_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_PRIM3,result_R_HFHS_PRIM3,result_R_CAF_PRIM3,result_R_GFP_PRIM3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW3_incl")#"3rd primary reward")
# PRIMREW5_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_PRIM5,result_R_HFHS_PRIM5,result_R_CAF_PRIM5,result_R_GFP_PRIM5,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_PRIMREW5_incl")#"5th primary reward")
# SECREW1_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_SEC1,result_R_HFHS_SEC1,result_R_CAF_SEC1,result_R_GFP_SEC1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW1_incl")#"1st secondary reward")
# SECREW2_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_SEC2,result_R_HFHS_SEC2,result_R_CAF_SEC2,result_R_GFP_SEC2,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW2_incl")#"1st secondary reward")
# SECREW3_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_SEC3,result_R_HFHS_SEC3,result_R_CAF_SEC3,result_R_GFP_SEC3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_SECREW3_incl")#"1st secondary reward")
# DISREW1_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_DIS1,result_R_HFHS_DIS1,result_R_CAF_DIS1,result_R_GFP_DIS1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_STDCHOW_incl")#"standard chow")
# PRIMREW_rev1_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_PRIM_rev1,result_R_HFHS_PRIM_rev1,result_R_CAF_PRIM_rev1,result_R_GFP_PRIM_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revPRIMREW1_incl")#"1st primary reward after reversal")
# PRIMREW_rev3_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_PRIM_rev3,result_R_HFHS_PRIM_rev3,result_R_CAF_PRIM_rev3,result_R_GFP_PRIM_rev3,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revPRIMREW3_incl")#"3rd primary reward after reversal")
# SECREW_rev1_R_GFP= compare_behavior_snipper_plusGFP(result_R_CTR_SEC_rev1,result_R_HFHS_SEC_rev1,result_R_CAF_SEC_rev1,result_R_GFP_SEC_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_reward,graphtitle="R_revSECREW1_incl")#"1st secondary reward after reversal")

# PRIMREW1_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_PRIM1,result_P_HFHS_PRIM1,result_P_CAF_PRIM1,result_P_GFP_PRIM1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_incl")#"1st primary (pre)reward")
# PRIMREW3_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_PRIM3,result_P_HFHS_PRIM3,result_P_CAF_PRIM3,result_P_GFP_PRIM3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_incl")#"3rd primary (pre)reward")
# PRIMREW5_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_PRIM5,result_P_HFHS_PRIM5,result_P_CAF_PRIM5,result_P_GFP_PRIM5,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_PRIMREW1_incl")#"5th primary (pre)reward")
# SECREW1_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_SEC1,result_P_HFHS_SEC1,result_P_CAF_SEC1,result_P_GFP_SEC1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_incl")#"1st secondary (pre)reward")
# SECREW2_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_SEC2,result_P_HFHS_SEC2,result_P_CAF_SEC2,result_P_GFP_SEC2,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_incl")#"1st secondary (pre)reward")
# SECREW3_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_SEC3,result_P_HFHS_SEC3,result_P_CAF_SEC3,result_P_GFP_SEC3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_SECREW1_incl")#"1st secondary (pre)reward")
# DISREW1_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_DIS1,result_P_HFHS_DIS1,result_P_CAF_DIS1,result_P_GFP_DIS1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_STDCHOW_incl")#"standard chow (pre)")
# PRIMREW_rev1_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_PRIM_rev1,result_P_HFHS_PRIM_rev1,result_P_CAF_PRIM_rev1,result_P_GFP_PRIM_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revPRIMREW1_incl")#"1st primary (pre)reward after reversal")
# PRIMREW_rev3_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_PRIM_rev3,result_P_HFHS_PRIM_rev3,result_P_CAF_PRIM_rev3,result_P_GFP_PRIM_rev3,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revPRIMREW3_incl")#"3rd primary (pre)reward after reversal")
# SECREW_rev1_P_GFP= compare_behavior_snipper_plusGFP(result_P_CTR_SEC_rev1,result_P_HFHS_SEC_rev1,result_P_CAF_SEC_rev1,result_P_GFP_SEC_rev1,"CTR","HFHS","CAF","GFP",list_interest_beh_prereward,graphtitle="P_revSECREW1_incl")#"1st secondary (pre)reward after reversal")                          'Mount (received)','Paracopulatory','Rejection','Selfgrooming','Sniffing reward']


# ###################################################################################################
# ################## AUC GRAPHS WITH INCLUDED BEHAVIORS!!!  ########################################################
# ###################################################################################################


# # AUC behavior snipper
# AUC_CAF_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",1,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",1,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",3,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",3,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD3_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",3,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD",5,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD",5,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD5_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD",5,excluding_behaviors='include')  

# AUC_CAF_SECREWARD1_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",1,excluding_behaviors='include')  
# AUC_CTR_SECREWARD1_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",1,excluding_behaviors='include')  

# AUC_CAF_SECREWARD2_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",2,excluding_behaviors='include')  
# AUC_CTR_SECREWARD2_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",2,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD2_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",2,excluding_behaviors='include')  

# AUC_CAF_SECREWARD3_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD",3,excluding_behaviors='include')  
# AUC_CTR_SECREWARD3_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD",3,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD3_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD",3,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD_rev",1,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD_rev",1,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD_rev1_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",1,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"CAF","PRIMREWARD_rev",3,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"CTR","PRIMREWARD_rev",3,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD_rev3_R=AUC_behavior_snipper(data_R,"HFHS","PRIMREWARD_rev",3,excluding_behaviors='include')  

# AUC_CAF_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"CAF","SECREWARD_rev",1,excluding_behaviors='include')  
# AUC_CTR_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"CTR","SECREWARD_rev",1,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD_rev1_R=AUC_behavior_snipper(data_R,"HFHS","SECREWARD_rev",1,excluding_behaviors='include')  

# AUC_CAF_DISREWARD1_R=AUC_behavior_snipper(data_R,"CAF","DISREWARD",1,excluding_behaviors='include')  
# AUC_CTR_DISREWARD1_R=AUC_behavior_snipper(data_R,"CTR","DISREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_DISREWARD1_R=AUC_behavior_snipper(data_R,"HFHS","DISREWARD",1,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",1,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",1,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",3,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",3,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD3_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",3,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD",5,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD",5,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD5_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD",5,excluding_behaviors='include')  

# AUC_CAF_SECREWARD1_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",1,excluding_behaviors='include')  
# AUC_CTR_SECREWARD1_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",1,excluding_behaviors='include')  

# AUC_CAF_SECREWARD2_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",2,excluding_behaviors='include')  
# AUC_CTR_SECREWARD2_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",2,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD2_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",2,excluding_behaviors='include')  

# AUC_CAF_SECREWARD3_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD",3,excluding_behaviors='include')  
# AUC_CTR_SECREWARD3_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD",3,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD3_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD",3,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD_rev",1,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD_rev",1,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD_rev1_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",1,excluding_behaviors='include')  

# AUC_CAF_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"CAF","PRIMREWARD_rev",3,excluding_behaviors='include')  
# AUC_CTR_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"CTR","PRIMREWARD_rev",3,excluding_behaviors='include')  
# AUC_HFHS_PRIMREWARD_rev3_P=AUC_behavior_snipper(data_P,"HFHS","PRIMREWARD_rev",3,excluding_behaviors='include')  

# AUC_CAF_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"CAF","SECREWARD_rev",1,excluding_behaviors='include')  
# AUC_CTR_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"CTR","SECREWARD_rev",1,excluding_behaviors='include')  
# AUC_HFHS_SECREWARD_rev1_P=AUC_behavior_snipper(data_P,"HFHS","SECREWARD_rev",1,excluding_behaviors='include')  

# AUC_CAF_DISREWARD1_P=AUC_behavior_snipper(data_P,"CAF","DISREWARD",1,excluding_behaviors='include')  
# AUC_CTR_DISREWARD1_P=AUC_behavior_snipper(data_P,"CTR","DISREWARD",1,excluding_behaviors='include')  
# AUC_HFHS_DISREWARD1_P=AUC_behavior_snipper(data_P,"HFHS","DISREWARD",1,excluding_behaviors='include')  


# Make a definition for the mean behavior snips per rat
def AUC_result_behavior_snipper (test,testsession,phase, beh_list=list_beh_tdt_plus,
                                  sniptime=2, exclude_outliers=False, graphtitle=None):
    """
    NOTE ->     If you get an error, check the dictionary used for fs

    Parameters
    ----------
    test : string
        Add what type of behavioral test you want to analyze
        e.g. "PRIMREWARD", "SECREWARD"
    testsession : float
        Add which test number you want to analyze
        e.g. 1 for PRIMREWARD1, 2 for PRIMREWARD2
    phase : string
        Add the phase of the reward test
        e.g. "R","T","B","I","A","P"
    beh_list : list -> Default = list_beh_tdt
        Add the list with behaviors that need to be analyzed -> Default is list_beh_tdt
        e.g. list_beh_tdt,list_sex, list_behaviors, list_startcop, list_other_behaviors, list_behaviors_extra,
    sniptime : integer
        Add the number of seconds you want the snip to start before and after the event-> Default = 2
    exclude_outliers : boolean -> Default = False
        Add whether or not the dFF/zscore need to be corrected by taking out outliers in signals (e.g. when fiber needs to be re-adjusted)
        False = no corrections, True = corrections
    graphtitle : string
        Add the name of the figure. -> Default = None
    Returns
    -------
    dict_AUC_means
    Dictionary of the mean of AUC of mean signals of the dFF signals for the period of determined 
    snips around behaviors.
    Graphs of the mean signals of the AUC for the period of determined snips around behaviors per rat 
    and combines rats in one figure.
    """
    print("Start AUC_result_behavior_snipper")

    # set directory for figures
    if exclude_outliers==False:
        directory_graph=directory_results
    else:
        directory_graph=directory_results_cor

    if exclude_outliers==False:
        dict_AUC_CTR="AUC_CTR_"+str(test)+str(testsession)+"_"+str(phase)   
        dict_AUC_HFHS="AUC_HFHS_"+str(test)+str(testsession)+"_"+str(phase) 
        dict_AUC_CAF="AUC_CAF_"+str(test)+str(testsession)+"_"+str(phase) 
    else:
        dict_AUC_CTR="AUC_CTR_COR_"+str(test)+str(testsession)+"_"+str(phase)   
        dict_AUC_HFHS="AUC_HFHS_COR_"+str(test)+str(testsession)+"_"+str(phase) 
        dict_AUC_CAF="AUC_CAF_COR_"+str(test)+str(testsession)+"_"+str(phase) 
        

    dictionary_CTR= eval(dict_AUC_CTR)
    dictionary_CAF= eval(dict_AUC_CAF)
    dictionary_HFHS= eval(dict_AUC_HFHS)
    
    dict_AUC_CTR
    dict_AUC_HFHS
    dict_AUC_CAF

    list_diet=['CTR','HFHS','CAF']
    list_AUC=['AUC_pre','AUC_post']
    
    dict_AUC_means={}
    dict_AUC_ratmeans={}
    for d in list_diet:
        dict_AUC_means[d]={}
        dict_AUC_ratmeans[d]={}

        for moment in list_AUC:
            dict_AUC_means[d][moment]={}
            dict_AUC_ratmeans[d][moment]={}

            for moments,behaviors in dictionary_CTR.items():
                for beh,ids in behaviors.items():
                    dict_AUC_ratmeans[d][moment][beh]=[]
                    dict_AUC_means[d][moment][beh]=[]
    
    # Fill dictionary
    for moment,behavior in dictionary_CTR.items():
        if moment == 'AUC_pre':
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['CTR']['AUC_pre'][beh]=list_value
                dict_AUC_ratmeans['CTR']['AUC_pre'][beh]=np.nanmean(list_value)
        else:
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['CTR']['AUC_post'][beh]=list_value
                dict_AUC_ratmeans['CTR']['AUC_post'][beh]=np.nanmean(list_value)

    for moment,behavior in dictionary_HFHS.items():
        if moment == 'AUC_pre':
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['HFHS']['AUC_pre'][beh]=list_value
                dict_AUC_ratmeans['HFHS']['AUC_pre'][beh]=np.nanmean(list_value)
        else:
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['HFHS']['AUC_post'][beh]=list_value
                dict_AUC_ratmeans['HFHS']['AUC_post'][beh]=np.nanmean(list_value)

    for moment,behavior in dictionary_CAF.items():
        if moment == 'AUC_pre':
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['CAF']['AUC_pre'][beh]=list_value
                dict_AUC_ratmeans['CAF']['AUC_pre'][beh]=np.nanmean(list_value)
        else:
            for beh,values in behavior.items():
                list_value=[]
                for rat, value in values.items():
                    for v in value:
                        list_value.append(v)
                dict_AUC_means['CAF']['AUC_post'][beh]=list_value
                dict_AUC_ratmeans['CAF']['AUC_post'][beh]=np.nanmean(list_value)


    # Make a barplot
    if graphtitle == None:
        pass
    else:
        if not os.path.isdir(directory_graph+directory_TDT_behavior_AUC):
            os.mkdir(directory_graph+directory_TDT_behavior_AUC)
        if not os.path.isdir(directory_graph+directory_TDT_behavior_AUC+"/%s"%phase):
            os.mkdir(directory_graph+directory_TDT_behavior_AUC+"/%s"%phase)
        os.chdir(directory_graph+directory_TDT_behavior_AUC+"/%s"%phase)
        
        for moments,behaviors in dictionary_CTR.items():
            for beh,ids in behaviors.items():
                

                # Plot the data in bar charts with individual datapoints
                # Set position of bar on X axis - MAKE SURE IT MATCHES YOUR NUMBER OF GROUPS
                # set width of bar
                # sns.set(style="ticks", rc=custom_params)
                barWidth = 0.8
                x1 = ['Pre']
                x3 = ['Post']
        
                x_scatter1=len(dict_AUC_means['CTR']['AUC_pre'][beh])
                x_scatter2=len(dict_AUC_means['HFHS']['AUC_pre'][beh])
                x_scatter3=len(dict_AUC_means['CAF']['AUC_pre'][beh])
                yy= [-20,-15,-10,-5,0,5,10,15,20] 
                fig, axs = plt.subplots(1,3, figsize=(6,4), sharex=True, sharey=True)#, constrained_layout = True)
        
                axs[0].bar(x1, dict_AUC_ratmeans['CTR']['AUC_pre'][beh], color=color_AUC_CTR_pre, width=barWidth, edgecolor='white', label='Pre',zorder=2)
                axs[0].scatter(x_scatter1*x1, dict_AUC_means['CTR']['AUC_pre'][beh], color=color_AUC_CTR_pre_scatter, alpha=.9,zorder=3)
                axs[0].bar(x3, dict_AUC_ratmeans['CTR']['AUC_post'][beh], color=color_AUC_CTR_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
                axs[0].scatter(x_scatter1*x3, dict_AUC_means['CTR']['AUC_post'][beh],color=color_AUC_CTR_post_scatter,  alpha=.9,zorder=3)
                axs[0].set_title('CTR')
                axs[0].set_ylabel('AUC')
                # axs[0].set_yticks(yy)
                # Plotting the zero line
                axs[0].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)
        
                axs[1].bar(x1, dict_AUC_ratmeans['HFHS']['AUC_pre'][beh], color=color_AUC_HFHS_pre , width=barWidth, edgecolor='white', label='Pre',zorder=2)
                axs[1].scatter(x_scatter2*x1, dict_AUC_means['HFHS']['AUC_pre'][beh],color=color_AUC_HFHS_pre_scatter, alpha=.9,zorder=3)
                axs[1].bar(x3, dict_AUC_ratmeans['HFHS']['AUC_post'][beh], color=color_AUC_HFHS_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
                axs[1].scatter(x_scatter2*x3, dict_AUC_means['HFHS']['AUC_post'][beh], color=color_AUC_HFHS_post_scatter,alpha=.9,zorder=3)
                axs[1].set_title('HFHS')
                # axs[1].set_yticks(yy)
                axs[1].spines['left'].set_visible(False)                
                axs[1].tick_params(left=False)              
                axs[1].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)
               
                axs[2].bar(x1, dict_AUC_ratmeans['CAF']['AUC_pre'][beh], color=color_AUC_CAF_pre, width=barWidth, edgecolor='white', label='Pre',zorder=2)
                axs[2].scatter(x_scatter3*x1, dict_AUC_means['CAF']['AUC_pre'][beh], color=color_AUC_CAF_pre_scatter, alpha=.9,zorder=3)
                axs[2].bar(x3, dict_AUC_ratmeans['CAF']['AUC_post'][beh], color=color_AUC_CAF_post, width=barWidth, edgecolor='white', label='Post',zorder=2)
                axs[2].scatter(x_scatter3*x3, dict_AUC_means['CAF']['AUC_post'][beh],color=color_AUC_CAF_post_scatter,  alpha=.9,zorder=3)
                axs[2].set_title('CAF')
                # axs[2].set_yticks(yy)
                axs[2].spines['left'].set_visible(False)                
                axs[2].tick_params(left=False)              
                axs[2].axhline(y=0, linewidth=1, color=color_zeroline,zorder=4)
        
                # fig.suptitle('%s'%(beh), fontsize=16)
        
                plt.savefig('%s %s %s %s%s.png'%(graphtitle,phase,beh,test,testsession))
                plt.close(fig)
                # Change directory back
        os.chdir(directory)

    return dict_AUC_means

    print("AUC_result_behavior_snipper done")


###################################################################################################
################## AUC GRAPHS WITHOUT OUTLIERS - BUT INCL BEHAVIORS ########################################################
###################################################################################################

# Create results AUC figures -> Default sniptime = 2
AUC_RESULTS_COR_PRIM1_R=AUC_result_behavior_snipper("PRIMREWARD",1,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM3_R=AUC_result_behavior_snipper("PRIMREWARD",3,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM5_R=AUC_result_behavior_snipper("PRIMREWARD",5,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC1_R=AUC_result_behavior_snipper("SECREWARD",1,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC2_R=AUC_result_behavior_snipper("SECREWARD",2,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC3_R=AUC_result_behavior_snipper("SECREWARD",3,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_DIS1_R=AUC_result_behavior_snipper("DISREWARD",1,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM_rev1_R=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM_rev3_R=AUC_result_behavior_snipper("PRIMREWARD_rev",3,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC_rev1_R=AUC_result_behavior_snipper("SECREWARD_rev",1,"R",graphtitle="AUC_COR_incl ",exclude_outliers=True)  

AUC_RESULTS_COR_PRIM1_P=AUC_result_behavior_snipper("PRIMREWARD",1,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM3_P=AUC_result_behavior_snipper("PRIMREWARD",3,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM5_P=AUC_result_behavior_snipper("PRIMREWARD",5,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC2_P=AUC_result_behavior_snipper("SECREWARD",2,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_DIS1_P=AUC_result_behavior_snipper("DISREWARD",1,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM_rev1_P=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM_rev1_P=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_PRIM_rev3_P=AUC_result_behavior_snipper("PRIMREWARD_rev",3,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  
AUC_RESULTS_COR_SEC_rev1_P=AUC_result_behavior_snipper("SECREWARD_rev",1,"P",graphtitle="AUC_COR_incl ",exclude_outliers=True)  

###################################################################################################
################## AUC GRAPHS WITH OUTLIERS - BUT INCL BEHAVIORS ########################################################
###################################################################################################

# # Create results AUC figures -> Default sniptime = 2
# AUC_RESULTS_PRIM1_R=AUC_result_behavior_snipper("PRIMREWARD",1,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM3_R=AUC_result_behavior_snipper("PRIMREWARD",3,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM5_R=AUC_result_behavior_snipper("PRIMREWARD",5,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC1_R=AUC_result_behavior_snipper("SECREWARD",1,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC2_R=AUC_result_behavior_snipper("SECREWARD",2,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC3_R=AUC_result_behavior_snipper("SECREWARD",3,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_DIS1_R=AUC_result_behavior_snipper("DISREWARD",1,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM_rev1_R=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM_rev3_R=AUC_result_behavior_snipper("PRIMREWARD_rev",3,"R",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC_rev1_R=AUC_result_behavior_snipper("SECREWARD_rev",1,"R",graphtitle="AUC_incl ")  

# AUC_RESULTS_PRIM1_P=AUC_result_behavior_snipper("PRIMREWARD",1,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM3_P=AUC_result_behavior_snipper("PRIMREWARD",3,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM5_P=AUC_result_behavior_snipper("PRIMREWARD",5,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC2_P=AUC_result_behavior_snipper("SECREWARD",2,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_DIS1_P=AUC_result_behavior_snipper("DISREWARD",1,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM_rev1_P=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM_rev1_P=AUC_result_behavior_snipper("PRIMREWARD_rev",1,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_PRIM_rev3_P=AUC_result_behavior_snipper("PRIMREWARD_rev",3,"P",graphtitle="AUC_incl ")  
# AUC_RESULTS_SEC_rev1_P=AUC_result_behavior_snipper("SECREWARD_rev",1,"P",graphtitle="AUC_incl ")  

