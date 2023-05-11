# -*- coding: utf-8 -*-
"""
Created in 2022

Script to analyze the fiber photometry data with reward test for SCARF004.
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
    10) Fill in list with excluded animals and potential manual adjustments

Information on conditions built in:
    - Start lordosis is scored as lordosis, End lordosis as the copulation the female received


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
import time
import math
from matplotlib import rcParams
import pickle

# Define the directory folders (use / instead of \)
directory= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA" # Of the metafile and behavioral data
directory_tdt="D:/TDT SCARF004/" # Of the TDT recordings
directory_output= "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Output" # Of the output folder for your results

if not os.path.isdir(directory_output):
    os.mkdir(directory_output)

directory_TDT_lightdoor = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT lightdoor"
directory_TDT_lightdoor_perrat="C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT lightdoor per rat"
directory_TDT_lightdoor_AUC = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT AUC lightdoor"
directory_TDT_behavior = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT behavior"
directory_TDT_behavior_perrat="C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT behavior per rat"
directory_TDT_behavior_AUC = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results TDT AUC behavior"
directory_behavior_AUC = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results AUC behavior"
directory_behavior_perrat = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results behavior per rat"
directory_behavior_pertest = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results behavior per test"
directory_behavior_total = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Results behavior total"
directory_pickle = "D:/TDT SCARF004/Pickle files"
directory_TDT_fullgraphs = "C:/Users/esn001/OneDrive - UiT Office 365/Python 3.8/Data projects/SCARF004 Jaume VTA/Pictures Fullgraphs"

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

dict_manual_adjustments={'Cut_start':{
                          '304SECREWARD3':1200,
                          '312SECREWARD1':900,
                          '316SECREWARD3':850,
                          '321SECREWARD1':1250},
                        'Cut_end':{
                          '304SECREWARD3':1800,
                          '312SECREWARD1':1800,
                          '316SECREWARD3':950,
                          '321SECREWARD1':1800}}
                         

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

# Make dictionary for diet and virus
dict_diet = dict(zip(list_ratid,list_diet))
dict_virus = dict(zip(list_ratid,list_virus))
dict_id= dict(zip(list_ID,list_ratid))
dict_test=dict(zip(list_ID,list_test))
dict_testsession=dict(zip(list_ID,list_testsession))

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
list_interest_beh_prereward=['Close to door','Exploring door','Exploring environment (+rearing)','Head towards door','Paracopulatory','Reward INTRO','Selfgrooming']
list_interest_beh_reward=['Anogenital sniffing (received by the male)','Anogenital sniffing','Approach reward','Carry food','Close to reward','Eating','Ejaculation (received)','Exploring environment (+rearing)',
                          'Intromission (received)','LE','LI','LM','Lordosis 0','Lordosis 1','Lordosis 2', 'Lordosis 3','Lordosis',
                          'Mount (received)','Paracopulatory','Rejection','Selfgrooming','Sniffing reward']
list_behmark=[BO,BP,BU,BV,BW]

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

# # Save the results dataframes to excel for check
# writer_results = pd.ExcelWriter(out_path4, engine='xlsxwriter')
# data_R.to_excel(writer_results, sheet_name='data_R')
# writer_results.save()
# writer_results.close()

# Make list of the eating bout related outcomes
list_eating_bout=['Single eating','Single first eating','Single last eating','Single middle eating','Eating starts EB',
                  'Eating ends EB','First eating in EB','Last eating in EB','Middle eating in EB']

list_sex_bout=['Single sex','Single first sex','Single last sex','Single middle sex','sex starts SB',
                  'sex ends SB','First sex in SB','Last sex in SB','Middle sex in SB']

# Calculate the numbers of behaviors
def data_beh(dataframe,title):
    """
    Parameters
    ----------
    data : DataFrame
        Add the dataframe for analysis
        e.g. data_B, data_I, data_A, data_R
    title : string
        Add the experimental code
        e.g. 'data_B', 'data_I', 'data_A', 'data_R'
    Returns
    -------
    data : dictionary
        Returns a dictionary with the behavioral data per animal and test
    """
    
    start = time.time()
    dataframe['obs_num'] = dataframe.groupby(OBS)[BEH].transform(lambda x: np.arange(1, len(x) + 1))

    # Create an empty dictionary with ID and behaviors
    dict_data={}
    for key in list_id2:
        dict_data[key]={}
        for beh in list_behaviors:
            dict_data[key]['TN_%s'%beh]=[]
    
    # Fill in behaviors and times in dictionary
    for key,value in dict_data.items():
        print (title,key)
        for beh in list_behaviors:
            TN_temp=0
            TN_temp_sc=0
            TN_temp_rc=0
            TD_temp=0
            TD_temp_sc=0
            TD_temp_rc=0
            for row in dataframe.itertuples():
                if row.ID==key:
                    if row.Behavior == beh:
                        TN_temp=TN_temp+1
                        TD_temp=TD_temp+row.durations
                        if row.Chamber_mark == 'SC':
                            TN_temp_sc=TN_temp_sc+1
                            TD_temp_sc=TD_temp_sc+row.durations
                        else:
                            TN_temp_rc=TN_temp_rc+1
                            TD_temp_rc=TD_temp_rc+row.durations
           
            # Fill in dictionary with total number, number in start compartment, and number in reward compartment
            dict_data[key]['TN_%s'%beh]=TN_temp
            dict_data[key]['TN_%s_sc'%beh]=TN_temp_sc
            dict_data[key]['TN_%s_rc'%beh]=TN_temp_rc
            dict_data[key]['TD_%s'%beh]=TD_temp
            dict_data[key]['TD_%s_sc'%beh]=TD_temp_sc
            dict_data[key]['TD_%s_rc'%beh]=TD_temp_rc

        # Fill in starttimes
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.obs_num == 1:
                    temp = row.Time 
        dict_data[key]['Starttime']=temp

        # Fill in latency in dictionary
        for beh in list_behaviors:
            value=NaN
            temp=1800
            for row in dataframe.itertuples():
                if row.ID==key:
                    if row.Behavior == beh and row.Time<temp:
                        temp=row.Time
                        value=temp-dict_data[key]['Starttime']
            dict_data[key]['L1_%s'%beh]=value

        # Calculate the extra behaviors of total test, and performed in start and reward compartment
        for k,v in dict_list_extra.items():
            TN_temp=0
            TN_temp_sc=0
            TN_temp_rc=0
            TD_temp=0
            TD_temp_sc=0
            TD_temp_rc=0
            for i in v:
                TN_temp=TN_temp+dict_data[key]['TN_%s'%i]
                TN_temp_sc=TN_temp_sc+dict_data[key]['TN_%s_sc'%i]
                TN_temp_rc=TN_temp_rc+dict_data[key]['TN_%s_rc'%i]
                TD_temp=TD_temp+dict_data[key]['TD_%s'%i]
                TD_temp_sc=TD_temp_sc+dict_data[key]['TD_%s_sc'%i]
                TD_temp_rc=TD_temp_rc+dict_data[key]['TD_%s_rc'%i]
            
            dict_data[key]['TN_%s'%k]=TN_temp
            dict_data[key]['TN_%s_sc'%k]=TN_temp_sc
            dict_data[key]['TN_%s_rc'%k]=TN_temp_rc
            dict_data[key]['TD_%s'%k]=TD_temp
            dict_data[key]['TD_%s_sc'%k]=TD_temp_sc
            dict_data[key]['TD_%s_rc'%k]=TD_temp_rc
            
        # Fill in latency for extra behaviors in dictionary
        for k,v in dict_list_extra.items():
            value=1800
            for i in v:
                if dict_data[key]['L1_%s'%i]<value:
                    value=dict_data[key]['L1_%s'%i]
            dict_data[key]['L1_%s'%k]=value

        # Calculate number of crossings
        temp=0
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.Behavior in list_EH:
                    temp=temp+1
            
            dict_data[key]['Crossings']=temp-1

        # Fill in latency to cross
        value1=NaN
        temp1=1800
        value2=NaN
        temp2=1800
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.Behavior == CR and row.Time<temp1:
                    temp1=row.Time
                    value1=temp1-dict_data[key]['Starttime']
                if row.Behavior == CS and row.Time<temp2:
                    temp2=row.Time
                    value2=temp2-temp1
        if dict_data[key]['Crossings']==0:
            dict_data[key]['L1_Crossing']=NaN
            dict_data[key]['L1_Backcross']=NaN
        else:
            dict_data[key]['L1_Crossing']=value1
            dict_data[key]['L1_Backcross']=value2

        # Calculate extra lordoses
        dict_data[key]['Lordosis_extra']= dict_data[key]['TN_%s'%EB]+dict_data[key]['TN_%s'%BT]-dict_data[key]['TN_%s'%EA]
            
        # Calculte LQ and LS
        if dict_data[key]['TN_%s'%EA]>0: 
            dict_data[key]['LQ']= (dict_data[key]['TN_%s'%EB]-dict_data[key]['Lordosis_extra'])/dict_data[key]['TN_%s'%EA]*100
            dict_data[key]['LQ_plus']= (dict_data[key]['TN_%s'%EB]/dict_data[key]['TN_%s'%EA]*100)
            dict_data[key]['LS']= (((dict_data[key]['TN_%s'%BU]*1)+(dict_data[key]['TN_%s'%BV]*2)+(dict_data[key]['TN_%s'%BW]*3))/(dict_data[key]['TN_%s'%EB]+dict_data[key]['TN_%s'%BT]))
            dict_data[key]['TN_Dart_ratio']= dict_data[key]['TN_%s'%BP]/dict_data[key]['TN_%s'%EA]
            dict_data[key]['TD_Dart_ratio']= dict_data[key]['TD_%s'%BP]/dict_data[key]['TN_%s'%EA]
        else:
            dict_data[key]['LQ']= NaN
            dict_data[key]['LQ_plus']= NaN
            dict_data[key]['LS']= NaN
            dict_data[key]['TN_Dart_ratio']= NaN
            dict_data[key]['TD_Dart_ratio']= NaN
        
        # Calculate lordosis1-3 upon mount, intromission or ejaculation
        TN_temp_LM=0
        TN_temp_LI=0
        TN_temp_LE=0
        for row in dataframe.itertuples():
            if row.ID==key:
                if (row.Behavior == BU) or (row.Behavior == BV) or (row.Behavior == BW):  
                    if row.Next_beh == BQ:
                        TN_temp_LM=TN_temp_LM+1
                if (row.Behavior == BU) or (row.Behavior == BV) or (row.Behavior == BW):  
                    if row.Next_beh == BR:
                        TN_temp_LI=TN_temp_LI+1
                if (row.Behavior == BU) or (row.Behavior == BV) or (row.Behavior == BW):  
                    if row.Next_beh == BS:
                        TN_temp_LE=TN_temp_LE+1
        dict_data[key]['TN_LM']=TN_temp_LM
        dict_data[key]['TN_LI']=TN_temp_LI
        dict_data[key]['TN_LE']=TN_temp_LE
        
        # Calculate the CRL after mounts, intromissions and ejaculations
        tempM=0
        tempI=0
        tempE=0

        tnM=0
        tnI=0
        tnE=0
        for row in dataframe.itertuples():
            if row.ID==key:
                tempM=tempM+row.CRL_M if row.CRL_M >0 else tempM+0
                tempI=tempI+row.CRL_I if row.CRL_I >0 else tempI+0
                tempE=tempE+row.CRL_E if row.CRL_E >0 else tempE+0
                tnM=tnM+1 if row.CRL_M >0 else tnM+0
                tnI=tnI+1 if row.CRL_I >0 else tnI+0
                tnE=tnE+1 if row.CRL_E >0 else tnE+0
                
        dict_data[key]['TD_CRL_M']=tempM
        dict_data[key]['TD_CRL_I']=tempI
        dict_data[key]['TD_CRL_E']=tempE

        dict_data[key]['MD_CRL_M']=tempM/tnM if tnM>0 else NaN
        dict_data[key]['MD_CRL_I']=tempI/tnI if tnI>0 else NaN
        dict_data[key]['MD_CRL_E']=tempE/tnE if tnE>0 else NaN
        
        # Count number and duration eating bouts in total test
        for b in list_eating_bout:
            TN_temp=0
            TD_temp=0
            for row in dataframe.itertuples():
                if row.ID==key:
                    if row.EB_Eating_mark == '%s'%b:
                        TN_temp=TN_temp+1
                        TD_temp=TD_temp+row.Duration_eating_bout if row.Duration_eating_bout>0 else TD_temp+0

            dict_data[key]['TN_%s' %b]= TN_temp
            dict_data[key]['TD_%s' %b]= TD_temp
        TN_EB_temp=0
        TD_EB_temp=0
        for p in list_eating_bout:
            TN_EB_temp=TN_EB_temp+dict_data[key]['TN_%s' %p]
            TD_EB_temp=TD_EB_temp+dict_data[key]['TD_%s' %p]
        
        dict_data[key]['TN_EB']=TN_EB_temp-dict_data[key]['TN_Middle eating in EB']-dict_data[key]['TN_First eating in EB']-dict_data[key]['TN_Eating starts EB']
        dict_data[key]['TD_EB']=TD_EB_temp 
        dict_data[key]['MD_EB']=dict_data[key]['TD_EB']/dict_data[key]['TN_EB'] if dict_data[key]['TN_EB']>0 else NaN

        TN_temp_TO=0
        TD_temp_TO=0
        IMBI=[]
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.Duration_time_out > 0:
                    TN_temp_TO = TN_temp_TO+1
                    TD_temp_TO = TD_temp_TO+row.Duration_time_out
                
                # Calculate IMBI, mean of interval mount bouts
                if row.Interval_EB >0:
                    IMBI.append(row.Interval_EB)
        dict_data[key]['MD_IMBI']=np.mean(IMBI) if dict_data[key]['TN_EB']>0 else NaN
        dict_data[key]['TN_TO']= TN_temp_TO
        dict_data[key]['TD_TO']= TD_temp_TO if TN_temp_TO >0 else NaN
        dict_data[key]['MD_TO']= TD_temp_TO/TN_temp_TO if TN_temp_TO>0 else NaN
        
        ################
        # Count number and duration eating bouts in total test including the carrying food
        for b in list_eating_bout:
            TN_temp2=0
            TD_temp2=0
            TN_temp2_carry=0
            TD_temp2_carry=0
            TN_temp2_eating=0
            TD_temp2_eating=0
            for row in dataframe.itertuples():
                if row.ID==key:
                    if row.EB_Eating_mark2 == '%s'%b:
                        TN_temp2=TN_temp2+1
                        TD_temp2=TD_temp2+row.Duration_eating_bout2 if row.Duration_eating_bout2>0 else TD_temp2+0
                    if row.EB_Eating_mark2 == '%s'%b and row.Behavior== BN:
                        TN_temp2_carry=TN_temp2_carry+1
                        TD_temp2_carry=TD_temp2_carry+row.Duration_eating_bout2 if row.Duration_eating_bout2>0 else TD_temp2_carry+0
                    if row.EB_Eating_mark2 == '%s'%b and row.Behavior== BO:
                        TN_temp2_eating=TN_temp2_eating+1
                        TD_temp2_eating=TD_temp2_eating+row.Duration_eating_bout2 if row.Duration_eating_bout2>0 else TD_temp2_eating+0

            dict_data[key]['TN_%s_plus' %b]= TN_temp2
            dict_data[key]['TD_%s_plus' %b]= TD_temp2

            dict_data[key]['TN_%s_plus_carry' %b]= TN_temp2_carry
            dict_data[key]['TD_%s_plus_carry' %b]= TD_temp2_carry

            dict_data[key]['TN_%s_plus_eating' %b]= TN_temp2_eating
            dict_data[key]['TD_%s_plus_eating' %b]= TD_temp2_eating

        TN_EB_temp2=0
        TD_EB_temp2=0
        for p in list_eating_bout:
            TN_EB_temp2=TN_EB_temp2+dict_data[key]['TN_%s_plus' %p]
            TD_EB_temp2=TD_EB_temp2+dict_data[key]['TD_%s_plus' %p]
        
        dict_data[key]['TN_EB_plus']=TN_EB_temp2-dict_data[key]['TN_Middle eating in EB_plus']-dict_data[key]['TN_First eating in EB_plus']-dict_data[key]['TN_Eating starts EB_plus']
        dict_data[key]['TD_EB_plus']=TD_EB_temp2
        dict_data[key]['MD_EB_plus']=dict_data[key]['TD_EB_plus']/dict_data[key]['TN_EB_plus'] if dict_data[key]['TN_EB_plus']>0 else NaN

        TN_temp_TO2=0
        TD_temp_TO2=0
        IMBI2=[]
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.Duration_time_out2 > 0:
                    TN_temp_TO2 = TN_temp_TO2+1
                    TD_temp_TO2 = TD_temp_TO2+row.Duration_time_out2
                
                # Calculate IMBI, mean of interval mount bouts
                if row.Interval_EB2 >0:
                    IMBI2.append(row.Interval_EB2)
        dict_data[key]['MD_IMBI_plus']=np.mean(IMBI2) if dict_data[key]['TN_EB_plus']>0 else NaN
        dict_data[key]['TN_TO_plus']= TN_temp_TO2
        dict_data[key]['TD_TO_plus']= TD_temp_TO2 if TN_temp_TO2 >0 else NaN
        dict_data[key]['MD_TO_plus']= TD_temp_TO2/TN_temp_TO2 if TN_temp_TO2>0 else NaN

        ###################################################
        # Count number and duration sex bouts in total test
        for b in list_sex_bout:
            TN_sex_temp=0
            TD_sex_temp=0

            TN_sex_temp_dart=0
            TD_sex_temp_dart=0

            TN_sex_temp_lor=0
            TD_sex_temp_lor=0
            for row in dataframe.itertuples():
                if row.ID==key:
                    if row.SB_sex_mark == '%s'%b:
                        TN_sex_temp=TN_sex_temp+1
                        TD_sex_temp=TD_sex_temp+row.Duration_sex_bout if row.Duration_sex_bout>0 else TD_sex_temp+0
                    if row.SB_sex_mark == '%s'%b and row.Behavior== BP:
                        TN_sex_temp_dart=TN_sex_temp_dart+1
                        TD_sex_temp_dart=TD_sex_temp_dart+row.Duration_sex_bout if row.Duration_sex_bout>0 else TD_sex_temp_dart+0
                    if row.SB_sex_mark == '%s'%b and ((row.Behavior== BU)|(row.Behavior== BV)|(row.Behavior== BW)):
                        TN_sex_temp_lor=TN_sex_temp_lor+1
                        TD_sex_temp_lor=TD_sex_temp_lor+row.Duration_sex_bout if row.Duration_sex_bout>0 else TD_sex_temp_lor+0

            dict_data[key]['TN_%s' %b]= TN_sex_temp
            dict_data[key]['TD_%s' %b]= TD_sex_temp

            dict_data[key]['TN_%s_dart' %b]= TN_sex_temp_dart
            dict_data[key]['TD_%s_dart' %b]= TD_sex_temp_dart

            dict_data[key]['TN_%s_lor' %b]= TN_sex_temp_lor
            dict_data[key]['TD_%s_lor' %b]= TD_sex_temp_lor

        TN_SB_sex_temp=0
        TD_SB_sex_temp=0
        for p in list_sex_bout:
            TN_SB_sex_temp=TN_SB_sex_temp+dict_data[key]['TN_%s' %p]
            TD_SB_sex_temp=TD_SB_sex_temp+dict_data[key]['TD_%s' %p]
        
        dict_data[key]['TN_SB_sex']=TN_SB_sex_temp-dict_data[key]['TN_Middle sex in SB']-dict_data[key]['TN_First sex in SB']-dict_data[key]['TN_sex starts SB']
        dict_data[key]['TD_SB_sex']=TD_SB_sex_temp
        dict_data[key]['MD_SB_sex']=dict_data[key]['TD_SB_sex']/dict_data[key]['TN_SB_sex'] if dict_data[key]['TN_SB_sex']>0 else NaN

        TN_sex_temp_TO=0
        TD_sex_temp_TO=0
        IMBI=[]
        for row in dataframe.itertuples():
            if row.ID==key:
                if row.Duration_time_out_SB > 0:
                    TN_sex_temp_TO = TN_sex_temp_TO+1
                    TD_sex_temp_TO = TD_sex_temp_TO+row.Duration_time_out_SB
                
                # Calculate IMBI, mean of interval mount bouts
                if row.Interval_SB >0:
                    IMBI.append(row.Interval_SB)
        dict_data[key]['MD_IMBI_sex']=np.mean(IMBI) if dict_data[key]['TN_SB_sex']>0 else NaN
        dict_data[key]['TN_TO_sex']= TN_sex_temp_TO
        dict_data[key]['TD_TO_sex']= TD_sex_temp_TO if TN_sex_temp_TO >0 else NaN
        dict_data[key]['MD_TO_sex']= TD_sex_temp_TO/TN_sex_temp_TO if TN_sex_temp_TO>0 else NaN
        
    # Empty values when not tested
    if 'SEC' in key:
        for beh in list_fooditems:
            dict_data[key]['TN_%s'%beh]=NaN
            dict_data[key]['TN_%s_sc'%beh]=NaN
            dict_data[key]['TN_%s_rc'%beh]=NaN
            dict_data[key]['TD_%s'%beh]=NaN
            dict_data[key]['TD_%s_sc'%beh]=NaN
            dict_data[key]['TD_%s_rc'%beh]=NaN
            dict_data[key]['L1_%s'%beh]=NaN
        for i in list_eating_bout:   
            dict_data[key]['TN_%s'%i]=NaN
            dict_data[key]['TD_%s'%i]=NaN
            dict_data[key]['TN_EB']=NaN
            dict_data[key]['TD_EB']=NaN
            dict_data[key]['TN_TO']=NaN
            dict_data[key]['TD_TO']=NaN
            dict_data[key]['MD_TO']=NaN
            dict_data[key]['MD_IMBI']=NaN
            dict_data[key]['MD_EB']=NaN
            dict_data[key]['TN_%s_plus'%i]=NaN
            dict_data[key]['TD_%s_plus'%i]=NaN
            dict_data[key]['TN_%s_plus_carry'%i]=NaN
            dict_data[key]['TD_%s_plus_carry'%i]=NaN
            dict_data[key]['TN_%s_plus_eating'%i]=NaN
            dict_data[key]['TD_%s_plus_eating'%i]=NaN
            dict_data[key]['TN_EB_plus']=NaN
            dict_data[key]['TD_EB_plus']=NaN
            dict_data[key]['TN_TO_plus']=NaN
            dict_data[key]['TD_TO_plus']=NaN
            dict_data[key]['MD_TO_plus']=NaN
            dict_data[key]['MD_IMBI_plus']=NaN
            dict_data[key]['MD_EB_plus']=NaN
        
    if 'PRIM' in key or 'DIS' in key:
        for beh in list_sexitems:
            dict_data[key]['TN_%s'%beh]=NaN
            dict_data[key]['TN_%s_sc'%beh]=NaN
            dict_data[key]['TN_%s_rc'%beh]=NaN
            dict_data[key]['TD_%s'%beh]=NaN
            dict_data[key]['TD_%s_sc'%beh]=NaN
            dict_data[key]['TD_%s_rc'%beh]=NaN
            dict_data[key]['L1_%s'%beh]=NaN
            dict_data[key]['Lordosis_extra']=NaN
            dict_data[key]['LQ']=NaN
            dict_data[key]['LQ_plus']=NaN
            dict_data[key]['LS']=NaN
            dict_data[key]['TN_LM']=NaN
            dict_data[key]['TN_LI']=NaN
            dict_data[key]['TN_LE']=NaN
            dict_data[key]['TN_Dart_ratio']=NaN
            dict_data[key]['TD_Dart_ratio']=NaN
            dict_data[key]['TD_CRL_M']=NaN
            dict_data[key]['TD_CRL_I']=NaN
            dict_data[key]['TD_CRL_E']=NaN
            dict_data[key]['MD_CRL_M']=NaN
            dict_data[key]['MD_CRL_I']=NaN
            dict_data[key]['MD_CRL_E']=NaN
        for i in list_sex_bout:   
            dict_data[key]['TN_%s'%i]=NaN
            dict_data[key]['TD_%s'%i]=NaN
            dict_data[key]['TN_%s_dart'%i]=NaN
            dict_data[key]['TD_%s_dart'%i]=NaN
            dict_data[key]['TN_%s_lor'%i]=NaN
            dict_data[key]['TD_%s_lor'%i]=NaN
            dict_data[key]['TN_SB_sex']=NaN
            dict_data[key]['TD_SB_sex']=NaN
            dict_data[key]['TN_TO_sex']=NaN
            dict_data[key]['TD_TO_sex']=NaN
            dict_data[key]['MD_TO_sex']=NaN
            dict_data[key]['MD_IMBI_sex']=NaN
            dict_data[key]['MD_SB_sex']=NaN
    

    end = time.time()
    print(end - start)
    print('%s'%title)
    return dict_data

print ('definition behavior done')

#########################################################################################################
#########################################################################################################
################## BEHAVIORAL ANALYSIS ##################################################################
#########################################################################################################
#########################################################################################################

# # Calculate the results
# # dict_TN_results_T=data_beh_freq(data_T,'data_T')
# start=time.time()

# dict_results_R=data_beh(data_R,'data_R')
# dict_results_B=data_beh(data_B,'data_B')
# dict_results_I=data_beh(data_I,'data_I')
# dict_results_A=data_beh(data_A,'data_A')

# end=time.time()
# time_analysis= (end-start)/60
# print('data analyzed in %s minutes'%(time_analysis))

# # Create a list with the eating bout columns
# list_bout_columns = ['TN_EB','TD_EB','TN_TO','TD_TO','MD_TO','MD_IMBI','MD_EB',
#                    'TN_Single eating','TN_Single first eating','TN_Single last eating','TN_Single middle eating',
#                    'TN_Eating starts EB','TN_Eating ends EB','TN_First eating in EB','TN_Last eating in EB','TN_Eating middle EB',
#                    'TD_Single eating','TD_Single first eating','TD_Single last eating','TD_Single middle eating',
#                    'TD_Eating starts EB','TD_Eating ends EB','TD_First eating in EB','TD_Last eating in EB','TD_Eating middle EB',
#                    'TN_EB_plus','TD_EB_plus','TN_TO_plus','TD_TO_plus','MD_TO_plus','MD_IMBI_plus','MD_EB_plus',
#                     'TN_Single eating_plus','TN_Single first eating_plus','TN_Single last eating_plus','TN_Single middle eating_plus',
#                     'TN_Eating starts EB_plus','TN_Eating ends EB_plus','TN_First eating in EB_plus','TN_Last eating in EB_plus','TN_Eating middle EB_plus',
#                     'TD_Single eating_plus','TD_Single first eating_plus','TD_Single last eating_plus','TD_Single middle eating_plus',
#                     'TD_Eating starts EB_plus','TD_Eating ends EB_plus','TD_First eating in EB_plus','TD_Last eating in EB_plus','TD_Eating middle EB_plus',
#                     'TN_Single eating_plus_carry','TN_Single first eating_plus_carry','TN_Single last eating_plus_carry','TN_Single middle eating_plus_carry',
#                     'TN_Eating starts EB_plus_carry','TN_Eating ends EB_plus_carry','TN_First eating in EB_plus_carry','TN_Last eating in EB_plus_carry','TN_Eating middle EB_plus_carry',
#                     'TD_Single eating_plus_carry','TD_Single first eating_plus_carry','TD_Single last eating_plus_carry','TD_Single middle eating_plus_carry',
#                     'TD_Eating starts EB_plus_carry','TD_Eating ends EB_plus_carry','TD_First eating in EB_plus_carry','TD_Last eating in EB_plus_carry','TD_Eating middle EB_plus_carry',
#                     'TN_Single eating_plus_eating','TN_Single first eating_plus_eating','TN_Single last eating_plus_eating','TN_Single middle eating_plus_eating',
#                     'TN_Eating starts EB_plus_eating','TN_Eating ends EB_plus_eating','TN_First eating in EB_plus_eating','TN_Last eating in EB_plus_eating','TN_Eating middle EB_plus_eating',
#                     'TD_Single eating_plus_eating','TD_Single first eating_plus_eating','TD_Single last eating_plus_eating','TD_Single middle eating_plus_eating',
#                     'TD_Eating starts EB_plus_eating','TD_Eating ends EB_plus_eating','TD_First eating in EB_plus_eating','TD_Last eating in EB_plus_eating','TD_Eating middle EB_plus_eating',
#                     'TN_SB_sex','TD_SB_sex','TN_TO_sex','TD_TO_sex','MD_TO_sex','MD_IMBI_sex','MD_SB_sex',
#                     'TN_Single sex','TN_Single first sex','TN_Single last sex','TN_Single middle sex',
#                     'TN_sex starts SB','TN_sex ends SB','TN_First sex in SB','TN_Last sex in SB','TN_sex middle SB',
#                     'TD_Single sex','TD_Single first sex','TD_Single last sex','TD_Single middle sex',
#                     'TD_sex starts SB','TD_sex ends SB','TD_First sex in SB','TD_Last sex in SB','TD_sex middle SB',
#                     'TN_Single sex_dart','TN_Single first sex_dart','TN_Single last sex_dart','TN_Single middle sex_dart',
#                     'TN_sex starts SB_dart','TN_sex ends SB_dart','TN_First sex in SB_dart','TN_Last sex in SB_dart','TN_sex middle SB_dart',
#                     'TD_Single sex_dart','TD_Single first sex_dart','TD_Single last sex_dart','TD_Single middle sex_dart',
#                     'TD_sex starts SB_dart','TD_sex ends SB_dart','TD_First sex in SB_dart','TD_Last sex in SB_dart','TD_sex middle SB_dart',
#                     'TN_Single sex_lor','TN_Single first sex_lor','TN_Single last sex_lor','TN_Single middle sex_lor',
#                     'TN_sex starts SB_lor','TN_sex ends SB_lor','TN_First sex in SB_lor','TN_Last sex in SB_lor','TN_sex middle SB_lor',
#                     'TD_Single sex_lor','TD_Single first sex_lor','TD_Single last sex_lor','TD_Single middle sex_lor',
#                     'TD_sex starts SB_lor','TD_sex ends SB_lor','TD_First sex in SB_lor','TD_Last sex in SB_lor','TD_sex middle SB_lor']

# # Sum dictionaries to create a dictionary for the total test and prereward phase.
# def sum_2dicts(dict1,dict2):
#     """
#     Parameters
#     ----------
#     dict1 : dictionary
#         Add 1st dictionary that needs to be added
#         e.g. data_B, data_I, data_A, data_R
#     dict2 : dictionary
#         Add 2nd dictionary that needs to be added
#         e.g. data_B, data_I, data_A, data_R

#     Returns
#     -------
#     new_dict : dictionary
#         Returns a new dictionary that combined two dictionaries into one (by adding values)

#     """
#     list_parameters=[]
#     list_id=[]
#     new_dict={}
#     for key,behavior in dict1.items():
#         if key not in list_id:
#             list_id.append(key)
#         for beh, val in behavior.items():
#             if beh not in list_parameters:
#                 list_parameters.append(beh)
    
#     for ids in list_id:
#         new_dict[ids]={}
#         for i in list_parameters:
#             new_dict[ids][i]=[]   
  
#     for key1,b1 in dict1.items():
#         # print(key1)
#         for key2,b2 in dict2.items():
#             # Now fill new dictionary
#             if key1==key2:
#                 for beh1,val1 in b1.items():
#                     for beh2,val2 in b2.items():
#                         if beh1 in list_bout_columns:
#                             new_dict[key1][beh1]=val2
#                         else:
#                             if beh1==beh2:
#                                 if 'L1' in beh1:
#                                     if val1 < val2:
#                                         new_dict[key1][beh1]=val1
#                                     else:
#                                         new_dict[key1][beh1]=val2
#                                 else:  
#                                     new_dict[key1][beh1]=val1+val2

#     print('Summation of dictionaries done')                 
#     return new_dict

# def sum_3dicts(dict1,dict2,dict3):
#     """
#     Parameters
#     ----------
#     dict1 : dictionary
#         Add 1st dictionary that needs to be added
#         e.g. data_B, data_I, data_A, data_R
#     dict2 : dictionary
#         Add 2nd dictionary that needs to be added
#         e.g. data_B, data_I, data_A, data_R
#         e.g. data_B, data_I, data_A, data_R
#     dict3 : dictionary
#         Add 3rd dictionary that needs to be added
#         e.g. data_B, data_I, data_A, data_R

#     Returns
#     -------
#     new_dict : dictionary
#         Returns a new dictionary that combined three dictionaries into one (by adding values)

#     """

#     list_parameters=[]
#     list_id=[]
#     new_dict={}
#     for key,behavior in dict1.items():
#         if key not in list_id:
#             list_id.append(key)
#         # for beh,val in behavior.items(): 
#         for beh, val in behavior.items():
#             if beh not in list_parameters:
#                 list_parameters.append(beh)
    
#     for ids in list_id:
#         new_dict[ids]={}
#         for i in list_parameters:
#             new_dict[ids][i]=[]   
  
#     for key1,b1 in dict1.items():
#         print(key1)
#         for key2,b2 in dict2.items():
#             for key3,b3 in dict3.items():
#                 # Now fill new dictionary
#                 if key1==key2 and key1 == key3:
#                     for beh1,val1 in b1.items():
#                         for beh2,val2 in b2.items():
#                             for beh3,val3 in b3.items():
#                                 if beh1==beh2 and beh1==beh3:
#                                     if 'L1' in beh1:
#                                         if val1 < val2 and val1 < val3:
#                                             new_dict[key1][beh1]=val1
#                                         if val2 < val1 and val2 < val3:
#                                             new_dict[key1][beh1]=val2
#                                         else:
#                                             new_dict[key1][beh1]=val3
#                                     else:    
#                                         new_dict[key1][beh1]=val1+val2+val3
        
    
#     print('Summation of dictionaries done')                 
#     return new_dict

# # SUm dictionaries to get a dictionary for the prereward phase (baseline+introductory and anticipatory phase) and total test
# start=time.time()

# dict_results_P=sum_3dicts(dict_results_B,dict_results_I,dict_results_A)
# dict_results_T=sum_2dicts(dict_results_P,dict_results_R)

# end=time.time()
# time_analysis= (end-start)/60
# print('total and prereward data analyzed in %s minutes'%(time_analysis))

# # Correct LQ,LS,etc in dict_results_T
# for key,behav in dict_results_T.items():
#     for beh,val in behav.items():
#         dict_results_T[key]['Lordosis_extra']= dict_results_R[key]['Lordosis_extra']
#         dict_results_T[key]['LQ']= dict_results_R[key]['LQ']
#         dict_results_T[key]['LQ_plus']= dict_results_R[key]['LQ_plus']
#         dict_results_T[key]['LS']= dict_results_R[key]['LS']

# # Now make dataframes from the dictionairies
# df_results_T = pd.DataFrame(dict_results_T)
# df_results_T=df_results_T.T

# df_results_B = pd.DataFrame(dict_results_B)
# df_results_B=df_results_B.T

# df_results_I = pd.DataFrame(dict_results_I)
# df_results_I=df_results_I.T

# df_results_A = pd.DataFrame(dict_results_A)
# df_results_A=df_results_A.T

# df_results_P = pd.DataFrame(dict_results_P)
# df_results_P=df_results_P.T

# df_results_R = pd.DataFrame(dict_results_R)
# df_results_R=df_results_R.T

# # Make dictionary of dataframes with total
# df_results={'T':df_results_T,'B':df_results_B,'I':df_results_I,'A':df_results_A,'P':df_results_P,'R':df_results_R}

# # # Save the results dataframes to excel for later easy read in without having to run the script completely
# # writer_results = pd.ExcelWriter(out_path6, engine='xlsxwriter')
# # df_results_T.to_excel(writer_results, sheet_name='results_T')
# # df_results_B.to_excel(writer_results, sheet_name='results_B')
# # df_results_I.to_excel(writer_results, sheet_name='results_I')
# # df_results_A.to_excel(writer_results, sheet_name='results_A')
# # df_results_P.to_excel(writer_results, sheet_name='results_P')
# # df_results_R.to_excel(writer_results, sheet_name='results_R')
# # writer_results.save()
# # writer_results.close()

# # Rename columns for practical use
# for keys in df_results.keys():
#       df_results[keys].columns=df_results[keys].columns.str.replace('(','', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(')','', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('+','', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Exploring environment rearing','Exploration', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' received by the male','_male', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' received','', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('towards','to', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' open','', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Anogenital sniffing','Anosniffing', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' - right','box', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' - left','box', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace(' ','_', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('_0','0', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('_1','1', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('_2','2', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('_3','3', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Baseline_mark','Phase_mark', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Introduction_mark','Phase_mark', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Anticipatory_mark','Phase_mark', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Prereward_mark','Phase_mark', regex=True)
#       df_results[keys].columns=df_results[keys].columns.str.replace('Reward_mark','Phase_mark', regex=True)

# # Add columns about virus, diet, etc
# for key,df in df_results.items():
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
    
# start_columns=['ID',RATID,VIRUS,DIET,TEST,'Testsession']

# # # Save the results dataframes to excel for check
# # writer_results = pd.ExcelWriter(out_path5, engine='xlsxwriter')
# # df_results_T.to_excel(writer_results, sheet_name='results_T')
# # df_results_B.to_excel(writer_results, sheet_name='results_B')
# # df_results_I.to_excel(writer_results, sheet_name='results_I')
# # df_results_A.to_excel(writer_results, sheet_name='results_A')
# # df_results_P.to_excel(writer_results, sheet_name='results_P')
# # df_results_R.to_excel(writer_results, sheet_name='results_R')
# # writer_results.save()
# # writer_results.close()


# # Create a list of column names you would like per sheet
# list_TN_baseline=['TN_Reward_interest','TN_Exploration','TN_Exploring_door',
#                   'TN_Head_to_door','TN_Close_to_door','TN_Selfgrooming','TN_Resting']

# list_TD_baseline=['TD_Reward_interest','TD_Exploration','TD_Exploring_door',
#                   'TD_Head_to_door','TD_Close_to_door','TD_Selfgrooming','TD_Resting']

# list_L1_baseline=['L1_Reward_interest','L1_Exploration','L1_Exploring_door',
#                   'L1_Head_to_door','L1_Close_to_door','L1_Selfgrooming','L1_Resting']
                  
# list_TN_main=['TN_Reward_interest','TN_Approach_reward','TN_Reward_anticipatory','TN_Reward_consummatory','TN_Reward_consummatory_rc','TN_Reward_consummatory_sc',
#                           'TN_Food_interaction','TN_Sex_interaction','TN_Dart_ratio','LQ','LQ_plus','LS','Lordosis_extra',
#                           'TN_Sniffing_reward','TN_Close_to_reward','TN_Anosniffing','TN_Anosniffing_male',
#                           'TN_Allogrooming','TN_Carry_food','TN_Eating','TN_Paracopulatory','TN_Copulations','TN_Lordosis',
#                           'TN_LM', 'TN_LI', 'TN_LE','TN_Mount','TN_Intromission','TN_Ejaculation','TN_Rejection',
#                           'TN_EB','TN_TO','TN_Single_eating','TN_Single_first_eating','TN_Single_last_eating',
#                           'TN_Single_middle_eating','TN_Eating_starts_EB','TN_Eating_ends_EB','TN_First_eating_in_EB',
#                           'TN_Last_eating_in_EB','TN_Middle_eating_in_EB',
#                           'TN_EB_plus','TN_TO_plus','TN_Single_eating_plus','TN_Single_first_eating_plus','TN_Single_last_eating_plus',
#                           'TN_Single_middle_eating_plus','TN_Eating_starts_EB_plus','TN_Eating_ends_EB_plus','TN_First_eating_in_EB_plus',
#                           'TN_Last_eating_in_EB_plus','TN_Middle_eating_in_EB_plus',
#                           'TN_Single_eating_plus_carry','TN_Single_first_eating_plus_carry','TN_Single_last_eating_plus_carry',
#                           'TN_Single_middle_eating_plus_carry','TN_Eating_starts_EB_plus_carry','TN_Eating_ends_EB_plus_carry','TN_First_eating_in_EB_plus_carry',
#                           'TN_Last_eating_in_EB_plus_carry','TN_Middle_eating_in_EB_plus_carry',
#                           'TN_Single_eating_plus_eating','TN_Single_first_eating_plus_eating','TN_Single_last_eating_plus_eating',
#                           'TN_Single_middle_eating_plus_eating','TN_Eating_starts_EB_plus_eating','TN_Eating_ends_EB_plus_eating','TN_First_eating_in_EB_plus_eating',
#                           'TN_Last_eating_in_EB_plus_eating','TN_Middle_eating_in_EB_plus_eating',
#                           'TN_SB_sex','TN_TO_sex',
#                           'TN_Single_sex','TN_Single_first_sex','TN_Single_last_sex','TN_Single_middle_sex',
#                           'TN_sex_starts_SB','TN_sex_ends_SB','TN_First_sex_in_SB','TN_Last_sex_in_SB','TN_Middle_sex_in_SB',
#                           'TN_Single_sex_dart','TN_Single_first_sex_dart','TN_Single_last_sex_dart','TN_Single_middle_sex_dart',
#                           'TN_sex_starts_SB_dart','TN_sex_ends_SB_dart','TN_First_sex_in_SB_dart','TN_Last_sex_in_SB_dart','TN_Middle_sex_in_SB_dart',
#                           'TN_Single_sex_lor','TN_Single_first_sex_lor','TN_Single_last_sex_lor','TN_Single_middle_sex_lor',
#                           'TN_sex_starts_SB_lor','TN_sex_ends_SB_lor','TN_First_sex_in_SB_lor','TN_Last_sex_in_SB_lor','TN_Middle_sex_in_SB_lor']

# list_TN_extra=['TN_Reward_interest_rc','TN_Reward_interest_sc','TN_Approach_reward_rc','TN_Approach_reward_sc',
#                'TN_Reward_anticipatory_rc','TN_Reward_anticipatory_sc','TN_Food_interaction_rc','TN_Food_interaction_sc',
#                'TN_Sex_interaction_rc','TN_Sex_interaction_sc','TN_Sniffing_reward_rc','TN_Sniffing_reward_sc',
#                'TN_Close_to_reward_rc','TN_Close_to_reward_sc','TN_Anosniffing_rc','TN_Anosniffing_sc',
#                'TN_Anosniffing_male_rc','TN_Anosniffing_male_sc','TN_Allogrooming_rc','TN_Allogrooming_sc',
#                'TN_Carry_food_rc','TN_Carry_food_sc','TN_Eating_rc','TN_Eating_sc','TN_Lordosis_rc','TN_Lordosis_sc',
#                'TN_Mount_rc','TN_Mount_sc','TN_Intromission_rc','TN_Intromission_sc',
#                'TN_Paracopulatory_rc','TN_Paracopulatory_sc','TN_Copulations_rc','TN_Copulations_sc',
#                'TN_Ejaculation_rc','TN_Ejaculation_sc','TN_Rejection_rc','TN_Rejection_sc',
#                'TN_Exploration','TN_Exploration_rc','TN_Exploration_sc','TN_Exploring_door','TN_Exploring_door_rc','TN_Exploring_door_sc',
#                           'TN_Head_to_door','TN_Head_to_door_rc','TN_Head_to_door_sc','TN_Close_to_door','TN_Close_to_door_rc','TN_Close_to_door_sc',
#                           'TN_Selfgrooming','TN_Selfgrooming_rc',
#                           'TN_Selfgrooming_sc','TN_In_door','TN_In_door_rc','TN_In_door_sc','TN_Resting','TN_Resting_rc','TN_Resting_sc',
#                           'TN_Lordosis0','TN_Lordosis0_rc','TN_Lordosis0_sc','TN_Lordosis1','TN_Lordosis1_rc','TN_Lordosis1_sc','TN_Lordosis2','TN_Lordosis2_rc',
#                           'TN_Lordosis2_sc','TN_Lordosis3','TN_Lordosis3_rc','TN_Lordosis3_sc']

# list_TD_main=['TD_Reward_interest','TD_Reward_anticipatory','TD_Reward_consummatory','TD_Food_interaction',
#                           'TD_Sex_interaction','TD_Dart_ratio','TD_Sniffing_reward','TD_Close_to_reward','TD_Anosniffing',
#                           'TD_Anosniffing_male','TD_Allogrooming','TD_Carry_food','TD_Eating','TD_Paracopulatory',
#                           'TD_Copulations','TD_Mount','TD_Intromission','TD_Ejaculation','TD_Rejection','TD_CRL_M','TD_CRL_I','TD_CRL_E',
#                           'MD_CRL_M','MD_CRL_I','MD_CRL_E',
#                           'TD_EB','MD_EB','TD_TO','MD_TO','MD_IMBI','TD_Single_eating','TD_Single_first_eating','TD_Single_last_eating',
#                           'TD_Single_middle_eating','TD_Eating_starts_EB','TD_Eating_ends_EB','TD_First_eating_in_EB',
#                           'TD_Last_eating_in_EB','TD_Middle_eating_in_EB',
#                           'TD_EB_plus','MD_EB_plus','TD_TO_plus','MD_TO_plus','MD_IMBI_plus','TD_Single_eating_plus','TD_Single_first_eating_plus','TD_Single_last_eating_plus',
#                           'TD_Single_middle_eating_plus','TD_Eating_starts_EB_plus','TD_Eating_ends_EB_plus','TD_First_eating_in_EB_plus',
#                           'TD_Last_eating_in_EB_plus','TD_Middle_eating_in_EB_plus',
#                           'TD_Single_eating_plus_carry','TD_Single_first_eating_plus_carry','TD_Single_last_eating_plus_carry',
#                           'TD_Single_middle_eating_plus_carry','TD_Eating_starts_EB_plus_carry','TD_Eating_ends_EB_plus_carry','TD_First_eating_in_EB_plus_carry',
#                           'TD_Last_eating_in_EB_plus_carry','TD_Middle_eating_in_EB_plus_carry',
#                           'TD_Single_eating_plus_eating','TD_Single_first_eating_plus_eating','TD_Single_last_eating_plus_eating',
#                           'TD_Single_middle_eating_plus_eating','TD_Eating_starts_EB_plus_eating','TD_Eating_ends_EB_plus_eating','TD_First_eating_in_EB_plus_eating',
#                           'TD_Last_eating_in_EB_plus_eating','TD_Middle_eating_in_EB_plus_eating',
#                           'TD_SB_sex','TD_TO_sex','MD_TO_sex','MD_IMBI_sex','MD_SB_sex',
#                           'TD_Single_sex','TD_Single_first_sex','TD_Single_last_sex','TD_Single_middle_sex',
#                           'TD_sex_starts_SB','TD_sex_ends_SB','TD_First_sex_in_SB','TD_Last_sex_in_SB','TD_Middle_sex_in_SB',
#                           'TD_Single_sex_dart','TD_Single_first_sex_dart','TD_Single_last_sex_dart','TD_Single_middle_sex_dart',
#                             'TD_sex_starts_SB_dart','TD_sex_ends_SB_dart','TD_First_sex_in_SB_dart','TD_Last_sex_in_SB_dart','TD_Middle_sex_in_SB_dart',
#                             'TD_Single_sex_lor','TD_Single_first_sex_lor','TD_Single_last_sex_lor','TD_Single_middle_sex_lor',
#                             'TD_sex_starts_SB_lor','TD_sex_ends_SB_lor','TD_First_sex_in_SB_lor','TD_Last_sex_in_SB_lor','TD_Middle_sex_in_SB_lor']


# list_TD_extra=['TD_Reward_interest_rc','TD_Reward_interest_sc','TD_Reward_anticipatory_rc','TD_Reward_anticipatory_sc',
#                'TD_Reward_consummatory_rc','TD_Reward_consummatory_sc','TD_Food_interaction_rc','TD_Food_interaction_sc',
#                'TD_Sex_interaction_rc','TD_Sex_interaction_sc','TD_Sniffing_reward_rc','TD_Sniffing_reward_sc',
#                'TD_Close_to_reward_rc','TD_Close_to_reward_sc','TD_Anosniffing_rc','TD_Anosniffing_sc',
#                'TD_Anosniffing_male_rc','TD_Anosniffing_male_sc','TD_Allogrooming_rc','TD_Allogrooming_sc',
#                'TD_Carry_food_rc','TD_Carry_food_sc','TD_Eating_rc','TD_Eating_sc','TD_Paracopulatory_rc','TD_Paracopulatory_sc',
#                'TD_Copulations_rc','TD_Copulations_sc','TD_Mount_rc','TD_Mount_sc','TD_Intromission_rc','TD_Intromission_sc',
#                'TD_Ejaculation_rc','TD_Ejaculation_sc','TD_Rejection_rc','TD_Rejection_sc',
#                'TD_Exploration','TD_Exploration_rc','TD_Exploration_sc','TD_Exploring_door','TD_Exploring_door_rc','TD_Exploring_door_sc',
#                           'TD_Head_to_door','TD_Head_to_door_rc','TD_Head_to_door_sc','TD_Close_to_door','TD_Close_to_door_rc','TD_Close_to_door_sc',
#                           'TD_Selfgrooming','TD_Selfgrooming_rc',
#                           'TD_Selfgrooming_sc','TD_In_door','TD_In_door_rc','TD_In_door_sc','TD_Resting','TD_Resting_rc','TD_Resting_sc']

# list_L1_main=['L1_Crossing','L1_Backcross','L1_Reward_interest','L1_Approach_reward','L1_Reward_anticipatory',
#               'L1_Reward_consummatory','L1_Food_interaction','L1_Sex_interaction','L1_Sniffing_reward','L1_Close_to_reward','L1_Anosniffing',
#               'L1_Anosniffing_male','L1_Allogrooming','L1_Carry_food','L1_Eating','L1_Paracopulatory','L1_Copulations','L1_Lordosis','L1_Mount','L1_Intromission',
#               'L1_Ejaculation','L1_Rejection']

# list_L1_extra=['L1_Exploration','L1_Exploring_door','L1_Head_to_door','L1_Close_to_door','L1_Selfgrooming','L1_In_door','L1_Resting',
#               'L1_Lordosis0','L1_Lordosis1','L1_Lordosis2','L1_Lordosis3']                                         
                                                 

# # Create new dataframes with the relevant data
# df_TN_main_T=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_TN_main):
#     df_TN_main_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_TN_main_B=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_B['%s'%i]=df_results_B['%s'%i].copy()
# for t,title in enumerate(list_TN_baseline):
#     df_TN_main_B['B_%s'%title]=df_results_B['%s'%title].copy()

# df_TN_main_I=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_I['%s'%i]=df_results_I['%s'%i].copy()
# for t,title in enumerate(list_TN_baseline):
#     df_TN_main_I['I_%s'%title]=df_results_I['%s'%title].copy()

# df_TN_main_A=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_A['%s'%i]=df_results_A['%s'%i].copy()
# for t,title in enumerate(list_TN_baseline):
#     df_TN_main_A['A_%s'%title]=df_results_A['%s'%title].copy()

# df_TN_main_P=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_P['%s'%i]=df_results_P['%s'%i].copy()
# for t,title in enumerate(list_TN_baseline):
#     df_TN_main_P['P_%s'%title]=df_results_P['%s'%title].copy()

# df_TN_main_R=pd.DataFrame()
# for i in start_columns:
#     df_TN_main_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_TN_main):
#     df_TN_main_R['R_%s'%title]=df_results_R['%s'%title].copy()

# df_TN_extra_T=pd.DataFrame()
# for i in start_columns:
#     df_TN_extra_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_TN_extra):
#     df_TN_extra_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_TN_extra_R=pd.DataFrame()
# for i in start_columns:
#     df_TN_extra_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_TN_extra):
#     df_TN_extra_R['R_%s'%title]=df_results_R['%s'%title].copy()

# df_TD_main_T=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_TD_main):
#     df_TD_main_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_TD_main_B=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_B['%s'%i]=df_results_B['%s'%i].copy()
# for t,title in enumerate(list_TD_baseline):
#     df_TD_main_B['B_%s'%title]=df_results_B['%s'%title].copy()

# df_TD_main_I=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_I['%s'%i]=df_results_I['%s'%i].copy()
# for t,title in enumerate(list_TD_baseline):
#     df_TD_main_I['I_%s'%title]=df_results_I['%s'%title].copy()

# df_TD_main_A=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_A['%s'%i]=df_results_A['%s'%i].copy()
# for t,title in enumerate(list_TD_baseline):
#     df_TD_main_A['A_%s'%title]=df_results_A['%s'%title].copy()

# df_TD_main_P=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_P['%s'%i]=df_results_P['%s'%i].copy()
# for t,title in enumerate(list_TD_baseline):
#     df_TD_main_P['P_%s'%title]=df_results_P['%s'%title].copy()

# df_TD_main_R=pd.DataFrame()
# for i in start_columns:
#     df_TD_main_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_TD_main):
#     df_TD_main_R['R_%s'%title]=df_results_R['%s'%title].copy()

# df_TD_extra_T=pd.DataFrame()
# for i in start_columns:
#     df_TD_extra_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_TD_extra):
#     df_TD_extra_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_TD_extra_R=pd.DataFrame()
# for i in start_columns:
#     df_TD_extra_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_TD_extra):
#     df_TD_extra_R['R_%s'%title]=df_results_R['%s'%title].copy()

# df_L1_main_T=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_L1_main):
#     df_L1_main_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_L1_main_B=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_B['%s'%i]=df_results_B['%s'%i].copy()
# for t,title in enumerate(list_L1_baseline):
#     df_L1_main_B['B_%s'%title]=df_results_B['%s'%title].copy()

# df_L1_main_I=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_I['%s'%i]=df_results_I['%s'%i].copy()
# for t,title in enumerate(list_L1_baseline):
#     df_L1_main_I['I_%s'%title]=df_results_I['%s'%title].copy()

# df_L1_main_A=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_A['%s'%i]=df_results_A['%s'%i].copy()
# for t,title in enumerate(list_L1_baseline):
#     df_L1_main_A['A_%s'%title]=df_results_A['%s'%title].copy()

# df_L1_main_P=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_P['%s'%i]=df_results_P['%s'%i].copy()
# for t,title in enumerate(list_L1_baseline):
#     df_L1_main_P['P_%s'%title]=df_results_P['%s'%title].copy()

# df_L1_main_R=pd.DataFrame()
# for i in start_columns:
#     df_L1_main_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_L1_main):
#     df_L1_main_R['R_%s'%title]=df_results_R['%s'%title].copy()

# df_L1_extra_T=pd.DataFrame()
# for i in start_columns:
#     df_L1_extra_T['%s'%i]=df_results_T['%s'%i].copy()
# for t,title in enumerate(list_L1_extra):
#     df_L1_extra_T['T_%s'%title]=df_results_T['%s'%title].copy()

# df_L1_extra_R=pd.DataFrame()
# for i in start_columns:
#     df_L1_extra_R['%s'%i]=df_results_R['%s'%i].copy()
# for t,title in enumerate(list_L1_extra):
#     df_L1_extra_R['R_%s'%title]=df_results_R['%s'%title].copy()

# # Create a dataframe of the most important information
# df_important_data1=df_TD_main_R[['ID',RATID,VIRUS,DIET,TEST,'Testsession']].copy()
# df_important_data1['B_TD_Reward_interest']=df_TD_main_B['B_TD_Reward_interest']
# df_important_data1['P_TD_Reward_interest']=df_TD_main_P['P_TD_Reward_interest']
# df_important_data1['R_TD_Reward_interest']=df_TD_main_R['R_TD_Reward_interest']
# df_important_data1['B_TN_Reward_interest']=df_TN_main_B['B_TN_Reward_interest']
# df_important_data1['P_TN_Reward_interest']=df_TN_main_P['P_TN_Reward_interest']
# df_important_data1['R_TN_Reward_interest']=df_TN_main_R['R_TN_Reward_interest']
# df_important_data1['R_TD_Reward_anticipatory']=df_TD_main_R['R_TD_Reward_anticipatory']
# df_important_data1['R_TN_Reward_anticipatory']=df_TN_main_R['R_TN_Reward_anticipatory']
# df_important_data1['R_L1_Reward_anticipatory']=df_L1_main_R['R_L1_Reward_anticipatory']
# df_important_data1['R_TD_Reward_consummatory']=df_TD_main_R['R_TD_Reward_consummatory']
# df_important_data1['R_TN_Reward_consummatory']=df_TN_main_R['R_TN_Reward_consummatory']
# df_important_data1['R_L1_Reward_consummatory']=df_L1_main_R['R_L1_Reward_consummatory']
# df_important_data1['R_TD_Reward_interaction']=np.where(((df_TD_main_R['Test']=='SECREWARD')|(df_TD_main_R['Test']=='SECREWARD_rev')), df_TD_main_R['R_TD_Sex_interaction'],df_TD_main_R['R_TD_Food_interaction'])
# df_important_data1['R_TN_Reward_interaction']=np.where(((df_TN_main_R['Test']=='SECREWARD')|(df_TN_main_R['Test']=='SECREWARD_rev')), df_TN_main_R['R_TN_Sex_interaction'],df_TN_main_R['R_TN_Food_interaction'])
# df_important_data1['R_L1_Reward_interaction']=np.where(((df_L1_main_R['Test']=='SECREWARD')|(df_L1_main_R['Test']=='SECREWARD_rev')), df_L1_main_R['R_L1_Sex_interaction'],df_L1_main_R['R_L1_Food_interaction'])

# df_important_data2=df_TD_main_R[['ID',RATID,VIRUS,DIET,TEST,'Testsession']].copy()
# df_important_data2['R_TD_Sniffing_reward']=df_TD_main_R['R_TD_Sniffing_reward']
# df_important_data2['R_TN_Sniffing_reward']=df_TN_main_R['R_TN_Sniffing_reward']
# df_important_data2['R_TD_Carry_food']=df_TD_main_R['R_TD_Carry_food']
# df_important_data2['R_TN_Carry_food']=df_TN_main_R['R_TN_Carry_food']
# df_important_data2['R_TD_Eating']=df_TD_main_R['R_TD_Eating']
# df_important_data2['R_TN_Eating']=df_TN_main_R['R_TN_Eating']
# df_important_data2['R_TN_EB']=df_TN_main_R['R_TN_EB']
# df_important_data2['R_TD_EB']=df_TD_main_R['R_TD_EB']
# df_important_data2['R_MD_EB']=df_TD_main_R['R_MD_EB']
# df_important_data2['R_TN_TO']=df_TN_main_R['R_TN_TO']
# df_important_data2['R_TD_TO']=df_TD_main_R['R_TD_TO']
# df_important_data2['R_MD_TO']=df_TD_main_R['R_MD_TO']
# df_important_data2['R_MD_IMBI']=df_TD_main_R['R_MD_IMBI']
# df_important_data2['R_TN_EB_plus']=df_TN_main_R['R_TN_EB_plus']
# df_important_data2['R_TD_EB_plus']=df_TD_main_R['R_TD_EB_plus']
# df_important_data2['R_MD_EB_plus']=df_TD_main_R['R_MD_EB_plus']
# df_important_data2['R_TN_TO_plus']=df_TN_main_R['R_TN_TO_plus']
# df_important_data2['R_TD_TO_plus']=df_TD_main_R['R_TD_TO_plus']
# df_important_data2['R_MD_TO_plus']=df_TD_main_R['R_MD_TO_plus']
# df_important_data2['R_MD_IMBI_plus']=df_TD_main_R['R_MD_IMBI_plus']
# df_important_data2['R_TD_Paracopulatory']=df_TD_main_R['R_TD_Paracopulatory']
# df_important_data2['R_TN_Paracopulatory']=df_TN_main_R['R_TN_Paracopulatory']
# df_important_data2['R_TN_Dart_ratio']=df_TN_main_R['R_TN_Dart_ratio']
# df_important_data2['R_TD_Dart_ratio']=df_TD_main_R['R_TD_Dart_ratio']
# df_important_data2['R_TD_CRL_M']=df_TD_main_R['R_TD_CRL_M']
# df_important_data2['R_TD_CRL_I']=df_TD_main_R['R_TD_CRL_I']
# df_important_data2['R_TD_CRL_E']=df_TD_main_R['R_TD_CRL_E']
# df_important_data2['R_MD_CRL_M']=df_TD_main_R['R_MD_CRL_M']
# df_important_data2['R_MD_CRL_I']=df_TD_main_R['R_MD_CRL_I']
# df_important_data2['R_MD_CRL_E']=df_TD_main_R['R_MD_CRL_E']
# df_important_data2['R_TN_Copulations']=df_TN_main_R['R_TN_Copulations']
# df_important_data2['R_LQ']=df_TN_main_R['R_LQ']
# df_important_data2['R_LQ_plus']=df_TN_main_R['R_LQ_plus']
# df_important_data2['R_LS']=df_TN_main_R['R_LS']
# df_important_data2['R_TN_Lordosis']=df_TN_main_R['R_TN_Lordosis']
# df_important_data2['R_Lordosis_extra']=df_TN_main_R['R_Lordosis_extra']
# df_important_data2['R_TN_Rejection']=df_TN_main_R['R_TN_Rejection']
# df_important_data2['R_TN_SB_sex']=df_TN_main_R['R_TN_SB_sex']
# df_important_data2['R_TD_SB_sex']=df_TD_main_R['R_TD_SB_sex']
# df_important_data2['R_MD_SB_sex']=df_TD_main_R['R_MD_SB_sex']
# df_important_data2['R_TN_TO_sex']=df_TN_main_R['R_TN_TO_sex']
# df_important_data2['R_TD_TO_sex']=df_TD_main_R['R_TD_TO_sex']
# df_important_data2['R_MD_TO_sex']=df_TD_main_R['R_MD_TO_sex']
# df_important_data2['R_MD_IMBI_sex']=df_TD_main_R['R_MD_IMBI_sex']

# # Create a dictionairy with the codes and explanations for the info sheet 
# dict_info={'Observation':'Name of observation','Experiment':'Experimental code','RatID':'RatID','Diet':'Diet treatment',
#             'Test':'Test day of the reward','Reward':'Reward type','Testreward':'Reward type and test day',
#             'T':'data from the total test','B':'data from baseline, before reward is introduced',
#             'I':'data from introduction of reward to lights on','A':'data from anticipatory phase, from lights on to door opening',
#             'P':'data from the introduction reward to door opening','R':'data from door opening to end of the test',
#             'TN':'Total number of the behaviors in complete test','TN_SC':'Total number of behaviors performed in start compartment',
#             'TN_RC':' Total number of behaviors performed in reward compartment','TD':'Total time spent on the behaviors in complete test',
#             'TD_SC':'Total time spent on the behaviors in the start compartment','TD_RC':'Total time spent on the behaviors in the reward compartment',
#             'L1B':'Latency to first behavior (start point depends on the phase that is investigated',
#             'Reward interest':'sniffing door +head towards door+close to door+rearing door',
#             'Food interaction':'eating, approach reward, sniffing reward and carrying food together',
#             'Sex interaction':'lordosis+paracopulatory+approach reward+sniffing reward+anogenital sniffing+allogrooming',
#             'reward anticipatory':'approach reward, sniffing reward, paracopulatory, sniffing anogenitally, allogrooming',
#             'Reward_consummatory':'eating,carrying food, lordosis',
#             'sc,rc':'start chamber, reward chamber',
#             'Copulations':'number of mounts, intromissions and ejaculations together',
#             'Lordosis':'Number of lordosis 1, 2 and 3 together',
#             'Lordosis_extra':'(L0+L1+L2+L3)-(total copulations)','TN_LM':'Number of lordosis upon mount (same for LI and LE with intromission and ejaculation',
#             'LQ':'lordosis quotient = lordosis1+lordosis2+lordosis3-extra lordosis/total copulations * 100%', 
#             'LS':'lordosis score = lordosis1*1+lordosis2*2+lordosis3*3/(total number of lordosis +l0)',
#             'LQ_plus':'LQ but with the extra lordoses, L1+L2+l3/total copulations*100%',
#             'Single eating':'Eating in eating bout consisting of just 1 eating episode',
#             'Single first eating':'Eating was the first (but only eating) behavior of an eating bout that had more eating-related behaviors',
#             'Single last eating':'Eating was the last (but only eating) behavior of an eating bout that had more eating-related behaviors',
#             'Single middle eating':'Eating was the middle (but only eating) behavior of an eating bout that had more eating-related behaviors',
#             'Eating starts EB':'Eating was the first behavior of an eating bout consisting of more eating and eating-related behaviors',
#             'Eating ends EB':'Eating was the last behavior of an eating bout consisting of more eating and eating-related behaviors',
#             'First eating in EB':'Eating was the first eating (but not eating-related) behavior of an eating bout consisting of more eating and eating-related behaviors',
#             'Last eating in EB':'Eating was the last (but not eating-related) behavior of an eating bout consisting of more eating and eating-related behaviors',
#             'Eating middle EB':'Eating was in the middle of an eating bout consisting of more eating and eating-related behaviors',
#             'EB':'Eating bouts, defined as eating episodes that are not interrupted by non-eating related behaviors. It starts and ends with eating',
#             'TO':'Time-outs, defined from end of eating of an eating bout until start of eating next eating bout',
#             'IMBI':'Mean time from (start of) first eating of one eating bout to the (start of) first eating of the next eating bout',
#             'SB': 'sex bout, has all parameters as eating bout, but then for sex behavior. Paracopulatory and lordosis 1-3 are included as relevant behaviors. Lordosis0 is a bout continuator, but not recorded as event. Chamber change is NOT a bout breaker',
#             'plus':'plus refers to the calculations on eating bouts in which carrying food is also an event, just like eating',
#             'CRL':'contact return latency is a new parameter that calculated the time it takes after a M/I/E that the female starts darting again'}


# # Make dataframe from dict_info for printing
# df_info= pd.DataFrame.from_dict(dict_info, orient='index')
# df_info.reset_index()

# print('dataframes finished')

# # Make dictionary with the result dataframes to save the dataframes to excel with total
# dfs_print={'Info':df_info,'TN_T':df_TN_main_T,'TN_B':df_TN_main_B,'TN_I':df_TN_main_I,'TN_A':df_TN_main_A,'TN_P':df_TN_main_P,'TN_R':df_TN_main_R,
#             'TD_T':df_TD_main_T,'TD_B':df_TD_main_B,'TD_I':df_TD_main_I,'TD_A':df_TD_main_A,'TD_P':df_TD_main_P,'TD_R':df_TD_main_R,
#             'L1_T':df_L1_main_T,'L1_B':df_L1_main_B,'L1_I':df_L1_main_I,'L1_A':df_L1_main_A,'L1_P':df_L1_main_P,'L1_R':df_L1_main_R,
#             'TN_extra_T':df_TN_extra_T,'TN_extra_R':df_TN_extra_R,
#             'TD_extra_T':df_TD_extra_T,'TD_extra_R':df_TD_extra_R,
#             'L1_extra_T':df_L1_extra_T,'L1_extra_R':df_L1_extra_R}

# dfs_print_important={'Info':df_info,'General':df_important_data1,'Behaviors':df_important_data2}

# # Save the dataframes to excel
# writer1 = pd.ExcelWriter(out_path1, engine='xlsxwriter')
# for sheetname, df in dfs_print.items():  # loop through `dict` of dataframes
#     df.to_excel(writer1, sheet_name=sheetname)  # send df to writer
#     worksheet = writer1.sheets[sheetname]  # pull worksheet object
#     for idx, col in enumerate(df):  # loop through all columns
#         series = df[col]
#         max_len = max((
#             series.astype(str).map(len).max(),  # len of largest item
#             len(str(series.name))  # len of column name/header
#             )) + 2  # adding a little extra space
#         worksheet.set_column(idx, idx, max_len)  # set column width
# writer1.save()
# writer1.close()

# writer2 = pd.ExcelWriter(out_path2, engine='xlsxwriter')
# for sheetname, df in dfs_print_important.items():  # loop through `dict` of dataframes
#     df.to_excel(writer2, sheet_name=sheetname)  # send df to writer
#     worksheet = writer2.sheets[sheetname]  # pull worksheet object
#     for idx, col in enumerate(df):  # loop through all columns
#         series = df[col]
#         max_len = max((
#             series.astype(str).map(len).max(),  # len of largest item
#             len(str(series.name))  # len of column name/header
#             )) + 2  # adding a little extra space
#         worksheet.set_column(idx, idx, max_len)  # set column width
# writer2.save()
# writer2.close()

# print('results printed')

# # Put all dataframes into a dictionary 
# dfs={'TN_T':df_TN_main_T,'TN_B':df_TN_main_B,'TN_I':df_TN_main_I,'TN_A':df_TN_main_A,'TN_P':df_TN_main_P,'TN_R':df_TN_main_R,
#             'TD_T':df_TD_main_T,'TD_B':df_TD_main_B,'TD_I':df_TD_main_I,'TD_A':df_TD_main_A,'TD_P':df_TD_main_P,'TD_R':df_TD_main_R,
#             'L1_T':df_L1_main_T,'L1_B':df_L1_main_B,'L1_I':df_L1_main_I,'L1_A':df_L1_main_A,'L1_P':df_L1_main_P,'L1_R':df_L1_main_R,
#             'TN_extra_T':df_TN_extra_T,'TN_extra_R':df_TN_extra_R,
#             'TD_extra_T':df_TD_extra_T,'TD_extra_R':df_TD_extra_R,
#             'L1_extra_T':df_L1_extra_T,'L1_extra_R':df_L1_extra_R}

# # # Statistics on data
# dict_results={'T':dict_results_T,'B':dict_results_B,'I':dict_results_I,'A':dict_results_A,'P':dict_results_P,'R':dict_results_R}

# # Create a list with statistical measures
# list_stat=['Mean','Median','Std','SEM','Q25','Q75','semedian','var']
# list_rewardid=['PRIMREWARD1','PRIMREWARD3','PRIMREWARD5','SECREWARD1','SECREWARD2','SECREWARD3',
#                 'DISREWARD1','PRIMREWARD_rev1','PRIMREWARD_rev3','SECREWARD_rev1']
# list_treat=['CTR','HFHS','CAF']

# # fill list of RatIDs for each group
# list_CTR=[]
# list_CAF=[]
# list_HFHS=[]

# for key,value in dict_diet.items():
#     if value == 'CTR':
#         list_CTR.append(key)
#     if value == 'CAF':
#         list_CAF.append(key)
#     if value == 'HFHS':
#         list_HFHS.append(key)
       
# # Create definition to fill dictionary with data per group      
# def groupdict(dictionary):
#     """
#     Parameters
#     ----------
#     dictionary : dictionary
#         Add dictionary from which statistics need to be done
#         e.g. dict_results_T, dict_results_B, dict_results_I, dict_results_A, dict_results_R, dict_results_P

#     Returns
#     -------
#     dict_groups : dictionary
#         Creates a dictionary with the statistical data per groups for statistics
    
#     """
    
#     # Create an empty dictionary with ID and behaviors
#     dict_groups={}
#     for key,parameters in dictionary.items():
#         for parameter,value in parameters.items():
#             dict_groups[parameter]={}
#             for t in list_rewardid:
#                 dict_groups[parameter][t]={}
#                 for d in list_treat:
#                     dict_groups[parameter][t][d]=[]

#     for key,parameters in dictionary.items():
#         for parameter,value in parameters.items():
#             for t in list_rewardid:
#                 for i in list_CTR:     
#                     if t in key and str(i) in key:
#                         dict_groups[parameter][t]['CTR'].append(value)
#                 for i in list_CAF:     
#                     if t in key and str(i) in key:
#                         dict_groups[parameter][t]['CAF'].append(value)
#                 for i in list_HFHS:     
#                     if t in key and str(i) in key:
#                         dict_groups[parameter][t]['HFHS'].append(value)
    
#     return dict_groups


# # Create definition to fill dictionary with statistics        
# def statsdict(dictionary_groups):
#     """
#     Parameters
#     ----------
#     dictionary : dictionary
#         Add dictionary made by groupdict definition
#         e.g. dict_group_T, dict_group_B, dict_group_I, dict_group_A, dict_group_P, dict_group_R

#     Returns
#     -------
#     dict_groups : dictionary
#         Creates a dictionary with the statistical data derived from the dictionary
#     """
    
#     # Create an empty dictionary with ID and behaviors
#     dict_stats={}
#     for parameters,rewardids in dictionary_groups.items():
#         dict_stats[parameters]={}
#         for rewardid,treats in rewardids.items():
#             dict_stats[parameters][rewardid]={}
#             for treat,values in treats.items():
#                 dict_stats[parameters][rewardid][treat]={}
#                 for i in list_stat:
#                     dict_stats[parameters][rewardid][treat][i]=[]

#     # # Fill dictionary with statistical measures
#     for parameters,rewardids in dictionary_groups.items():
#         for rewardid,treats in rewardids.items():
#             for treat,values in treats.items():
#                 dict_stats[parameters][rewardid][treat]['Mean']=np.nanmean(values)
#                 dict_stats[parameters][rewardid][treat]['Median']=np.nanmedian(values)
#                 dict_stats[parameters][rewardid][treat]['Std']=np.nanstd(values)
#                 dict_stats[parameters][rewardid][treat]['SEM']=np.nanstd(values)/np.sqrt(np.size(values))
#                 dict_stats[parameters][rewardid][treat]['Q25']=np.nanquantile(values,0.25)
#                 dict_stats[parameters][rewardid][treat]['Q75']=np.nanquantile(values,0.75)
#                 dict_stats[parameters][rewardid][treat]['semedian']=(dict_stats[parameters][rewardid][treat]['Q75']-dict_stats[parameters][rewardid][treat]['Q25'])/len(values)*1.34
#                 dict_stats[parameters][rewardid][treat]['var']=np.nanvar(values)
#                 dict_stats[parameters][rewardid][treat]['len']=len(values)
#     return dict_stats
# ###########################################################################################

# # Create groupdictionaries
# dict_group_T=groupdict(dict_results_T)
# dict_group_B=groupdict(dict_results_B)
# dict_group_I=groupdict(dict_results_I)
# dict_group_A=groupdict(dict_results_A)
# dict_group_P=groupdict(dict_results_P)
# dict_group_R=groupdict(dict_results_R)

# # Calculate statistics
# dict_stat_T=statsdict(dict_group_T)
# dict_stat_B=statsdict(dict_group_B)
# dict_stat_I=statsdict(dict_group_I)
# dict_stat_A=statsdict(dict_group_A)
# dict_stat_P=statsdict(dict_group_P)
# dict_stat_R=statsdict(dict_group_R)

# #########################################################################################################
# #########################################################################################################
# ################ ################ ################ ################  
# ################ ################ ################ ################  
# # Create a dictionary of all dictionaries, dataframes, and lists to store as pickle, and later get back 
# list_behaviordata=[dict_results_B,dict_results_I,dict_results_A,dict_results_P,dict_results_R,dict_results_T,
#                     dict_group_T,dict_group_B,dict_group_I,dict_group_A,dict_group_P,dict_group_R,
#                     dict_stat_T,dict_stat_B,dict_stat_I,dict_stat_A,dict_stat_P,dict_stat_R]
# list_behaviordata_names=["dict_results_B","dict_results_I","dict_results_A","dict_results_P","dict_results_R","dict_results_T",
#                           "dict_group_T","dict_group_B","dict_group_I","dict_group_A","dict_group_P","dict_group_R",
#                           "dict_stat_T","dict_stat_B","dict_stat_I","dict_stat_A","dict_stat_P","dict_stat_R"]

# # Change directory to output folder
# if not os.path.isdir(directory_pickle):
#     os.mkdir(directory_pickle)
# os.chdir(directory_pickle)

# # Save this dictionary as pickle file
# my_dict_behavior=dict(zip(list_behaviordata_names,list_behaviordata))
# with open("my_dict_behavior.pickle", "wb") as file:
#     pickle.dump(my_dict_behavior, file, protocol=pickle.HIGHEST_PROTOCOL)

# print("pickle_behavior saved")
# # Change directory back
# os.chdir(directory)

# ############### ################ ################ ################  
# ############### ################ ################ ################  

# ############## NEEDS FIXING ######################
# # Create dataframe from statistics
# def df_stat(dictionary_stat):
#     """Creates a dataframe from the statistical dictionary"""
#     df_stat=pd.DataFrame.from_dict({(i,j,k): dictionary_stat[i][j][k]
#                                for i in dictionary_stat.keys() 
#                                for j in dictionary_stat[i].keys()
#                                for k in dictionary_stat[i][j].keys()},
#                            orient='index')
    
#     return df_stat

# test=df_stat(dict_stat_R)
    
#         ########################################


# # Save the statistics to excel
# writer3 = pd.ExcelWriter(out_path3, engine='xlsxwriter')
# for sheetname, df in dfs_stat_print.items():  # loop through `dict` of dataframes
#     df.to_excel(writer3, sheet_name=sheetname)  # send df to writer
#     worksheet = writer3.sheets[sheetname]  # pull worksheet object
#     for idx, col in enumerate(df):  # loop through all columns
#         series = df[col]
#         max_len = max((
#             series.astype(str).map(len).max(),  # len of largest item
#             len(str(series.name))  # len of column name/header
#             )) + 1  # adding a little extra space
#         worksheet.set_column(idx, idx, max_len)  # set column width
# writer3.save()
# writer3.close()

print('statistics printed')
    
print('Behavioral data finished')

######################################################################################3
# Run dictionaries again for TDT analysis later so that animals will be excluded

# Delete the excluded rats from the metafile
for i in list_excltdt:
    metafile=metafile[metafile.RatID != i]
for s in list_excltdt_sex:
    metafile=metafile[(metafile.Test != 'SECREWARD') | ((metafile.Test == 'SECREWARD') & (metafile.RatID != s))]

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
#################################################################################################


# set font size for all figures
SMALL_SIZE = 16
MEDIUM_SIZE = 18
BIGGER_SIZE = 20
# plt.rcParams['font.size'] = 22 
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
custom_params = {"axes.spines.right": False, "axes.spines.top": False}        

color_snips='#95A5A6'
color_GCaMP='#117864'
color_GFP_snips='#7C6B39'
color_GFP='#F8D672'

color_scat_snips='#5F6A6A'
color_scat_GCaMP='#0E6251'
color_scat_GFP_snips='#d472bc'
color_scat_GFP='#57224a'

color_CTR='#5F6A6A'
color_HFHS='#9E3C86'
color_CAF='#117864'

color_CTR_shadow='#cacccc'
color_HFHS_shadow='#f7c1ea'
color_CAF_shadow='#afede1'
color_GFP_shadow='#FCF2D4'

color_scat_CTR='#4D5656'
color_scat_HFHS='#57224a'
color_scat_CAF='#0E6251'

color_S='#0f0b0f'
color_L='#fcf33a'
color_P='#e807c8'
color_E='#e807c8'
                     
# ##############################################################################################################################################################################
# # Analysis of TDT data from Synapse
# # Get a list of start times of behaviors per RAT-EXP-Code


def processdata(diet,test,testsession,metafile=file_TDT,virus="GCaMP6",method='Lerner'):
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
    metafile : string -> Default = file_TDT
        Code referring to the excel metafile document 
    virus : string -> Default = 'GCaMP6'
        Add which virus you want to analyze 
        e.g. "GCaMP6" or "GFP"
    method : string -> Default = 'Lerner'
        Add the method for dFF analysis you would like to use
        'Lerner' = uses a polyfit on the ISOS and GCaMP and average per 10 samples
        'Jaime' = uses another mathematical way from Konanur to substract ISOS from GCaMP 
                    -> it needs extra information that my code blocks (by normalize = False)

    Returns
    -------
    dict_dFF : dictionary & figure
        Processes the TDT data by correcting dFF signals (Lerner method is standard), z-score for the full test. 
        In addition, it removes the artifacts based on IQR standards, and re-calculates the dFF and z-score based on this new data.
        All data is stored in a new dictionary.
        The definition also creates a figure with the original and corrected dFF signals over the course of the full test with marking for eating or sex.
    """

    print("Start processing tdt data %s %s %s %s"%(virus,diet,test,testsession))
    
    # Make empty dictionaries
    dict_dFF={}
    
    # Read out the data of synapse per unique exp-rat-code and set in dictionary with GCAMP and ISOS
    for rat,v,t,d,ts,di,b,u,startbox,light in zip(list_ID,list_virus,list_test,list_diet,list_testsession,list_directory_tank,list_blue,list_uv,list_startbox,list_light):
        if v == virus:
            if t == test:
                if d == diet:
                    if ts == testsession:
                        BLOCKPATH= "%s"%(di)
                        print('Analyzing %s'%rat)
                        if path.exists(BLOCKPATH):
                            data= tdt.read_block(BLOCKPATH)
                            # Make some variables up here to so if they change in new recordings you won't have to change everything downstream
                            if b == '465_A':
                                GCAMP="_465A"
                                ISOS="_405A"
                                
                            else:
                                GCAMP="_465C"
                                ISOS="_405C"
                            
                            if startbox == 'PC0':
                                START_SIGNAL = 'PC0_'
                                LIGHT_SIGNAL = 'PC2_'
                            
                            else:
                                START_SIGNAL = 'PC1_'
                                LIGHT_SIGNAL = 'PC3_'

                            try:
                                START_on = data.epocs[START_SIGNAL].onset
                                START_off = data.epocs[START_SIGNAL].offset
                            except:
                                START_on = 1800
                                print("#### % has no start video signal #####"%rat)

                            try:
                                LIGHT_on = data.epocs[LIGHT_SIGNAL].onset
                                LIGHT_off = data.epocs[LIGHT_SIGNAL].offset
                            except:
                                LIGHT_on = 1800
                                print("#### % has no light on signal #####"%rat)

                            # Make a time array based on the number of samples and sample freq of 
                            # the demodulated streams
                            time = np.linspace(1,len(data.streams[GCAMP].data), len(data.streams[GCAMP].data))/data.streams[GCAMP].fs
                                    
                            #There is often a large artifact on the onset of LEDs turning on
                            #Remove data below a set time t
                            #Plot the demodulated strain without the beginning artifact
                            # Fix for Reward test
                            if LIGHT_on[-1] < 1800:
                                t=LIGHT_on[-1]-360
                            else: t=50
                            inds = np.where(time>t)
                            ind = inds[0][0]
                            time = time[ind:] # go from ind to final index
                            blue = data.streams[GCAMP].data[ind:]
                            uv = data.streams[ISOS].data[ind:]
                            
                            # Change directory to output folder
                            if not os.path.isdir(directory_TDT_fullgraphs):
                                os.mkdir(directory_TDT_fullgraphs)
        
                            os.chdir(directory_TDT_fullgraphs)
                            
                            try:
                                # Plot again at new time range
                                sns.set(style="ticks", rc=custom_params)
                                fig = plt.figure(figsize=(30, 18))
                                ax1 = fig.add_subplot(111)
                            
                                # Plotting the traces
                                p1, = ax1.plot(time,blue, linewidth=2, color=color_GCaMP, label='GCaMP')
                                p2, = ax1.plot(time,uv, linewidth=2, color='blueviolet', label='ISOS')
                                
                                ax1.set_ylabel('mV',fontsize=18)
                                ax1.set_xlabel('Seconds',fontsize=18)
                                ax1.set_title('Raw Demodulated Responses',fontsize=20)
                                ax1.legend(handles=[p1,p2],loc='upper right',fontsize=18)
                                fig.tight_layout()
                                
                                plt.savefig("%s_raw.jpg"%(rat))
                                plt.close(fig)
                                # Change directory back
                                os.chdir(directory)
                                print('%s Figure created '%rat)
       
                            except:
                                print('%s No figure created '%rat)
                                # Change directory back
                                os.chdir(directory)
        
                            if method == 'Lerner':
                                # Average around every Nth point and downsample Nx
                                N = 10  # Average every Nth samples into 1 value
                                F405 = []
                                F465 = []
                                time_cor=time
                                
                                for i in range(0, len(blue), N):
                                    F465.append(np.mean(blue[i:i+N-1])) # This is the moving window mean
                                blue_cor = F465
            
                                for i in range(0, len(uv), N):
                                    F405.append(np.mean(uv[i:i+N-1]))
                                uv_cor = F405
        
                                # Decimate time array to match length of demodulated stream
                                time_cor = time_cor[::N] # go from beginning to end of array in steps on N
                                time_cor = time_cor[:len(blue_cor)]
                                
                                fs = data.streams[GCAMP].fs/N
        
                                # x = np.array(uv_cor)
                                # y = np.array(blue_cor)
                                x = uv_cor
                                y = blue_cor
                                
                                try:
                                    bls = np.polyfit(x, y, 1)
                                    Y_fit_all = np.multiply(bls[0], x) + bls[1]
                                    blue_dF_all = y - Y_fit_all
                                    # Calculate the corrected signal in percentage
                                    dFF = np.multiply(100, np.divide(blue_dF_all, Y_fit_all))

                                except:
                                    print("##### % has signal length problem #####"%rat)
                                    dFF = []
        
        
                            elif method == 'Jaime':
                                ### In case you want to use the KONANUR method for correcting the signal #####
                                # Calculating dFF using Jaime's correction of the GCAMP versus ISOS signals
                                dFF=tp.processdata(blue, uv, normalize=False)
                                fs = data.streams[GCAMP].fs
                            
                            try:
                                zall = []
                                zb = np.mean(dFF)
                                zsd = np.std(dFF)
                                zall.append((dFF - zb)/zsd)
                               
                                zscore_dFF = np.mean(zall, axis=0)  
                            except:
                                zscore_dFF=[]
        
                            dict_dFF[rat]={}
                            dict_dFF[rat]['blue_raw']=blue
                            dict_dFF[rat]['uv_raw']=uv
                            dict_dFF[rat]['time_raw']=time
                            dict_dFF[rat]['blue']=blue_cor
                            dict_dFF[rat]['uv']=uv_cor
                            dict_dFF[rat]['dFF']=dFF
                            dict_dFF[rat]['zscore']=zscore_dFF
                            dict_dFF[rat]['START_on']=START_on[-1]
                            dict_dFF[rat]['START_off']=START_off[-1]
                            dict_dFF[rat]['LIGHT_on']=LIGHT_on[-1]
                            dict_dFF[rat]['LIGHT_off']=LIGHT_off[-1]
                            dict_dFF[rat]['time']=time_cor
                            dict_dFF[rat]['fs']=fs
                            print(rat)
                            print('Light on - ',LIGHT_on[-1])
                            print('Start on - ',START_on[-1])

        # Get the corrected dFF and z-scores when the drops in GCaMP signal are taken out
        # Get interquartile range of raw GCaMP and UV signal to delete outliers
    for rat,value in dict_dFF.items():    
        try:
            IQR_blue = []
            IQR_uv = []
            
            Q1_blue,Q3_blue = np.percentile(dict_dFF[rat]['blue_raw'],[25,75])
            Q1_uv,Q3_uv = np.percentile(dict_dFF[rat]['uv_raw'],[25,75])
    
            IQR_blue = Q3_blue-Q1_blue
            IQR_uv = Q3_uv-Q1_uv
            
            lower_fence_blue =Q1_blue-(2*IQR_blue) # increased it to 2 (instead of 1.5) to not miss the big signals
            higher_fence_blue =Q3_blue+(3*IQR_blue) 
    
            lower_fence_uv = Q1_uv-(2*IQR_uv)
            higher_fence_uv = Q3_uv+(2*IQR_uv)
                        
        except:
            print('no IQR calculated')

        # Delete all GCaMP and UV that are outliers
        temp_blue=list(dict_dFF[rat]['blue_raw'])
        temp_uv=list(dict_dFF[rat]['uv_raw'])
        temp_time=list(dict_dFF[rat]['time_raw'])
        time_new=[]
        blue_new=[]
        uv_new=[]

        if rat in dict_manual_adjustments['Cut_start'].keys():
            cut_start=dict_manual_adjustments['Cut_start'][rat]
            cut_end=dict_manual_adjustments['Cut_end'][rat]
        else:
            cut_start=1800
            cut_end=0

        blue_new_temp=[b for b,u,t in zip(temp_blue,temp_uv,temp_time) if b>lower_fence_blue and b<higher_fence_blue and u>lower_fence_uv and u<higher_fence_uv and (t<cut_start or t>cut_end)] 
        uv_new_temp=[u for b,u,t in zip(temp_blue,temp_uv,temp_time) if b>lower_fence_blue and b<higher_fence_blue and u>lower_fence_uv and u<higher_fence_uv and (t<cut_start or t>cut_end)] 
        time_new_temp=[t for b,u,t in zip(temp_blue,temp_uv,temp_time) if b>lower_fence_blue and b<higher_fence_blue and u>lower_fence_uv and u<higher_fence_uv and (t<cut_start or t>cut_end)] 

        for b in blue_new_temp:
            blue_new.append(b)
        for u in uv_new_temp:
            uv_new.append(u)
        for t in time_new_temp:
            time_new.append(t)

        # Change directory to output folder
        if not os.path.isdir(directory_TDT_fullgraphs):
            os.mkdir(directory_TDT_fullgraphs)

        os.chdir(directory_TDT_fullgraphs)

        try:
            # Plot again at new time range
            sns.set(style="ticks", rc=custom_params)
            fig = plt.figure(figsize=(30, 18))
            ax1 = fig.add_subplot(111)
        
            # Plotting the traces
            p1, = ax1.plot(time_new,blue_new, linewidth=2, color=color_GCaMP, label='GCaMP')
            p2, = ax1.plot(time_new,uv_new, linewidth=2, color='blueviolet', label='ISOS')
            
            ax1.set_ylabel('mV',fontsize=18)
            ax1.set_xlabel('Seconds',fontsize=18)
            ax1.set_title('Raw Demodulated Responses with Outliers Removed',fontsize=20)
            # ax1.legend(handles=[p1,p2],loc='upper right',fontsize=18)
            fig.tight_layout()
            
            plt.savefig("%s_raw_cor.jpg"%(rat))
            plt.close(fig)
            # Change directory back
            os.chdir(directory)
            print('%s Figure without outliers created '%rat)

        except:
            print('%s No figure created '%rat)
            # Change directory back
            os.chdir(directory)

        if method == 'Lerner':
            # Average around every Nth point and downsample Nx
            N = 10  # Average every Nth samples into 1 value
            F405_new = []
            F465_new = []
           
            for i in range(0, len(blue_new), N):
                F465_new.append(np.mean(blue_new[i:i+N-1])) # This is the moving window mean
            blue_new = F465_new
    
            for i in range(0, len(uv_new), N):
                F405_new.append(np.mean(uv_new[i:i+N-1]))
            uv_new = F405_new
    
            # Decimate time array to match length of demodulated stream
            time_new = time_new[::N] # go from beginning to end of array in steps on N
            time_new = time_new[:len(blue_new)]
            
            x_new = np.array(uv_new)
            y_new = np.array(blue_new)
            
            try:
                bls_new = np.polyfit(x_new, y_new, 1)
                Y_fit_all_new = np.multiply(bls_new[0], x_new) + bls_new[1]
                blue_dF_all_new = y_new - Y_fit_all_new
                # Calculate the corrected signal in percentage
                dFF_new = np.multiply(100, np.divide(blue_dF_all_new, Y_fit_all_new))
                
            except:
                print("##### % has signal length problem #####"%rat)
                dFF_new = []
            
        elif method == 'Jaime':
            ### In case you want to use the KONANUR method for correcting the signal #####
            # Calculating dFF using Jaime's correction of the GCAMP versus ISOS signals
            dFF_new=tp.processdata(blue_new, uv_new, normalize=False)
        
        try:
            zall_new = []
            zb_new = np.mean(dFF_new)
            zsd_new = np.std(dFF_new)
            zall_new.append((dFF_new - zb_new)/zsd_new)
           
            zscore_dFF_new = np.mean(zall_new, axis=0)  
        except:
            zscore_dFF_new=[]

        dict_dFF[rat]['blue_cor']=blue_new
        dict_dFF[rat]['uv_cor']=uv_new
        dict_dFF[rat]['dFF_cor']=dFF_new
        dict_dFF[rat]['zscore_cor']=zscore_dFF_new
        dict_dFF[rat]['time_cor']=time_new

        # Delete the raw data from dictionary to make the dictionary smaller in storage size
        del dict_dFF[rat]['blue_raw']
        del dict_dFF[rat]['uv_raw']
        del dict_dFF[rat]['time_raw']

    # Get the start times of eating, paracopulatory and lordosis behavior -> and mark in figure
    dict_start_beh={}
    for key in dict_dFF.keys():
        dict_start_beh[key]={}
        for beh in list_behmark:
            dict_start_beh[key][beh]=[]

    for rat,value in dict_dFF.items():    
        for behav in list_behmark:
            if dict_dFF[rat]['LIGHT_on']:
                if rat in dict_light.keys():
                    LIGHT_on=dict_dFF[rat]['LIGHT_on']
                    LIGHT_video=dict_light[rat]
                    delay=LIGHT_on-LIGHT_video
                    
                    df_reduced = data_T[(data_T['ID'] == rat) & (data_T[BEH] == behav)]
                    temp_start = list(df_reduced['Beh_start']+ delay)
                    dict_start_beh[rat][behav]=temp_start 
                else:
                    dict_start_beh[rat][behav]=[]
        temp=[]
        for i in dict_start_beh[rat][BU]:
            temp.append(i)
        for j in dict_start_beh[rat][BV]:
            temp.append(j)
        for k in dict_start_beh[rat][BW]:
            temp.append(k)
        dict_start_beh[rat]['lordosis']=temp

    # Get the end times of eating, paracopulatory and lordosis behavior -> and mark in figure
    dict_end_beh={}
    for key in dict_dFF.keys():
        dict_end_beh[key]={}
        for beh in list_behmark:
            dict_end_beh[key][beh]=[]

    for rat,value in dict_dFF.items():    
        for behav in list_behmark:
            if dict_dFF[rat]['START_on']:
                if rat in dict_light.keys():
                    LIGHT_on=dict_dFF[rat]['LIGHT_on']
                    LIGHT_video=dict_light[rat]
                    delay=LIGHT_on-LIGHT_video
            
                    df_reduced = data_T[(data_T['ID'] == rat) & (data_T[BEH] == behav)]
                    temp_end = list(df_reduced['Beh_end']+ delay)
                    dict_end_beh[rat][behav]=temp_end 
                else:
                    dict_end_beh[rat][behav]=[]
        temp=[]
        for i in dict_end_beh[rat][BU]:
            temp.append(i)
        for j in dict_end_beh[rat][BV]:
            temp.append(j)
        for k in dict_end_beh[rat][BW]:
            temp.append(k)
        dict_end_beh[rat]['lordosis']=temp
    
    # Read out the data from the dFF dictionary and link to behavior
    for rat,value in dict_dFF.items():
        # First make a continous time series of behavior events (epocs) and plot
        EATING_on = dict_start_beh[rat][BO] if dict_start_beh[rat][BO] else [0,0]
        EATING_off = dict_end_beh[rat][BO] if dict_end_beh[rat][BO] else [0,0]
        PARA_on = dict_start_beh[rat][BP] if dict_start_beh[rat][BP] else [0,0]
        PARA_off = dict_end_beh[rat][BP] if dict_end_beh[rat][BP] else [0,0]
        LORDOSIS_on = dict_start_beh[rat]['lordosis'] if dict_start_beh[rat]['lordosis'] else [0,0]
        LORDOSIS_off = dict_end_beh[rat]['lordosis'] if dict_end_beh[rat]['lordosis'] else [0,0]
        
        # Add the first and last time stamps to make tails on the TTL stream
        START_on = dict_dFF[rat]['START_on']
        START_off = dict_dFF[rat]['START_off']
        LIGHT_on = dict_dFF[rat]['LIGHT_on']
        LIGHT_off = dict_dFF[rat]['LIGHT_off']
        print(rat,LIGHT_on,LIGHT_off)
        
        # Add the first and last time stamps to make tails on the TTL stream
        EATING_x = np.append(np.append(dict_dFF[rat]['time'][0], np.reshape(np.kron([EATING_on, EATING_off],
                            np.array([[1], [1]])).T, [1,-1])[0]), dict_dFF[rat]['time'][-1])
        sz_F = len(EATING_on)
        d_F=[0.1]*sz_F

        PARA_x = np.append(np.append(dict_dFF[rat]['time'][0], np.reshape(np.kron([PARA_on,PARA_off],
                            np.array([[1], [1]])).T, [1,-1])[0]), dict_dFF[rat]['time'][-1])
        sz_M = len(PARA_on)
        d_M=[0.1]*sz_M
        
        LORDOSIS_x = np.append(np.append(dict_dFF[rat]['time'][0], np.reshape(np.kron([LORDOSIS_on, LORDOSIS_off],
                            np.array([[1], [1]])).T, [1,-1])[0]), dict_dFF[rat]['time'][-1])
        sz_I = len(LORDOSIS_on)
        d_I=[0.1]*sz_I
        
        # Add zeros to beginning and end of 0,1 value array to match len of LICK_x
        EATING_y = np.append(np.append(0,np.reshape(np.vstack([np.zeros(sz_F),
            d_F, d_F, np.zeros(sz_F)]).T, [1, -1])[0]),0)

        PARA_y = np.append(np.append(0,np.reshape(np.vstack([np.zeros(sz_M),
            d_M, d_M, np.zeros(sz_M)]).T, [1, -1])[0]),0)
        
        LORDOSIS_y = np.append(np.append(0,np.reshape(np.vstack([np.zeros(sz_I),
            d_I, d_I, np.zeros(sz_I)]).T, [1, -1])[0]),0)
        
        
        y_scale = 30 # adjust according to data needs
        y_shift = -10 #scale and shift are just for asthetics

        
        if method == 'Lerner' and virus== 'GCaMP6':
            try:
                # First subplot in a series: dFF with lick epocs
                os.chdir(directory_TDT_fullgraphs)
                fig = plt.figure(figsize=(30,8))
                ax = fig.add_subplot(111)
                
                p1, = ax.plot(dict_dFF[rat]['time'], dict_dFF[rat]['dFF'], linewidth=2, color=color_GCaMP, label=virus)
                p2 = ax.axvline(x=LIGHT_on, linewidth=3, color=color_S, label="Light on")
                p3 = ax.axvline(x=LIGHT_off, linewidth=3, color=color_S, label="Door open")
                p4, = ax.plot(EATING_x, y_scale*EATING_y+y_shift, linewidth=2, color=color_E, label='Eating')
                p5, = ax.plot(PARA_x, y_scale*PARA_y+y_shift, linewidth=2, color=color_P, label='Paracopulatory')
                p6, = ax.plot(LORDOSIS_x, y_scale*LORDOSIS_y+y_shift, linewidth=2, color=color_L, label='Lordosis')
                
                for on, off in zip(EATING_on,EATING_off):
                    ax.axvspan(on, off, alpha=0.25, color=color_E, label='Eating')
                for on, off in zip(PARA_on,PARA_off):
                    ax.axvspan(on, off, alpha=0.25, color=color_P, label='Paracopulatory')
                for on, off in zip(LORDOSIS_on, LORDOSIS_off):
                    ax.axvspan(on, off, alpha=0.25, color=color_L, label='Lordosis')
                
                ax.set_ylabel(r'$\Delta$F/F (%)',fontsize=18)
                ax.set_xlabel('Seconds',fontsize=18)
                # ax.set_yticks(yy)
                if 'SEC' in rat:
                    ax.legend(handles=[p2,p3,p5,p6], loc='upper right',fontsize=18)
                else:
                    ax.legend(handles=[p2,p3,p4], loc='upper right',fontsize=18)
                fig.tight_layout()
                plt.savefig("%s %s %s %s.jpg"%(rat, diet, virus, method))
                plt.close(fig)
    
                # Change directory back
                os.chdir(directory)
                print('%s Figure with marks created '%rat)

            except:
                print('%s No BEHMARK figures created '%rat)
                plt.close('all')
                # Change directory back
                os.chdir(directory)

            try:
                # First subplot in a series: dFF with lick epocs
                os.chdir(directory_TDT_fullgraphs)
                fig2 = plt.figure(figsize=(30,8))
                ax2 = fig2.add_subplot(111)
                
                p1, = ax2.plot(dict_dFF[rat]['time_cor'], dict_dFF[rat]['dFF_cor'], linewidth=2, color=color_GCaMP, label=virus)
                p2 = ax2.axvline(x=LIGHT_on, linewidth=3, color=color_S, label="Light on")
                p3 = ax2.axvline(x=LIGHT_off, linewidth=3, color=color_S, label="Door open")
                p4, = ax2.plot(EATING_x, y_scale*EATING_y+y_shift, linewidth=2, color=color_E, label='Eating')
                p5, = ax2.plot(PARA_x, y_scale*PARA_y+y_shift, linewidth=2, color=color_P, label='Paracopulatory')
                p6, = ax2.plot(LORDOSIS_x, y_scale*LORDOSIS_y+y_shift, linewidth=2, color=color_L, label='Lordosis')
                
                for on, off in zip(EATING_on,EATING_off):
                    ax2.axvspan(on, off, alpha=0.25, color=color_E, label='Eating')
                for on, off in zip(PARA_on,PARA_off):
                    ax2.axvspan(on, off, alpha=0.25, color=color_P, label='Paracopulatory')
                for on, off in zip(LORDOSIS_on, LORDOSIS_off):
                    ax2.axvspan(on, off, alpha=0.25, color=color_L, label='Lordosis')
                
                ax2.set_ylabel(r'$\Delta$F/F (%)',fontsize=18)
                ax2.set_xlabel('Seconds',fontsize=18)
                # ax2.set_yticks(yy)
                if 'SEC' in rat:
                    ax2.legend(handles=[p2,p3,p5,p6], loc='upper right',fontsize=18)
                else:
                    ax2.legend(handles=[p2,p3,p4], loc='upper right',fontsize=18)
                fig2.tight_layout()
                plt.savefig("%s %s %s %s cor.jpg"%(rat, diet, virus, method))
                plt.close(fig2)

                # Change directory back
                os.chdir(directory)
                print('%s Figure without outliers and with marks created '%rat)

            except:
                print('%s No BEHMARK figure cor created '%rat)
                plt.close('all')
                # Change directory back
                os.chdir(directory)

        else:
            os.chdir(directory_TDT_fullgraphs)
            fig = plt.figure(figsize=(30,8))
            ax = fig.add_subplot(111)
            
            p1, = ax.plot(dict_dFF[rat]['time'], dict_dFF[rat]['dFF'], linewidth=2, color=color_GCaMP, label='GCaMP')
            
            ax.set_ylabel(r'$\Delta$F/F',fontsize=18)
            ax.set_xlabel('Seconds',fontsize=18)
            ax.set_title(r'%s - $\Delta$F/F',fontsize=18)
            fig.tight_layout()
            plt.savefig("%s %s %s %s.jpg"%(rat, diet, virus, method))
            plt.close(fig)

            fig2 = plt.figure(figsize=(30,8))
            ax2 = fig2.add_subplot(111)
            
            p1, = ax2.plot(dict_dFF[rat]['time_cor'], dict_dFF[rat]['dFF_cor'], linewidth=2, color=color_GCaMP, label='GCaMP')
            
            ax2.set_ylabel(r'$\Delta$F/F',fontsize=18)
            ax2.set_xlabel('Seconds',fontsize=18)
            ax2.set_title(r'%s - $\Delta$F/F',fontsize=18)
            fig2.tight_layout()
            plt.savefig("%s %s %s %s cor.jpg"%(rat, diet, virus, method))
            plt.close(fig2)

            # Change directory back
            os.chdir(directory)
        
    print('data processing done')
    return dict_dFF

print('definition data processing made')



    ####################################################################################################
    
# Run the data analysis for each test separate
# GCAMP PRIMREWARD
dict_dFF_GCaMP6_CAF_PRIMREWARD_1=processdata("CAF","PRIMREWARD",1)        
dict_dFF_GCaMP6_HFHS_PRIMREWARD_1=processdata("HFHS","PRIMREWARD",1)        
dict_dFF_GCaMP6_CTR_PRIMREWARD_1=processdata("CTR","PRIMREWARD",1)        

dict_dFF_GCaMP6_CAF_PRIMREWARD_3=processdata("CAF","PRIMREWARD",3)        
dict_dFF_GCaMP6_HFHS_PRIMREWARD_3=processdata("HFHS","PRIMREWARD",3)        
dict_dFF_GCaMP6_CTR_PRIMREWARD_3=processdata("CTR","PRIMREWARD",3)        

dict_dFF_GCaMP6_CAF_PRIMREWARD_5=processdata("CAF","PRIMREWARD",5)        
dict_dFF_GCaMP6_HFHS_PRIMREWARD_5=processdata("HFHS","PRIMREWARD",5)        
dict_dFF_GCaMP6_CTR_PRIMREWARD_5=processdata("CTR","PRIMREWARD",5)  

# GCaMP6 SECREWARD
dict_dFF_GCaMP6_CAF_SECREWARD_1=processdata("CAF","SECREWARD",1)        
dict_dFF_GCaMP6_HFHS_SECREWARD_1=processdata("HFHS","SECREWARD",1)        
dict_dFF_GCaMP6_CTR_SECREWARD_1=processdata("CTR","SECREWARD",1)        

dict_dFF_GCaMP6_CAF_SECREWARD_2=processdata("CAF","SECREWARD",2)        
dict_dFF_GCaMP6_HFHS_SECREWARD_2=processdata("HFHS","SECREWARD",2)        
dict_dFF_GCaMP6_CTR_SECREWARD_2=processdata("CTR","SECREWARD",2)

dict_dFF_GCaMP6_CAF_SECREWARD_3=processdata("CAF","SECREWARD",3)        
dict_dFF_GCaMP6_HFHS_SECREWARD_3=processdata("HFHS","SECREWARD",3)        
dict_dFF_GCaMP6_CTR_SECREWARD_3=processdata("CTR","SECREWARD",3)        
 
# # GCaMP6 PRIMREWARD_rev_REVERSED
dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_1=processdata("CAF","PRIMREWARD_rev",1)        
dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_1=processdata("HFHS","PRIMREWARD_rev",1)        
dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_1=processdata("CTR","PRIMREWARD_rev",1)        

dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_3=processdata("CAF","PRIMREWARD_rev",3)        
dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_3=processdata("HFHS","PRIMREWARD_rev",3)        
dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_3=processdata("CTR","PRIMREWARD_rev",3)        

# GCaMP6 SECREWARD_rev_REVERSED
dict_dFF_GCaMP6_CAF_SECREWARD_rev_1=processdata("CAF","SECREWARD_rev",1)        
dict_dFF_GCaMP6_HFHS_SECREWARD_rev_1=processdata("HFHS","SECREWARD_rev",1)        
dict_dFF_GCaMP6_CTR_SECREWARD_rev_1=processdata("CTR","SECREWARD_rev",1)        

# # GCaMP6 DISREWARD
dict_dFF_GCaMP6_CAF_DISREWARD_1=processdata("CAF","DISREWARD",1)        
dict_dFF_GCaMP6_HFHS_DISREWARD_1=processdata("HFHS","DISREWARD",1)        
dict_dFF_GCaMP6_CTR_DISREWARD_1=processdata("CTR","DISREWARD",1)        

# # GFP PRIMREWARD
dict_dFF_GFP_CAF_PRIMREWARD_1=processdata("CAF","PRIMREWARD",1,virus='GFP')        
dict_dFF_GFP_HFHS_PRIMREWARD_1=processdata("HFHS","PRIMREWARD",1,virus='GFP')        
dict_dFF_GFP_CTR_PRIMREWARD_1=processdata("CTR","PRIMREWARD",1,virus='GFP')        

dict_dFF_GFP_CAF_PRIMREWARD_3=processdata("CAF","PRIMREWARD",3,virus='GFP')        
dict_dFF_GFP_HFHS_PRIMREWARD_3=processdata("HFHS","PRIMREWARD",3,virus='GFP')        
dict_dFF_GFP_CTR_PRIMREWARD_3=processdata("CTR","PRIMREWARD",3,virus='GFP')        

dict_dFF_GFP_CAF_PRIMREWARD_5=processdata("CAF","PRIMREWARD",5,virus='GFP')        
dict_dFF_GFP_HFHS_PRIMREWARD_5=processdata("HFHS","PRIMREWARD",5,virus='GFP')        
dict_dFF_GFP_CTR_PRIMREWARD_5=processdata("CTR","PRIMREWARD",5,virus='GFP')  

# GFP SECREWARD
dict_dFF_GFP_CAF_SECREWARD_1=processdata("CAF","SECREWARD",1,virus='GFP')        
dict_dFF_GFP_HFHS_SECREWARD_1=processdata("HFHS","SECREWARD",1,virus='GFP')        
dict_dFF_GFP_CTR_SECREWARD_1=processdata("CTR","SECREWARD",1,virus='GFP')        

dict_dFF_GFP_CAF_SECREWARD_2=processdata("CAF","SECREWARD",2,virus='GFP')        
dict_dFF_GFP_HFHS_SECREWARD_2=processdata("HFHS","SECREWARD",2,virus='GFP')        
dict_dFF_GFP_CTR_SECREWARD_2=processdata("CTR","SECREWARD",2,virus='GFP')

dict_dFF_GFP_CAF_SECREWARD_3=processdata("CAF","SECREWARD",3,virus='GFP')        
dict_dFF_GFP_HFHS_SECREWARD_3=processdata("HFHS","SECREWARD",3,virus='GFP')        
dict_dFF_GFP_CTR_SECREWARD_3=processdata("CTR","SECREWARD",3,virus='GFP')        

# # GFP PRIMREWARD_rev_REVERSED
dict_dFF_GFP_CAF_PRIMREWARD_rev_1=processdata("CAF","PRIMREWARD_rev",1,virus='GFP')        
dict_dFF_GFP_HFHS_PRIMREWARD_rev_1=processdata("HFHS","PRIMREWARD_rev",1,virus='GFP')        
dict_dFF_GFP_CTR_PRIMREWARD_rev_1=processdata("CTR","PRIMREWARD_rev",1,virus='GFP')        

dict_dFF_GFP_CAF_PRIMREWARD_rev_3=processdata("CAF","PRIMREWARD_rev",3,virus='GFP')        
dict_dFF_GFP_HFHS_PRIMREWARD_rev_3=processdata("HFHS","PRIMREWARD_rev",3,virus='GFP')        
dict_dFF_GFP_CTR_PRIMREWARD_rev_3=processdata("CTR","PRIMREWARD_rev",3,virus='GFP')        

# GFP SECREWARD_rev_REVERSED
dict_dFF_GFP_CAF_SECREWARD_rev_1=processdata("CAF","SECREWARD_rev",1,virus='GFP')        
dict_dFF_GFP_HFHS_SECREWARD_rev_1=processdata("HFHS","SECREWARD_rev",1,virus='GFP')        
dict_dFF_GFP_CTR_SECREWARD_rev_1=processdata("CTR","SECREWARD_rev",1,virus='GFP')        

# # GFP DISREWARD
dict_dFF_GFP_CAF_DISREWARD_1=processdata("CAF","DISREWARD",1,virus='GFP')        
dict_dFF_GFP_HFHS_DISREWARD_1=processdata("HFHS","DISREWARD",1,virus='GFP')        
dict_dFF_GFP_CTR_DISREWARD_1=processdata("CTR","DISREWARD",1,virus='GFP')        


##################### ########################### ############################## ############################################
##################### ########################### ############################## ############################################
# to save as pickle
# Create pickle dictionary 
list_processdata=[dict_dFF_GCaMP6_CAF_PRIMREWARD_1,dict_dFF_GCaMP6_CAF_PRIMREWARD_3,dict_dFF_GCaMP6_CAF_PRIMREWARD_5,
                  dict_dFF_GCaMP6_CAF_SECREWARD_1,dict_dFF_GCaMP6_CAF_SECREWARD_2,dict_dFF_GCaMP6_CAF_SECREWARD_3,
                  dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_1,dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_3,dict_dFF_GCaMP6_CAF_SECREWARD_rev_1,
                  dict_dFF_GCaMP6_CAF_DISREWARD_1,
                  dict_dFF_GCaMP6_CTR_PRIMREWARD_1,dict_dFF_GCaMP6_CTR_PRIMREWARD_3,dict_dFF_GCaMP6_CTR_PRIMREWARD_5,
                  dict_dFF_GCaMP6_CTR_SECREWARD_1,dict_dFF_GCaMP6_CTR_SECREWARD_2,dict_dFF_GCaMP6_CTR_SECREWARD_3,
                  dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_1,dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_3,dict_dFF_GCaMP6_CTR_SECREWARD_rev_1,
                  dict_dFF_GCaMP6_CTR_DISREWARD_1,
                  dict_dFF_GCaMP6_HFHS_PRIMREWARD_1,dict_dFF_GCaMP6_HFHS_PRIMREWARD_3,dict_dFF_GCaMP6_HFHS_PRIMREWARD_5,
                  dict_dFF_GCaMP6_HFHS_SECREWARD_1,dict_dFF_GCaMP6_HFHS_SECREWARD_2,dict_dFF_GCaMP6_HFHS_SECREWARD_3,
                  dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_1,dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_3,dict_dFF_GCaMP6_HFHS_SECREWARD_rev_1,
                  dict_dFF_GCaMP6_HFHS_DISREWARD_1,  
                  dict_dFF_GFP_CAF_PRIMREWARD_1,dict_dFF_GFP_CAF_PRIMREWARD_3,dict_dFF_GFP_CAF_PRIMREWARD_5,
                  dict_dFF_GFP_CAF_SECREWARD_1,dict_dFF_GFP_CAF_SECREWARD_2,dict_dFF_GFP_CAF_SECREWARD_3,
                  dict_dFF_GFP_CAF_PRIMREWARD_rev_1,dict_dFF_GFP_CAF_PRIMREWARD_rev_3,dict_dFF_GFP_CAF_SECREWARD_rev_1,
                  dict_dFF_GFP_CAF_DISREWARD_1,
                  dict_dFF_GFP_CTR_PRIMREWARD_1,dict_dFF_GFP_CTR_PRIMREWARD_3,dict_dFF_GFP_CTR_PRIMREWARD_5,
                  dict_dFF_GFP_CTR_SECREWARD_1,dict_dFF_GFP_CTR_SECREWARD_2,dict_dFF_GFP_CTR_SECREWARD_3,
                  dict_dFF_GFP_CTR_PRIMREWARD_rev_1,dict_dFF_GFP_CTR_PRIMREWARD_rev_3,dict_dFF_GFP_CTR_SECREWARD_rev_1,
                  dict_dFF_GFP_CTR_DISREWARD_1,
                  dict_dFF_GFP_HFHS_PRIMREWARD_1,dict_dFF_GFP_HFHS_PRIMREWARD_3,dict_dFF_GFP_HFHS_PRIMREWARD_5,
                  dict_dFF_GFP_HFHS_SECREWARD_1,dict_dFF_GFP_HFHS_SECREWARD_2,dict_dFF_GFP_HFHS_SECREWARD_3,
                  dict_dFF_GFP_HFHS_PRIMREWARD_rev_1,dict_dFF_GFP_HFHS_PRIMREWARD_rev_3,dict_dFF_GFP_HFHS_SECREWARD_rev_1,
                  dict_dFF_GFP_HFHS_DISREWARD_1]

list_processdata_names=["dict_dFF_GCaMP6_CAF_PRIMREWARD_1","dict_dFF_GCaMP6_CAF_PRIMREWARD_3","dict_dFF_GCaMP6_CAF_PRIMREWARD_5",
                  "dict_dFF_GCaMP6_CAF_SECREWARD_1","dict_dFF_GCaMP6_CAF_SECREWARD_2","dict_dFF_GCaMP6_CAF_SECREWARD_3",
                  "dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_1","dict_dFF_GCaMP6_CAF_PRIMREWARD_rev_3","dict_dFF_GCaMP6_CAF_SECREWARD_rev_1",
                  "dict_dFF_GCaMP6_CAF_DISREWARD_1",
                  "dict_dFF_GCaMP6_CTR_PRIMREWARD_1","dict_dFF_GCaMP6_CTR_PRIMREWARD_3","dict_dFF_GCaMP6_CTR_PRIMREWARD_5",
                  "dict_dFF_GCaMP6_CTR_SECREWARD_1","dict_dFF_GCaMP6_CTR_SECREWARD_2","dict_dFF_GCaMP6_CTR_SECREWARD_3",
                  "dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_1","dict_dFF_GCaMP6_CTR_PRIMREWARD_rev_3","dict_dFF_GCaMP6_CTR_SECREWARD_rev_1",
                  "dict_dFF_GCaMP6_CTR_DISREWARD_1",
                  "dict_dFF_GCaMP6_HFHS_PRIMREWARD_1","dict_dFF_GCaMP6_HFHS_PRIMREWARD_3","dict_dFF_GCaMP6_HFHS_PRIMREWARD_5",
                  "dict_dFF_GCaMP6_HFHS_SECREWARD_1","dict_dFF_GCaMP6_HFHS_SECREWARD_2","dict_dFF_GCaMP6_HFHS_SECREWARD_3",
                  "dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_1","dict_dFF_GCaMP6_HFHS_PRIMREWARD_rev_3","dict_dFF_GCaMP6_HFHS_SECREWARD_rev_1",
                  "dict_dFF_GCaMP6_HFHS_DISREWARD_1",  
                  "dict_dFF_GFP_CAF_PRIMREWARD_1","dict_dFF_GFP_CAF_PRIMREWARD_3","dict_dFF_GFP_CAF_PRIMREWARD_5",
                  "dict_dFF_GFP_CAF_SECREWARD_1","dict_dFF_GFP_CAF_SECREWARD_2","dict_dFF_GFP_CAF_SECREWARD_3",
                  "dict_dFF_GFP_CAF_PRIMREWARD_rev_1","dict_dFF_GFP_CAF_PRIMREWARD_rev_3","dict_dFF_GFP_CAF_SECREWARD_rev_1",
                  "dict_dFF_GFP_CAF_DISREWARD_1",
                  "dict_dFF_GFP_CTR_PRIMREWARD_1","dict_dFF_GFP_CTR_PRIMREWARD_3","dict_dFF_GFP_CTR_PRIMREWARD_5",
                  "dict_dFF_GFP_CTR_SECREWARD_1","dict_dFF_GFP_CTR_SECREWARD_2","dict_dFF_GFP_CTR_SECREWARD_3",
                  "dict_dFF_GFP_CTR_PRIMREWARD_rev_1","dict_dFF_GFP_CTR_PRIMREWARD_rev_3","dict_dFF_GFP_CTR_SECREWARD_rev_1",
                  "dict_dFF_GFP_CTR_DISREWARD_1",
                  "dict_dFF_GFP_HFHS_PRIMREWARD_1","dict_dFF_GFP_HFHS_PRIMREWARD_3","dict_dFF_GFP_HFHS_PRIMREWARD_5",
                  "dict_dFF_GFP_HFHS_SECREWARD_1","dict_dFF_GFP_HFHS_SECREWARD_2","dict_dFF_GFP_HFHS_SECREWARD_3",
                  "dict_dFF_GFP_HFHS_PRIMREWARD_rev_1","dict_dFF_GFP_HFHS_PRIMREWARD_rev_3","dict_dFF_GFP_HFHS_SECREWARD_rev_1",
                  "dict_dFF_GFP_HFHS_DISREWARD_1"]

os.chdir(directory_pickle)

my_dict_process=dict(zip(list_processdata_names,list_processdata))
with open("my_dict_process_cor.pickle", "wb") as file:
    pickle.dump(my_dict_process, file, protocol=pickle.HIGHEST_PROTOCOL)
# Change directory back
os.chdir(directory)

print("pickle_tdt saved")

#################### ########################### ############################### ###########################################
#################### ########################### ############################### ###########################################


