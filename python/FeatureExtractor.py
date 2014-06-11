'''
Created on Jun 6, 2014

@author: root
'''

import sys
import os
import zipfile
import time
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
    
    def __init__(self, basepath, nome):
        # Il nome della modella, probabilmente inutile
        self.nome = nome
        # Un dict che contiene tutti i files relativi alle varie scarpe
        self.scarpefiles = {}        
        Model.tipifunc = [Model.baricentro_parser, Model.pression_parser]
        self.parsedfiles = {}
        
        #Se c'e' il file .zip ma non la cartella, l'archivio viene 
        #scompattato in una cartella che ha il nome della modella
        extractdir = basepath + nome        
        if not os.path.isdir(extractdir):
            zipfile.ZipFile(d+f).extractall(d)  
        
        #Viene popolato il dizionario scarpefiles con tutti i path
        #dei file fscan relativi alla modella              
        fscandir = extractdir+'/'+Model.fscan
        for s in Model.scarpe:
            path = fscandir + '/' + s + '/' + Model.piede
            for f in os.listdir(path):
                for i in range(0, len(Model.tipi)):
                    if f.endswith(Model.tipi[i]):
                        if s not in self.scarpefiles:
                            self.scarpefiles[s] = {}
                        self.scarpefiles[s][Model.tipi[i]] = path + '/' + f
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
        rcf = Model.rowcolframes(f)
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
        rcf = Model.rowcolframes(f) 
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
            filepath = self.scarpefiles[scarpa][Model.tipi[1]]
        else:
            filepath = self.scarpefiles[scarpa][Model.tipi[3]]
        return Model.pression_parser(filepath)
    
    tipifunc = []
    
    def computeAllFrames(self):
        for scarpa in Model.scarpe:
            for i, tipo in enumerate(Model.tipi):
                if scarpa not in self.parsedfiles:
                    self.parsedfiles[scarpa] = {}
                self.parsedfiles[scarpa][tipo] = Model.tipifunc[i/2](self.scarpefiles[scarpa][tipo])
                
    def getFeatures(self, scarpa, pression, static):
        tipo = -1
        if not pression and static:
            tipo = 0
        elif not pression and not static:
            tipo = 1
        elif pression and static:
            tipo = 2
        else:
            tipo = 3
        if scarpa not in Model.scarpe:
            raise StandardError(str(scarpa) + ' is not a valid shoe model')
        if scarpa not in self.parsedfiles:
            self.parsedfiles[scarpa] = {}
        
        if Model.tipi[tipo] not in self.parsedfiles[scarpa]:
            self.parsedfiles[scarpa][Model.tipi[tipo]] = Model.tipifunc[tipo/2](self.scarpefiles[scarpa][Model.tipi[tipo]])
                
        return self.parsedfiles[scarpa][Model.tipi[tipo]]
    
    def getSTFeatures(self, scarpa, tipo):
        if scarpa not in Model.scarpe:
            raise StandardError(str(scarpa) + ' is not a valid shoe model')
        if tipo not in Model.tipi:
            raise StandardError(str(tipo) + ' is not a valid type')
        if scarpa not in self.parsedfiles:
            self.parsedfiles[scarpa] = {}
        
        if tipo not in self.parsedfiles[scarpa]:
            self.parsedfiles[scarpa][tipo] = Model.tipifunc[Model.tipi.index(tipo)/2](self.scarpefiles[scarpa][tipo])
                
        return self.parsedfiles[scarpa][tipo]
    
   
    @staticmethod
    def getAreaAndMax(matrix):
        maxtop = 0
        maxbottom = 0
        coordinatetop = 0,0
        coordinatebottom= 0,0
        areatop = 0
        areabottom = 0
        forcetop = 0
        forcebottom = 0
        
        middle = len(matrix)/2
        
        for j in range(0, middle):
            for i in range(0, len(matrix[0])):
                if matrix[j][i] > maxtop:
                    maxtop = matrix[j][i]
                    coordinatetop = j,i
                if matrix[j][i] > 0:
                    areatop += 1
                    forcetop += matrix[j][i]
        for j in range(middle, len(matrix)):
            for i in range(0, len(matrix[0])):
                if matrix[j][i] > maxbottom:
                    maxbottom = matrix[j][i]
                    coordinatebottom = j, i
                if matrix[j][i] > 0:
                    areabottom += 1
                    forcebottom += matrix[j][i]
                 
        areatotal = areatop + areabottom   
        forcetotal = forcetop + forcebottom
        maxtotal = max(maxtop, maxbottom)
        coordinatetotal = 0,0

        if maxtop >= maxbottom:
            coordinatetotal = coordinatetop
        if maxtop < maxbottom:
            coordinatetotal = coordinatebottom            
        
        return (maxtop, coordinatetop[0], coordinatetop[1], forcetop, areatop), \
            (maxbottom, coordinatebottom[0], coordinatebottom[1], forcebottom, areabottom), \
            (maxtotal, coordinatetotal[0], coordinatetotal[1], forcetotal, areatotal)
    
    def computeFeatures(self):
        self.features = {}
        for s in Model.scarpe:
            self.features[s] = {}
            for tipo in Model.tipi[2:]:
                print tipo
                self.features[s][tipo] = []
                frames = self.getSTFeatures(s, tipo)
                for frame in frames:
                    self.features[s][tipo].append(Model.getAreaAndMax(frame))
                    
        
    def createTable(self):
        self.computeFeatures()
        columns = ["Nome modella", 'Modello scarpa', 'Modalita\'', \
                   'Top max', 'Top max X', 'Top max Y', 'Top area', 'Top force', \
                   'Bottom max', 'Bottom max X', 'Bottom max Y', 'Bottom area', 'Bottom force', \
                   'All max', 'All max X', 'All max Y', 'All area', 'All force', \
                   'Baricentro X', 'Baricentro Y']
        
        formato = "{{:>{}}}" * len(columns)
        #print formato
        #print str(len(columns)) + " " + str(len(map(len, columns)))
        
        def myLen(s):
            return len(s) + 4
        row_format = formato.format(*map(myLen,columns))
        
        #row_format ="{:>15}" * len(columns)
        print row_format.format(*columns)
        for s in Model.scarpe:
            for i in range(0,1):
                #quando i e' 0, prendo baricentro e pressioni statiche, quando e' 1
                #prendo baricentro e pressioni camminate
                baricentri = self.getSTFeatures(s, Model.tipi[i])
                features = self.features[s][Model.tipi[i+2]]
                mode = 'statico' if i == 0 else 'camminata'
                for j in range(0, len(baricentri)):
                    top, bottom, total = features[j]
                    arglist = [self.nome, s, mode, \
                               top[0], top[1], top[2], top[3], top[4],\
                               bottom[0], bottom[1], bottom[2], bottom[3], bottom[4],\
                               total[0], total[1], total[2], total[3], total[4],\
                               baricentri[j][0], baricentri[j][1]]
                    print 'ciaociao'
                    print row_format.format(*map(str,arglist))
                
                    
#---------------------------------------------------------------------------------------------#
#maxtop 3 coordinatetop 1,1 areatop 6 forcetop 12 maxbottom 7 coordbottom 3,2 areabottom 3 forcebottom 11
#maxtotal 7 coordtotal 3,2 areatotal 9 forcetotal 23
testmatrix1 = [[0,2,2,0], \
               [1,3,3,1], \
               [0,2,2,0], \
               [0,0,7,0], ]

result = Model.getAreaAndMax(testmatrix1)
#top
assert result[0] == (3, 1, 1, 12, 6), 'Top is wrong: ' + str(result[0])
#bottom
assert result[1] == (7, 3, 2, 11, 3), 'Bottom is wrong' + str(result[1])
#total
assert result[2] == (7, 3, 2, 23, 9), 'Total is wrong' + str(result[2])

a,b,c = Model.getAreaAndMax(testmatrix1)

d = '/home/michele/Kode/'
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
    

def update(data):
#    print(update.frame)
#    update.frame += 1
    mat.set_data(data)
    return mat 

modella = allmodels[0]

modella.createTable()

'''start = time.clock()
modella.computeAllFrames()
modella.computeFeatures()
end= time.clock() - start

print 'Elapsed time: ' + str(end)'''

"""for scarpa in Model.scarpe:
    print scarpa + ' true true'
    print modella.getFeatures(scarpa, True, True)[-1]
    print scarpa + ' true false'
    print modella.getFeatures(scarpa, True, False)[-1]
    print scarpa + ' false true'
    print modella.getFeatures(scarpa, False, True)[-1]
    print scarpa + ' false false'
    print modella.getFeatures(scarpa, False, False)[-1]"""

#    scarpe = ['Flora', 'Jody', 'Jodyne', 'Marylin', 'Tacco basso']
'''flora = allmodels[0].pressionFramesForScarpa(Model.scarpe[0], False)
jody = allmodels[0].pressionFramesForScarpa(Model.scarpe[1], False)
jodyne = allmodels[0].pressionFramesForScarpa(Model.scarpe[2], False)
marylin = allmodels[0].pressionFramesForScarpa(Model.scarpe[3], False)
taccobasso = allmodels[0].pressionFramesForScarpa(Model.scarpe[4], False)

combined = []

print str(len(flora[0])) + ',' + str(len(flora[0])/2)

for i in range(0, len(flora)):
    combframe = []
    for n in range(0, len(flora[0])/2):
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
print 'Done'''


