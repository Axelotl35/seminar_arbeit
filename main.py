# Import aller wichtigen Bibliotheken
from random import random as rnd
import cairo
import math
import numpy as np
from PIL import Image
from struct import pack

# Bild wird als Numpy-Array geladen
file = "monalisa.png"
image = Image.open(file)
image = image.convert('RGB')
data = np.asarray(image).astype("float")

# Funktion um eine Variable zwischen einem Minimum und Maximum zu beschränken
def constr(n,minim,maxim):
    return max(minim,min(n,maxim))

# Klasse Ellipse, die alle Parameter einer Ellipse beinhaltet
class Ellipse():
    def __init__(self,screen):
        self.color = [0,0,0,0]
        self.x = 0
        self.y = 0
        self.r1 = 0
        self.r2 = 0
        self.screen = screen
    
    # Mutationsfunktion, die alle Werte zufällig ändert
    def mutate(self,rate):
        # damit die Ellipsen im Bildschirm bleiben und die RGB-Werte
        # zwischen 0 und 1 liegen, wird die constr-Funktion benutzt
        # Anmerkung: pycairo liest die RGB-Werte zwischen 0 und 1 ein,
        # es gibt aber immernoch nur 256 mögliche Werte für R,G und B
        
        # r,g,b
        self.color[0]=constr(self.color[0]+rate*0.15*(rnd()-0.5),0,1)
        self.color[1]=constr(self.color[1]+rate*0.15*(rnd()-0.5),0,1)
        self.color[2]=constr(self.color[2]+rate*0.15*(rnd()-0.5),0,1)
        # x,y
        self.x=constr(self.x+(rnd()-0.5)*rate*self.screen[0]/20,1,self.screen[0])
        self.y=constr(self.y+(rnd()-0.5)*rate*self.screen[1]/20,1,self.screen[1])
        # r1,r2
        self.r1=constr(self.r1+(rnd()-0.5)*rate*self.screen[0]/20,1,self.screen[0])
        self.r2=constr(self.r2+(rnd()-0.5)*rate*self.screen[1]/20,1,self.screen[1])
    
    # Generation einer zufälligen Ellipse
    def random(self):
        self.color = [rnd(),rnd(),rnd(),0.2]
        self.x,self.y = rnd()*self.screen[0],rnd()*self.screen[1]
        self.r1,self.r2 = rnd()*self.screen[0]/3,rnd()*self.screen[1]/3

# Klasse Picture in der sich eine bestimmte Anzahl von Ellipsen befindet
class Picture():
    def __init__(self,screen_size,ellipses):
        self.screen_size = screen_size
        self.fitness = 0
        self.ellipses = ellipses
    
    # randomisiert alle Ellipsen des Bildes
    def random(self):
        for ellipse in self.ellipses:
            ellipse.random()
    
    # mutiert alle Ellipsen des Bildes
    def mutate(self,rate):
        for ellipse in self.ellipses:
            ellipse.mutate(rate)
    
    # Fitness-Funktion
    def fitness_func(self):
        # erstellt den pycairo-Canvas
        width,height = self.screen_size
        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(ims)

        # zeichnet alle Ellipsen auf den Canvas
        for ellipse in self.ellipses:
            cr.save()
            r,g,b = ellipse.color[0],ellipse.color[1],ellipse.color[2]
            a = ellipse.color[3]
            cr.set_source_rgba(r, g, b, a)
            x,y,r1,r2 = ellipse.x,ellipse.y,ellipse.r1,ellipse.r2
            cr.translate(x,y)
            cr.scale(r1,r2)
            cr.arc(0, 0, 1, 0, 2*math.pi)
            cr.fill()
            cr.restore()

        # berechnet die Fitness des Bildes mithilfe des MSE
        buf = ims.get_data()
        nparr = np.ndarray(
                shape=(self.screen_size[0],self.screen_size[1],4),
                dtype=np.uint8,buffer=buf)[:,:,:3]
        err = np.sum((nparr.astype("float") - data) ** 2)
        err /= float(nparr.shape[0] * nparr.shape[1])
        self.fitness = err
    
    # speichert das derzeitige Bild
    def output(self,gen_num):
        width,height = self.screen_size
        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(ims)

        for ellipse in self.ellipses:
            cr.save()
            r,g,b = ellipse.color[0],ellipse.color[1],ellipse.color[2]
            a = ellipse.color[3]
            cr.set_source_rgba(r, g, b, a)
            x,y,r1,r2 = ellipse.x,ellipse.y,ellipse.r1,ellipse.r2
            cr.translate(x,y)
            cr.scale(r1,r2)
            cr.arc(0, 0, 1, 0, 2*math.pi)
            cr.fill()
            cr.restore()

        buf = ims.get_data()
        nparr = np.ndarray(
            shape=(self.screen_size[0],self.screen_size[1],4),
            dtype=np.uint8, buffer=buf)[:,:,:3]
        Image.fromarray(nparr).save("output"+str(gen_num)+".jpg")

# Klasse für die Population
class Population():
    def __init__(self,pictures):
        self.pictures = pictures
        self.screen_size = self.pictures[0].screen_size[:]
        self.best = None
        for picture in pictures:
            picture.random()
    
    # Simulierung der Generationen
    def run(self,n):
        for gen in range(n):
            self.generation(gen)
            self.best.output(gen)

    # Selektion, Rekombination, Mutation und Erstellung einer
    # neuen Population während einer Generation
    def generation(self,gen):
        gene_pool = []
        #Selektion
        self.best = [0,None]

        for id,picture in enumerate(self.pictures):
            picture.fitness_func()
            # Speicherung des Besten aus der Population
            if picture.fitness>self.best[0]:
                self.best = [picture.fitness,picture]
            gene_pool.append((id, picture.fitness))
        
        gene_pool = sorted(gene_pool, key=lambda x: x[1])
        self.best = self.best[1]
        new_pictures = []
        
        # Rekombination
        for _ in range(len(self.pictures)-1+1):
            new_picture = Picture(self.screen_size[:],[])
            # Top 20% der Population weren für die Eltern selektiert
            P1,P2=(self.pictures[gene_pool[int(rnd()*len(gene_pool)*0.2)][0]],
                   self.pictures[gene_pool[int(rnd()*len(gene_pool)*0.2)][0]])
            for id in range(len(P1.ellipses)):
                new_ellipse = Ellipse(self.screen_size[:])
                # jede Ellipse wird zufällig von einem der Elternpaare gewählt
                p1 = rnd()>0.5 
                if p1: new_ellipse.x = P1.ellipses[id].x
                else:  new_ellipse.x = P2.ellipses[id].x
                
                if p1: new_ellipse.y = P1.ellipses[id].y
                else:  new_ellipse.y = P2.ellipses[id].y
                
                if p1: new_ellipse.r1 = P1.ellipses[id].r1
                else:  new_ellipse.r1 = P2.ellipses[id].r1
                
                if p1: new_ellipse.r2 = P1.ellipses[id].r2
                else:  new_ellipse.r2 = P2.ellipses[id].r2
                
                if p1: new_ellipse.color[0] = P1.ellipses[id].color[0]
                else:  new_ellipse.color[0] = P2.ellipses[id].color[0]
                
                if p1: new_ellipse.color[1] = P1.ellipses[id].color[1]
                else:  new_ellipse.color[1] = P2.ellipses[id].color[1]
                
                if p1: new_ellipse.color[2] = P1.ellipses[id].color[2]
                else:  new_ellipse.color[2] = P2.ellipses[id].color[2]
                
                if p1: new_ellipse.color[3] = P1.ellipses[id].color[3]
                else:  new_ellipse.color[3] = P2.ellipses[id].color[3]
                new_picture.ellipses.append(new_ellipse)
            # Mutation
            new_picture.mutate(0.995**gen)
            new_pictures.append(new_picture)
        self.pictures = new_pictures[:]

# -------------------------------------------------------

# Ausführung der Generation mit 100 Individuen, 90 Ellipsen
# und 600 Generationen
p,n,g = 100,90,600
p = Population([Picture(image.size[:],[Ellipse(image.size[:])
for _ in range(n)])for _ in range(p)])
p.run(g)

# Auswahl des Besten Individuums
result = p.best

# Erstellung der Binärdatei (.eai = evolutionärer Kompressionsalgorithmus)
output = open("output.eka","wb")
binary1,binary2 = bytearray(),bytearray()
output.write(bytearray("IMAGE",encoding="ascii"))
output.write(pack("HH",result.ellipses[0].screen[0],result.ellipses[0].screen[1]))

# Speicherung der Ellipsen in Binärform
for ellipse in result.ellipses:
    # Speicherung der Koordinaten und Radien in Shorts
    binary1+=pack("HHHH",
        int(ellipse.x/ellipse.screen[0]*65535),
        int(ellipse.y/ellipse.screen[1]*65535),
        int(ellipse.r1/ellipse.screen[0]*65535),
        int(ellipse.r2/ellipse.screen[1]*65535)
    )
    # Speicherung der RGB-Werte in Bytes
    binary2+=pack("BBB",
        int(ellipse.color[0]*255),
        int(ellipse.color[1]*255),
        int(ellipse.color[2]*255)
    )

# Ausgabe der komprimierten Binär-Datei
output.write(binary1+binary2)