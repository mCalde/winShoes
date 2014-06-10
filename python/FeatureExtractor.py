'''
Created on Jun 6, 2014

@author: root
'''

import sys
import os
import zipfile
from __builtin__ import int
import matplotlib.pyplot as pp
from matplotlib.pylab import *
import matplotlib.animation as animation

rows_tag = 'ROWS'
cols_tag = 'COLS'
frames_tag = 'END_FRAME'     

#La classe Model mi rappresenta una modella, con i suoi 4 files per scarpa 
#e i vari metodi
class Model(object):
    
    fscan = 'fscan'
    scarpe = ['Flora', 'Jody', 'Jodyne', 'Marylin', 'Tacco basso']
    piede = 'SX'
    tipi = ['statica_baricentro.asc', 'camminata_baricentro.asc', 'statica_pressioni.asf', 'camminata_pressioni.asf']
    tipifunc = [Model.baricentro_parser, Model.pression_parser]
    
    def __init__(self, basepath, nome):
        # Il nome della modella, probabilmente inutile
        self.nome = nome
        # Un dict che contiene tutti i files relativi alle varie scarpe
        self.scarpefiles = {}
        
        #Se c'e' il file .zip ma non la cartella, l'archivio viene 
        #scompattato in una cartella che ha il nome della modella
        extractdir = basepath + nome        
        if not os.path.isdir(extractdir):
            zipfile.ZipFile(d+f).extractall(d)  
        
        #Viene popolato il dizionario scarpefiles con tutti i path
        #dei file fscan relativi alla modella              
        fscandir = extractdir+'/'+fscan
        for s in scarpe:
            path = fscandir + '/' + s + '/' + piede
            for f in os.listdir(path):
                for i in range(0, len(tipi)):
                    if f.endswith(tipi[i]):
                        all_files[i].append(path + '/' + f)
                        if s not in self.scarpefiles:
                            self.scarpefiles[s] = {}
                        self.scarpefiles[s][tipi[i]] = path + '/' + f
                        break
        
    @staticmethod            
    def rowcolframes(f):       
        rows = 0
        cols = 0
        frames = 0
        for line in f:
            split = line.split()
            if len(split) == 2:
                if split[0] == rows_tag:
                    rows = int(split[1])
                elif split[0] == cols_tag:
                    cols = int(split[1])
                elif split[0] == frames_tag:
                    frames = int(split[1])
                    break    
        f.seek(0)
        return rows, cols, frames
        
        
    @staticmethod
    def pression_parser(filepath):
        print filepath
        f = open(filepath)
        rcf = rowcolframes(f)
        rows = rcf[0]
        
        reading = False
        newframe = []
        allframes = []
        counter = 0
        
        g = lambda x: float('nan') if x == 'B' else float(x)
        
        for line in f:
            if reading == True:
                line = line.strip()
                newframe.append([g(x) for x in line.split(',')])
                counter -= 1
                if counter == 0:
                    reading = False
                    allframes.append(newframe)
                    newframe = []
            if line.startswith('Frame'):
                counter = rows
                reading = True
                #print 'Reading frame ' + line.split()[1]
                    
        print allframes[-1]   
        f.close()
        return allframes
    
    @staticmethod
    def baricentro_parser(filepath):
        f = open(filepath)
        rcf = rowcolframes(f) 
        frames = rcf[2]
        
        reading = False
        readingCounter = 2
        allinstances = []
        counter = frames
        
        for line in f:
            if reading == True:
                line = line.strip()
                split = line.split(', ')
                newinstance = [float(x) for x in split[1:]]
                allinstances.append(newinstance)
                counter -= 1
                if counter == 0:
                    break
            if readingCounter == 1:
                readingCounter = 0
                reading = True
                continue
            if line.startswith('ASCII_DATA'):
                readingCounter = 1
                continue
                
        print allinstances[-1:]
        return allinstances
    
    def pressionFramesForScarpa(self, scarpa, static):
        filepath = ''
        if scarpa not in Model.scarpe:
            raise StandardError(str(scarpa) + ' is not a valid shoe model')
        if static:
            filepath = self.scarpefiles[scarpa][tipi[1]]
        else:
            filepath = self.scarpefiles[scarpa][tipi[3]]
        return Model.pression_parser(filepath)
    
    def computeAllFrames(self):
        for scarpa in Model.scarpe:
            
        
        
                    
#---------------------------------------------------------------------------------------------#

def rowcolframes(f):       
    rows = 0
    cols = 0
    frames = 0
    for line in f:
        split = line.split()
        if len(split) == 2:
            if split[0] == rows_tag:
                rows = int(split[1])
            elif split[0] == cols_tag:
                cols = int(split[1])
            elif split[0] == frames_tag:
                frames = int(split[1])
                break    
    f.seek(0)
    return rows, cols, frames
    
    
def pression_parser(filepath):
    print filepath
    f = open(filepath)
    rows,cols,frames = rowcolframes(f)
    
    reading = False
    newframe = []
    allframes = []
    counter = 0
    
    g = lambda x: float('nan') if x == 'B' else float(x)
    
    for line in f:
        if reading == True:
            line = line.strip()
            newframe.append([g(x) for x in line.split(',')])
            counter -= 1
            if counter == 0:
                reading = False
                allframes.append(newframe)
                newframe = []
        if line.startswith('Frame'):
            counter = rows
            reading = True
            #print 'Reading frame ' + line.split()[1]
                
    print allframes[-1]   
    f.close()
    return allframes

def baricentro_parser(filepath):
    f = open(filepath)
    rows,cols,frames = rowcolframes(f) 
    
    reading = False
    readingCounter = 2
    allinstances = []
    counter = frames
    
    for line in f:
        if reading == True:
            line = line.strip()
            split = line.split(', ')
            newinstance = [float(x) for x in split[1:]]
            allinstances.append(newinstance)
            counter -= 1
            if counter == 0:
                break
        if readingCounter == 1:
            readingCounter = 0
            reading = True
        if line.startswith('ASCII_DATA'):
            readingCounter = 1
            
    print allinstances[-1:]
    return allinstances


def extract_static_pression(filepath):
    print 'static pression on ' + filepath
    
def extract_camminata_pression(filepath):
    print 'camminata pression on ' + filepath
    
def extract_static_bari(filepath):
    print 'static bari on ' + filepath
    
def extract_camminata_bari(filepath):
    print 'camminata bari on ' + filepath

d = '/home/michele/Kode/'
fscan = 'fscan'
scarpe = ['Flora', 'Jody', 'Jodyne', 'Marylin', 'Tacco basso']
piede = 'SX'
tipi = ['statica_baricentro.asc', 'statica_pressioni.asf', 'camminata_baricentro.asc', 'camminata_pressioni.asf']
models = []
files_static_baricentro = []
files_static_pression = []
files_camminata_pression = []
files_camminata_baricentro = []
all_files = [files_static_baricentro, files_static_pression, files_camminata_baricentro, files_camminata_pression]
extractors = [extract_static_bari, extract_static_pression, extract_camminata_pression, extract_camminata_bari]


# scarpefiles e' un dizionario che per ogni tipo di scarpa contiene i 4 files pressione, baricentro per
# statica e dinamica. Per ogni modella verra' creato un dizionario di tipo scarpefiles
scarpefiles = {scarpe[0]:{}, scarpe[1]:{}, scarpe[2]:{}, scarpe[3]:{}}

allmodels = []
    
if len(sys.argv) > 2:
    sys.exit("Usage: [dirpath]")
    
if len(sys.argv) == 2:
    d = sys.argv[1]
    if not os.path.isdir(d):
        sys.exit("%s is not a valid directory", d)
        

for f in os.listdir(d):
    if f.endswith('.zip'):
#        print dir + file
        idx = f.find('.zip')
        nome = f[:idx]
        allmodels.append(Model(d, nome))
        extractdir = d + f[:idx]
        
        if not os.path.isdir(extractdir):
            #shutil.rmtree(extractdir)        
            zipfile.ZipFile(d+f).extractall(d)
            
        models.append(f[:idx])
            
#print os.listdir(dir)
#print models        

for m in models:
    for s in scarpe:
        path = d+m+'/'+fscan+'/'+s+'/'+piede
#        print path
#        print os.listdir(path)
        for f in os.listdir(path):
            for i in range(0, len(tipi)):
                if f.endswith(tipi[i]):
                    all_files[i].append(path + '/' + f)
                    break

# for i in range(0, len(tipi)): 
#     for l in all_files[i]:
#         extractors[i](l)

#matrici = pression_parser(all_files[2][0])
#baricentro = baricentro_parser(all_files[3][0])

#for i in range(0, len(baricentro) - 1):
#    time, row, col = baricentro[i]
    
#    matrici[i][int(row)][int(col)] = nan    
    

def update(data):
#    print(update.frame)
#    update.frame += 1
    mat.set_data(data)
    return mat 

#    scarpe = ['Flora', 'Jody', 'Jodyne', 'Marylin', 'Tacco basso']
flora = allmodels[0].pressionFramesForScarpa(scarpe[0], False)
jody = allmodels[0].pressionFramesForScarpa(scarpe[1], False)
jodyne = allmodels[0].pressionFramesForScarpa(scarpe[2], False)
marylin = allmodels[0].pressionFramesForScarpa(scarpe[3], False)
taccobasso = allmodels[0].pressionFramesForScarpa(scarpe[4], False)

combined = []

for i in range(0, len(flora)):
    combframe = []
    for n in range(0, len(flora[0])):
        combline = flora[i][n] + jody[i][n] + jodyne[i][n] + marylin[i][n] + taccobasso[i][n]
        combframe.append(combline)
    combined.append(combframe)
    
#update.frame = 0
fig, ax = subplots()
mat = ax.matshow(combined[0], cmap = cm.Spectral_r, vmin = 0, vmax = 500) 
colorbar(mat)
ani = animation.FuncAnimation(fig, update, combined, interval=10, save_count=50, repeat=False)
#mywriter = animation.FFMpegWriter()
pp.show()

#ani.save('animation.mp4', writer=mywriter)
print 'Done'


