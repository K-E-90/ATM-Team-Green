# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 01:15:31 2019

@author: koen
"""

import numpy as np

def clear_all():
    #Clears all the variables from the workspace of the spyder application.
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue

        del globals()[var]

clear_all()

def incr_time(time,incr):
    ho = int(time.split(':')[0])
    mi = int(time.split(':')[1])
    se = float(time.split(':')[2])
    
    se += incr
    
    if se/60.00 >= 1.00:
        mi+= int(se)/60
        se = se%60.00
    
    if mi/60 >= 1:
        ho+= mi/60
        mi = mi%60
        
    if ho >= 24:
        print('Warning: Hours exceed 24 hrs in scenario file')
        
    ho = str(int(ho))
    mi = str(int(mi))
    se = str(round(se,2))
    
    if len(ho)==1:
        ho = '0'+ho
    
    if len(mi)==1:
        mi = '0'+mi
        
    if len(se)<5:
        if se[1] == '.':
            se = '0'+se
            
        if se[2] == '.' and len(se) <5:
            se += '0'
    
    return ho+':'+mi+':'+se
        
class AC:
    def __init__(self,time,acid,actp,lat,lon,hdg,alt,spd):
        #ALl values are obtained at spawn and are not updated
        self.time = time # AC spawn time
        self.acid = acid # AC identity
        self.actp = actp # AC type
        self.loc = np.array([lat,lon]) # AC latitude & longitude
        self.hdg = int(hdg) # AC heading
        self.alt = int(alt) # AC altitude
        self.spd = int(spd) # AC speed 
    
    def add_dest(self,dest):
        self.dest = dest # AC destination
    
    def add_orig(self,orig):
        self.orig = orig # AC origin
        
class Constraint:
    def __init__(self):
        self.dest = None
        self.orig = None
        self.wind = None
        self.hdg0 = None
        self.hdg1 = None
        self.rte  = None

        
def create_proc(scenario):
    #ADD TRAFFIC
    if scenario == 'NE':
        filename = 'trafficNE.scn'
    elif scenario == 'SW':
        filename = 'trafficSW.scn'
    
    f = open(filename,'r')
    text = f.read()
    text = text.split('\n')
    
    ACs = np.array([])
    info = ['','']
    for line in text:
        if len(line) != 0:
            if line[0]!='#':
                if '>CRE' in line:
                    info = line.split(' ')
                    aircraft = AC(info[0][:-4], info[1],info[2],info[3],info[4],info[5],info[6],info[7])
                    ACs = np.append(ACs,aircraft)
                
                if info[1] in line and '>CRE' not in line:
                    if 'DEST' in line:
                        ACs[-1].add_dest(line.split(' ')[-1])
                    elif 'ORIG' in line:
                        ACs[-1].add_orig(line.split(' ')[-1])
                    
    #ADD PROCEDURE CONSTRAINTS
    f = open('proc_conditions.txt')
    text = f.read()
    text = text.split('\n')
    
    Cs = np.array([])
    
    for line in text:
        if len(line) != 0:
            if line[0]!='#':
                created = False
                try:
                    info = line.split(' ')
                    if 'DEST' in info:
                        const = Constraint()
                        created = True
                        const.dest = info[info.index('DEST')+1]
                    elif 'ORIG' in info:
                        const = Constraint()
                        created = True
                        const.orig = info[info.index('ORIG')+1]
                    if 'HDG' in info:
                        if not created:
                            const = Constraint()
                            created = True
                        const.hdg0 = info[info.index('HDG')+1].split('-')[0]
                        const.hdg1 = info[info.index('HDG')+1].split('-')[1]
                        const.hdg0 = int(const.hdg0)
                        const.hdg1 = int(const.hdg1)                
                    if 'WIND' in info:
                        if not created:
                            const = Constraint()
                            created = True
                        const.wind = info[info.index('WIND')+1]
                    if '->' in info:
                        if not created:
                            const = Constraint()
                            created = True
                        const.rte = info[info.index('->')+1]
                        
                except:
                    pass
                if created:
                    Cs = np.append(Cs,const)
            
    #ADD PROCEDURES TO THE AIRCRAFT
    text = ''
    for ac in ACs: #Loop through AC's
        for c in Cs: #Loop through conditions for assigning procedures
            if c.wind == scenario or c.wind == None:
                if c.hdg0 <= ac.hdg < c.hdg1 or c.hdg0 == None or c.hdg1 == None:
                    if c.dest == ac.dest:
                        text += incr_time(ac.time,0.01)+'>'+ac.acid+' call '+c.rte+'\n'
                        text += incr_time(ac.time,0.02)+'>'+ac.acid+' LNAV ON\n'
                            
                    elif c.orig == ac.orig:                    
                        text += incr_time(ac.time,0.01)+'>'+ac.acid+' call '+c.rte+'\n'
                        text += incr_time(ac.time,0.02)+'>'+ac.acid+' LNAV ON\n'
    f = open('proc_init_'+scenario+'.scn','w')
    f.write(text)
    f.close() 

create_proc('NE')
create_proc('SW')