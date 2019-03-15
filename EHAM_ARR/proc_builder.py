# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 01:15:31 2019

@author: koen
"""
#from openpyxl import load_workbook
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
        self.loc = np.array([float(lat),float(lon)]) # AC latitude & longitude
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
    #SHOW SCENARIO
    print('\n--------\nSCENARIO: \n'+scenario)
    #ADD TRAFFIC
    if scenario == 'NE':
        filename = 'trafficNE.scn'
        excels = ['trafficNE-stack-arrivals', 'trafficNE-stack-departures']
    elif scenario == 'SW':
        filename = 'trafficSW.scn'
        excels = ['trafficSW-stack-arrivals', 'trafficSW-stack-departures']
    
    f = open(filename,'r')
    text = f.read()
    text = text.split('\n')
    
    global ACs
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
#                        print(line.split(' '))
                        if len(line.split(' ')) - line.split(' ').index('ORIG') > 2:
                            coord = [float(line.split(' ')[-2]),float(line.split(' ')[-1])]
#                            print(coord)
                            if (coord[0]-52.311593)**2+(coord[1]-4.666788)**2 < 1**2:
                                ACs[-1].add_orig('EHAM')                                
                            else:
                                ACs[-1].add_orig('NONE')
#                            print(ACs[-1]).orig
                        else: 
                            ACs[-1].add_orig(line.split(' ')[-1])
    schiphol = [52.3105386,4.7682744]
    
    for ac in ACs:
        print(ac.acid)
        ac.dir = 180./np.pi*(np.pi+np.arctan2(schiphol[1]-ac.loc[1],schiphol[0]-ac.loc[0]))
        print(ac.dir)
                        
    #GET DIRECTION FOR ACs
#    for name in excels:
#        workbook = load_workbook(name+'.xlsx', read_only=True)
#        sheet = workbook[name]
#        info =  np.array([[i.value for i in j] for j in sheet['A2':'H250']])
#        
#        for ac in ACs:
#            for row in info:
#                if ac.acid == row[4]:
#                    ac.dir = row[1]
  
    #ADD PROCEDURE CONSTRAINTS
    print('\n----------\nConditions:')
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
                    #SHOW CONDITIONS
                    print(line)
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
                    if 'DIR' in info:
#                        print('try')
                        if not created:
                            const = Constraint()
                            created = True
                        const.dir0 = info[info.index('DIR')+1].split('-')[0]
                        const.dir1 = info[info.index('DIR')+1].split('-')[1]
                        const.dir0 = int(const.dir0)
                        const.dir1 = int(const.dir1)   
#                        print(const.dir0,const.dir1)
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
    print(len(ACs))
    for ac in ACs: #Loop through AC's
        try:
            for c in Cs: #Loop through conditions for assigning procedures
                if c.wind == scenario or c.wind == None:
                    
                        if c.dir0 <= ac.dir < c.dir1 or c.dir0 == None or c.dir1 == None:
                            if c.dest == ac.dest:
                                text += incr_time(ac.time,0.01)+'>'+ac.acid+' call '+c.rte+'\n'
                                if c.rte[0] == 'A':
                                    text += incr_time(ac.time,0.01)+'>'+ac.acid+' DEST '+c.rte[:-3]+'0\n'
                                    text += incr_time(ac.time,0.02)+'>'+ac.acid+' VNAV ON\n'
                                text += '\n'
                            
                            elif c.orig == ac.orig:
                                text += incr_time(ac.time,0.01)+'>'+ac.acid+' call '+c.rte+'\n'
                                text += incr_time(ac.time,0.02)+'>'+ac.acid+' LNAV OFF\n'
                                text += '\n'
                            
        except:
            print('Warning: Failed to assign '+ac.acid+' from '+ac.orig+' to '+ac.dest)
        
    f = open('proc_init_'+scenario+'.scn','w')
    f.write(text)
    f.close() 

#create_proc('NE')
create_proc('SW')


