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

#La classe Model rappresenta una modella e contiene tutti i dati e le features estratte
#dai files
class Model(object):
    
    #Nome della cartella fscan
    fscan = 'fscan'
    #Modelli di scarpa
    scarpe = ['Flora', 'Jody', 'Jodyne', 'Marylin', 'Tacco basso']
    #Nome della cartella contente le registrazioni dei sensori
    piedi = ['SX', 'DX']
    #I quattro tipi di file per ogni scarpa
    tipi = ['statica_baricentro.asc', 'camminata_baricentro.asc', 'statica_pressioni.asf', 'camminata_pressioni.asf']
        
    def __init__(self, basepath, nome):
        
        self.tipifunc = [self.baricentro_parser, self.pression_parser]
        # Il nome della modella
        self.nome = nome
        # Un dict che contiene i nomi dei files relativi alle varie scarpe
        self.scarpefiles = {}       
        # Un dizionario che contiene tutti i dati parsati relativo a ogni scarpa/tipo di file 
        self.parsedfiles = {}
                
        self.basepath = basepath
        
        #Se c'e' il file .zip ma non la cartella, l'archivio viene 
        #scompattato in una cartella che ha il nome della modella
        extractdir = basepath + nome        
        if not os.path.isdir(extractdir):
            zipfile.ZipFile(extractdir + ".zip").extractall(extractdir)  
        
        #Viene popolato il dizionario scarpefiles con tutti i path
        #dei file fscan relativi alla modella              
        fscandir = extractdir + '/'
        self.piede = os.listdir(fscandir + os.listdir(fscandir)[0])[0]
        
        for s in Model.scarpe:
            path = fscandir + s + '/' + self.piede
            if os.path.isdir(path):
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
        
        
    # Funzione statica che parsa un file con i frame delle pressioni
    # Restituisce la liste delle matrici delle pressione parsate dal file
#    @staticmethod
    def pression_parser(self, filepath):
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
                row = [g(x) for x in line.split(',')]
                if self.piede == 'DX':
                    row.reverse()
                newframe.append(row)
                counter -= 1
                if counter == 0:
                    reading = False
                    allframes.append(newframe)
                    newframe = []
            if line.startswith('Frame'):
                counter = rows
                reading = True
                    
        f.close()
        return allframes
    
    # Funzione statica che parsa i file dei baricentri.
    # Restituisce una lista di [x, y], uno per ogni frame presente nel file
    def baricentro_parser(self, filepath):
        f = open(filepath)
        rcf = Model.rowcolframes(f) 
        frames = rcf[2]
        cols = rcf[1]
        
        reading = False
        readingCounter = 2
        allinstances = []
        counter = frames
        
        for line in f:
            if reading == True:
                line = line.strip()
                split = line.split(', ')
                newinstance = [float(x) for x in split[2:]]
                if self.piede == 'DX':
                    newinstance[0] = cols - newinstance[1]
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
                
        return allinstances
    
    # Funzione che parsa tutti i file e salva i valori in parsedfiles
    def computeAllFrames(self):
        for scarpa in self.scarpefiles:
            for i, tipo in enumerate(Model.tipi):
                if scarpa not in self.parsedfiles:
                    self.parsedfiles[scarpa] = {}
                self.parsedfiles[scarpa][tipo] = self.tipifunc[i/2](self.scarpefiles[scarpa][tipo])
    
    # Metodo che restituisce i dati relativi alla scarpa e al tipo di file indicato (parsando
    # il file solo nel caso in cui non fosse gia' stato parsato e salvato nel dizionario
    # parsedfiles)
    def getParsed(self, scarpa, tipo):
        if scarpa not in Model.scarpe:
            raise StandardError(str(scarpa) + ' is not a valid shoe model')
        if tipo not in Model.tipi:
            raise StandardError(str(tipo) + ' is not a valid type')
        if scarpa not in self.scarpefiles:
            return []
        
        if scarpa not in self.parsedfiles:
            self.parsedfiles[scarpa] = {}
        
        if tipo not in self.parsedfiles[scarpa]:
            self.parsedfiles[scarpa][tipo] = self.tipifunc[Model.tipi.index(tipo)/2](self.scarpefiles[scarpa][tipo])
                
        return self.parsedfiles[scarpa][tipo]
    
   
    # Metodo che date delle coordinate i, j, e i bound correnti top, bottom, left e right,
    # restituisce i nuovi bounds
    @staticmethod
    def getBounds(i, j, top, bottom, left, right):
        if j < top or top == -1:
            top = j
        if i < left or left == -1:
            left = i
        if j > bottom or bottom == -1:
            bottom = j
        if i > right or right == -1:
            right = i
        return top, bottom, left, right
   
    # Metodo statico che, prendendo in input uno dei frame delle pressioni (matrice)
    # restituisce tutte le features calcolate dalla matrice (quali force, area, bounds, etc.)
    def getFeatures(self, matrix):
        maxtop = -1
        maxbottom = -1
        coordinatetop = 0,0
        coordinatebottom= 0,0
        areatop = 0
        areabottom = 0
        forcetop = 0
        forcebottom = 0
        
        toptop = -1
        topleft = -1
        topright = -1
        topbottom = -1
        
        bottomtop = -1
        bottomleft = -1
        bottomright = -1
        bottombottom = -1
        
        middle = len(matrix)/2
        topcount = 0
        bottomcount = 0
        totalcount = 0
        
        for j in range(0, middle):
            for i in range(0, len(matrix[0])):
                if matrix[j][i] > maxtop:
                    maxtop = matrix[j][i]
                    coordinatetop = i, j
                    topcount = 1
                elif matrix[j][i] == maxtop:
                    topcount += 1
                if matrix[j][i] > 0:
                    areatop += 1
                    forcetop += matrix[j][i]
                    toptop, topbottom, topleft, topright = Model.getBounds(i, j, toptop, topbottom, topleft, topright)
        for j in range(middle, len(matrix)):
            for i in range(0, len(matrix[0])):
                if matrix[j][i] > maxbottom:
                    maxbottom = matrix[j][i]
                    coordinatebottom = i, j
                    bottomcount = 1
                elif matrix[j][i] == maxbottom:
                    bottomcount += 1
                if matrix[j][i] > 0:
                    areabottom += 1
                    forcebottom += matrix[j][i]
                    bottomtop, bottombottom, bottomleft, bottomright = Model.getBounds(i, j, bottomtop, bottombottom, bottomleft, bottomright)
                 
        areatotal = areatop + areabottom   
        forcetotal = forcetop + forcebottom
        maxtotal = max(maxtop, maxbottom)
        coordinatetotal = 0,0

        if maxtop >= maxbottom:
            coordinatetotal = coordinatetop
            if maxtop > maxbottom:
                totalcount = topcount
            else:
                totalcount = topcount + bottomcount
        if maxtop < maxbottom:
            coordinatetotal = coordinatebottom      
            totalcount = bottomcount      
        
        return (maxtop, coordinatetop[0], coordinatetop[1], forcetop, areatop), \
            (maxbottom, coordinatebottom[0], coordinatebottom[1], forcebottom, areabottom), \
            (maxtotal, coordinatetotal[0], coordinatetotal[1], forcetotal, areatotal), \
            (toptop, topbottom, topleft, topright), (bottomtop, bottombottom, bottomleft, bottomright), \
            (topcount, bottomcount, totalcount)
    
    # Funzione che calcola le features su tutti i frames di tutte le scarpe e le salva nella variabile
    # membro `features'
    def computeFeatures(self):
        self.features = {}
        for s in self.scarpefiles:
            self.features[s] = {}
            for tipo in Model.tipi[2:]:
                #print tipo
                self.features[s][tipo] = []
                frames = self.getParsed(s, tipo)
                for frame in frames:
                    self.features[s][tipo].append(self.getFeatures(frame))
                    
    # Funzione che produce il file di testo con la matrice contenente tutte le features calcolate per ogni
    # frame e scarpa    
    def createTable(self):
        base = self.basepath + self.nome + "-output"
#        paths = {}
#        output = {}
     
        #open(self.nome + "-output", 'w+')
        self.computeFeatures()
        columns = ["Nome modella", 'Modello scarpa', 'Piede', 'Modalita\'', 'Frame number', \
                   'Top max', 'Top max X', 'Top max Y', 'Top Force', 'Top Area', \
                   'Bottom max', 'Bottom max X', 'Bottom max Y', 'Bottom Force', 'Bottom Area', \
                   'All max', 'All max X', 'All max Y', 'All Force', 'All Area', \
                   'Baricentro X', 'Baricentro Y', \
                   'Top top', 'Top bottom', 'Top left', 'Top right', \
                   'Bottom top', 'Bottom bottom', 'Bottom left', 'Bottom right', \
                   'Top Count', 'Bottom Count', 'Total Count']
        
        #formato = "{}\t" * len(columns)
        #print formato
        #print str(len(columns)) + " " + str(len(map(len, columns)))
        
        def myLen(s):
            return len(s) + 2
        row_format = "{}\t" * (len(columns)-1) + "{}"#formato.format(*map(myLen,columns))
        
        #row_format ="{:>15}" * len(columns)
        #print row_format.format(*columns)
        '''for s in Model.scarpe:
            for t in Model.tipi[2:]:
                if s not in paths:
                    paths[s] = {}
                    output[s] = {}
                paths[s][t] = base + "-" + s + "-" + t[:-4] + ".txt"
                output[s][t] = open(paths[s][t], 'w+')
                output[s][t].write(row_format.format(*columns) + '\n')'''
        
        out = open(base + ".txt", 'w+')        
        out.write(row_format.format(*columns) + '\n')
        
        print 'Creating table for ' + self.nome
        
        for s in self.scarpefiles:
            for i in range(0,2):
                #quando i e' 0, prendo baricentro e pressioni statiche, quando e' 1
                #prendo baricentro e pressioni camminate
                baricentri = self.getParsed(s, Model.tipi[i])
                features = self.features[s][Model.tipi[i+2]]
                mode = 'statico' if i == 0 else 'camminata'
                for j in range(0, len(baricentri)):
                    top, bottom, total, boundstop, boundsbottom, counts = features[j]
                    arglist = [self.nome, s, self.piede, mode, str(j+1), \
                               top[0], top[1], top[2], top[3], top[4],\
                               bottom[0], bottom[1], bottom[2], bottom[3], bottom[4],\
                               total[0], total[1], total[2], total[3], total[4],\
                               baricentri[j][0], baricentri[j][1], \
                               boundstop[0], boundstop[1], boundstop[2], boundstop[3], \
                               boundsbottom[0], boundsbottom[1], boundsbottom[2], boundsbottom[3], \
                               counts[0], counts[1], counts[2]]
                    #print row_format.format(*map(str,arglist))
                    #output[s][Model.tipi[i+2]].write(row_format.format(*map(str,arglist)) + '\n')
                    out.write(row_format.format(*map(str,arglist)) + '\n')
        self.parsedfiles = {}
        self.features = {}
                
                    
#---------------------------------------------------------------------------------------------#
#maxtop 3 coordinatetop 1,1 areatop 6 forcetop 12 maxbottom 7 coordbottom 3,2 areabottom 3 forcebottom 11
#maxtotal 7 coordtotal 3,2 areatotal 9 forcetotal 23
#toptop 0 topleft 0 topright 3 topbottom 1, bottomtop 2, bottomleft 1, bottomright  2, bottombottom 3
# testmatrix1 = [[0,2,2,0], \
#                [1,3,3,1], \
#                [0,2,2,0], \
#                [0,0,7,0], ]
# 
# result = Model.getFeatures(testmatrix1)
# #top
# assert result[0] == (3, 1, 1, 12, 6), 'Top is wrong: ' + str(result[0])
# #bottom
# assert result[1] == (7, 3, 2, 11, 3), 'Bottom is wrong' + str(result[1])
# #total
# assert result[2] == (7, 3, 2, 23, 9), 'Total is wrong' + str(result[2])
# #top bounds
# assert result[3] == (0, 1, 0, 3), 'Top Bounds are wrong' + str(result[3])
# #bottom bounds
# assert result[4] == (2, 3, 1, 2), 'Bottom Bounds are wrong' + str(result[3])

#sys.exit("Success")

d = '/home/michele/Kode/Modelle/'
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

for modella in allmodels:
    modella.createTable()


#feats = modella.getFeatures('Flora', 1, 0)
'''feats = modella.features['Flora'][Model.tipi[3]]
frames = modella.parsedfiles['Flora'][Model.tipi[3]]

for n, frame in enumerate(frames):
    topbox = feats[n][3]
    bottombox = feats[n][4]
    for i in range(int(topbox[0]), int(topbox[1]) + 1):
        for j in range(int(topbox[2]), int(topbox[3]) + 1):
            if i == topbox[0] or i == topbox[1] or j == topbox[2] or j == topbox[3]:
                frame[i][j] = nan
    for i in range(int(bottombox[0]), int(bottombox[1]) + 1):
        for j in range(int(bottombox[2]), int(bottombox[3]) + 1):
            if i == bottombox[0] or i == bottombox[1] or j == bottombox[2] or j == bottombox[3]:
                frame[i][j] = nan'''

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
    combined.append(combframe)'''
    
#update.frame = 0
'''fig, ax = subplots()
mat = ax.matshow(frames[0], cmap = cm.Spectral_r, vmin = 0, vmax = 500) 
colorbar(mat)
ani = animation.FuncAnimation(fig, update, frames, interval=10, save_count=50, repeat=True)
#mywriter = animation.FFMpegWriter()
pp.show()

#ani.save('animation.mp4', writer=mywriter)
print 'Done'''
    

    
    
    
    
    
    
    
    
    
    
    
    

