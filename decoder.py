# Import aller wichtigen Bibliotheken
from struct import unpack
import numpy as np
import math
from PIL import Image
import cairo

def decode(file):  
    # Einlesen der Binärdatei
    binary = file.read()
    # Überprüfen, ob die ersten 5 Bytes stimmen
    if binary[:5].decode(encoding="ascii")!="IMAGE":
        print("Es wurde ein falsches Dateiformat ausgewählt")
        return
    binary = binary[5:]
    num_ellipses = (len(bytearray(binary))-4)//11
    
    # Binärstring in einen Array aus Integern konvertieren
    data = unpack("HH"+"HHHH"*num_ellipses+"BBB"*num_ellipses,binary)
    width,height = data[0],data[1]
    # Cairo-Canvas erstellen
    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(ims)
    data = data[2:]
    
    # alle Ellipsen aus den Informationen der eingelesenen Datei generieren
    for i in range(num_ellipses):
            x,y,r1,r2 = data[i*4:i*4+4]
            x,y = x/65535*width,y/65535*height
            r1,r2 = r1/65535*width,r2/65535*height
            r,g,b = data[num_ellipses*4+i*3:num_ellipses*4+i*3+3]
            r,g,b = r/255,g/255,b/255
            cr.save()
            cr.set_source_rgba(r, g, b, 0.2)
            cr.translate(x,y)
            cr.scale(r1,r2)
            cr.arc(0, 0, 1, 0, 2*math.pi)
            cr.fill()
            cr.restore()
    
    # Speichern der Datei als JPG-Datei
    buf = ims.get_data()
    nparr = np.ndarray (shape=(width,height,4), dtype=np.uint8, buffer=buf)[:,:,:3]
    Image.fromarray(nparr).save("decompressed.png")

#Dekodieren der ausgewählten Datei
file = "output.eka"
decode(open(file,"rb"))