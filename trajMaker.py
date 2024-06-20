import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from math import atan2,sin,cos,pi,sqrt,acos
import sys,time
try:
    from PIL import Image, ImageTk
    withPil = True
except:
    withPil = False

"""
line: "type x(1) Y(1) Z(1) X(2) Y(2) Z(2) speed data plasma"
"""

"""
model from plasmagui (almost!):
  0   1    2    3     4    5    6   7      8     9
type x(1) y(1) z(1) x(2) y(2) z(2) data  speed plasma
there always x(1) y(1) z(1) = final point(0,1,2) and speed plasma (-2,-1)
"""
def filterDir(x,t):
    print(list(filter(lambda x:x.find(t)!=-1,dir(x))))

def ORDONNE(a,b,c,d):
    return (((a)<=(b)) and ((b)<=(c)) and ((c)<=(d)))

def isOnArc( te,  ts,  tp,  t):
    """
    arc te<->ts des deux cotes on garde celui qui contient tp,
    et on demande si t est dessus
    """
    if (ORDONNE(te, ts, tp, t)):
        return 1
    if (ORDONNE(te, tp, ts, t)):
        return 0
    if (ORDONNE(ts, te, tp, t)):
        return 1
    if (ORDONNE(ts, tp, te, t)):
        return 0
    if (ORDONNE(tp, te, ts, t)):
        return 1
    if (ORDONNE(tp, ts, te, t)):
        return 1

    if (ORDONNE(te, ts, t, tp)):
        return 1
    if (ORDONNE(te, tp, t, ts)):
        return 1
    if (ORDONNE(ts, te, t, tp)):
        return 1
    if (ORDONNE(ts, tp, t, te)):
        return 1
    if (ORDONNE(tp, te, t, ts)):
        return 0
    if (ORDONNE(tp, ts, t, te)):
        return 0

    if (ORDONNE(te, t, ts, tp)):
        return 0
    if (ORDONNE(te, t, tp, ts)):
        return 1
    if (ORDONNE(ts, t, te, tp)):
        return 0
    if (ORDONNE(ts, t, tp, te)):
        return 1
    if (ORDONNE(tp, t, te, ts)):
        return 1
    if (ORDONNE(tp, t, ts, te)):
        return 1

    if (ORDONNE(t, te, ts, tp)):
        return 1
    if (ORDONNE(t, te, tp, ts)):
        return 0
    if (ORDONNE(t, ts, te, tp)):
        return 1
    if (ORDONNE(t, ts, tp, te)):
        return 0
    if (ORDONNE(t, tp, te, ts)):
        return 1
    if (ORDONNE(t, tp, ts, te)):
        return 1
    return 0 

def rectangleExinscritEPS(xe, ye, xp, yp, xs, ys):
    """
    l'arc de cercle est la partie entre (xe,ye) et (xs,ys)
    du cercle defini par le parcours (xe,ye) -> (x,y) -> (xs,ys)
    cette fonction retourne les coordonnes du rectangle exinscrit a l'arc
    """
    xCenter, yCenter, R = cercleCano(xp, yp, xe, ye, xs, ys)
    tp = angle(xp - xCenter, yp - yCenter)
    te = angle(xe - xCenter, ye - yCenter)
    ts = angle(xs - xCenter, ys - yCenter)
    ymax = yCenter + R if isOnArc(te, ts, tp, pi / 2) else max(ye, ys) # NORD
    xmin = xCenter - R if isOnArc(te, ts, tp, pi) else min(ye, ys) # OUEST
    ymin = yCenter - R if isOnArc(te, ts, tp, 3 * pi / 2) else min(ye, ys) # SUD
    xmax = xCenter + R if isOnArc(te, ts, tp, 2 * pi) else max(ye, ys) # EST
    return xmin,ymin,xmax,ymax

def rectangleExinscritCES(xCenter, yCenter, xe, ye, xs, ys, sens):
    """
    l'arc de cercle est la partie du cercle de centre xc,yc entre (xe,ye)
    et (xs,ys) parcouru dans le sens (1=trigo,sinon clockwise)
    cette fonction retourne les coordonnes du rectangle exinscrit a l'arc
    """
    R = sqrt((xe-xCenter)**2 + (ye-yCenter)**2)
    te = angle(xe - xCenter, ye - yCenter)
    ts = angle(xs - xCenter, ys - yCenter)
    tp = (te+ts)/2 if sens else -(te+ts)/2
    xp = xCenter + R*cos(tp)
    yp = yCenter + R*sin(tp)
    print(f"rectangleExinscritCES: xe,ye,xp,yp,xs,ys={xe,ye,xp,yp,xs,ys}")
    return rectangleExinscritEPS(xe, ye, xp, yp, xs, ys),xp,yp

def angle(x,y) :
    """
    retourne l'angle dans [0,2*pi[
    """
    R = sqrt(x * x + y * y)
    t = acos(x / R) # 0<=t<=pi
    if (abs(R * sin(t) - y) > 1e-6):
        t = 2 * pi - t
    return t

def cercleCano(x1, y1, x2, y2, x3, y3,):
    """
    affecte le centre et rayons du cercle passant par (x1,y1),(x2,y2) et x3,y3)
    """
    denom = -2*x1*y3 + 2*y1*x3 - 2*x2*y1 + 2*x2*y3 + 2*y2*x1 - 2*y2*x3;
    num_xCenter = -x1*x1*y3 + y2*x1*x1 - y1*y2*y2 - y1*y1*y3 - y3*y3*y2 + y1*y3*y3 + y1*y1*y2 + y3*x2*x2 + y1*x3*x3 + y3*y2*y2 - y1*x2*x2 - x3*x3*y2
    num_yCenter = x1*x1*x3 - x1*x3*x3 - x1*y3*y3 + y1*y1*x3 + x2*x2*x1 - x2*x2*x3 - x2*x1*x1 - x2*y1*y1 + x2*x3*x3 + x2*y3*y3 + y2*y2*x1 - y2*y2*x3
    xCenter = num_xCenter / denom;
    yCenter = num_yCenter / denom;
    R = sqrt((x1 - xCenter)*(x1 - xCenter) + (y1 - yCenter)*(y1 - yCenter));
    return xCenter,yCenter,R

def fromPtsToCenterR(x1,y1,x2,y2,x3,y3):
    """
    return a string and 3 numbers = 'status',xc,yc,R
    """
    den = 2*x1*y2-2*x1*y3-2*y1*x2+2*y1*x3-2*x3*y2+2*y3*x2 # denominator of xC and yC
    if abs(den)<1e-5:
        return "small denominator",0,0,0
    numx = -y1*x2**2+y3*x2**2-y2**2*y1+y2*y1**2+y1*x3**2+y3**2*y1-x1**2*y3+x1**2*y2-y3*y1**2+y2**2*y3-x3**2*y2-y2*y3**2
    numy = -x1**2*x2+x1**2*x3+x1*x2**2+x1*y2**2-x1*x3**2-x1*y3**2-y1**2*x2+y1**2*x3+x3**2*x2-x3*x2**2-x3*y2**2+y3**2*x2
    xc = numx/den
    yc = numy/den
    R = sqrt((xc-x1)**2+(yc-y1)**2)
    RR = sqrt((xc-x2)**2+(yc-y2)**2)
    RRR = sqrt((xc-x3)**2+(yc-y3)**2)
    if abs(R-RR) + abs(R-RRR) > 1e-4:
        return "several different R determinations",0,0,0
    return  "ok",xc,yc,R
# FIN def fromPtsToCenterR(x1,y1,x2,y2,x3,y3):
# #####################################################################################

def create_arcParameter(xd,yd,xf,yf,xp,yp):
    """
    (xd,yd)=INITIAL POINT,  (xf,yf)=FINAL POINT,   (xp,yp)=INTERMEDIATE POINT
    return the status and the 4 positional parameters and start ans extent parameter as
    ("ok",x1,y1,x2,y2,start,extent) or ("message",0,0,0,0,0,0
    """
    stat,xc,yc,R = fromPtsToCenterR(xd,yd,xf,yf,xp,yp)
    # print(f"create_arcParameter: xc,yc,R={xc,yc,R}") #bidon
    if stat!='ok':
        return stat,0,0,0,0,0,0
    # angles determination in Rd
    Ad = atan2(yd-yc,xd-xc)
    Af = atan2(yf-yc,xf-xc)
    Ap = atan2(yp-yc,xp-xc)
    if Ad<0:Ad += 2*pi
    if Af<0:Af += 2*pi
    if Ap<0:Ap += 2*pi
    # swtich to degree for tkinter
    ad = Ad*180/pi
    af = Af*180/pi
    ap = Ap*180/pi
    # here the 3 angles are in Degree on [0,360[ 
    type=-1
    if ad<=ap and ap<af:   #dpf
        type=0
    elif ad<=af and af<ap: #dfp
        type=1
    elif af<=ad and ad<ap: #fdp
        type=2
    elif af<=ap and ap<ad: #fpd
        type=3
    elif ap<=ad and ad<af: #pdf
        type=4
    elif ap<=af and af<ad: #pfd
        type=5
    else:
        return "create_arcParameter: impossible error!",0,0,0,0,0,0
    if type==0 or type==3:
        extent  = ad-af
    else:
        extent= 360-(af-ad) if ad<af else -(af-ad)-360
        # print(f"create_arcParameter: ok,{xc-R},{yc-R},{xc+R},{yc+R},{ad},{extent}") #ok
    return "ok",xc-R,yc-R,xc+R,yc+R,-ad,extent
# FIN def create_arcParameter(xd,yd,xf,yf,xp,yp)
# #############################################################################################

class jcCheckbutton(ttk.Checkbutton):
    """
    a tk.Checkbutton which can be set or unset with .set(True) or .set(False)
    and read with .get() (return the state)
    """
    def __init__(self, parent,  **kwargs):
        variable = tk.IntVar()
        self.v = variable
        super().__init__(parent,  variable=variable, **kwargs)
    
    def get(self):
        return self.v.get()
    
    def set(self,v):
        self.v.set(v)
 # FIN class jcCheckbutton(ttk.Checkbutton)
# ##############################################################################

######################################################################################
#                                CLASS MATRIX                                        #
######################################################################################
class trajMaker():
    """
    The "trajMaker" allowing to draw a trajectory.
    A gui to create  trajectory as a list of section.
    A section is a collection of parameters.
    Hence the word trajMaker : rows correspond to section, column to parameters.
    1) my = trajMaker()
    2) root=tk.Tk();my=trajMaker(root) or my=trajMaker(tk.Tk()) (root is my.parent)
    3) my=trajMaker(tk.Toplevel())
    It can be instancied with a Toplevel, or without (root is then used)

    12 columns:
        0              1    ...      8            9          10     11
    ttk.Combobbox ttk.Entry ... ttk.Entry  jcCheckbutton tk.label jcCheckbutton
    """
    types = ["line","ezsqx","ezsqy","arc1","arc2","circ1","circ2","start","end","w"]
    implementedTypes = types[:] # usefull for adding new types of section
    widthCell = 6
    # le type doit etre un combobox en colonne 0 
    Dico={"line":{"type":0,"xF":1,"yF":2,"zF":3,"speed":8,"plasma":9},                 # point final
          "ezsqx":{"type":0,"xF":1,"yF":2,"nZigZag":4,"speed":8,"plasma":9},           # point final nb de zigzag
          "ezsqy":{"type":0,"xF":1,"yF":2,"nZigZag":4,"speed":8,"plasma":9},           # point final nb de zigzag
          "arc1":{"type":0,"xF":1,"yF":2,"xP":4,"yP":5,"speed":8,"plasma":9},          # point final point de passage (3 pts ==> OK)
          "arc2":{"type":0,"xF":1,"yF":2,"xC":4,"yC":5,"sens":6,"speed":8,"plasma":9}, # point final centre sens PAS FOPRCEMENT CONSISTENT
          "circ1":{"type":0,"xP1":1,"yP1":2,"xP2":4,"yP2":5,"speed":8,"plasma":9},     # point de passage 1  point de passage 2 (3 pts OK)
          "circ2":{"type":0,"xC":1,"yC":2,"sens":6,"speed":8,"plasma":9},              # centre et sens
          "w":{"type":0,"waitTime":1},                                                 # waiting time
          "start":{"type":0},                                                          # start
          "end":{"type":0,"speed":8}                                                   # end  
          }
    def __init__(self,parent=None,widthPhysical=800,heightPhysical=600,widthCanv=510, **kwargs):
        ##########################################################
        #                      PARAMETERS                        #
        ##########################################################
        colorSpecialAsHelpToWork = False
        self.arc2Fake = 1    # Ycenter computed not read in the GUI
        self.backgroundImageName = "./backgroundImage.jpg"
        closable = True # False is usefull sometimes to keep track of what happens 
        largParent,hautParent = 615,300
        largFrameM,hautFrameM = largParent,hautParent
        largCan,hautCan       = 604,300
        largFrame,hautFrame   = 0,0  # sans effet
        self.numberLineMax = 200
        largWind,hautWind     = largParent,19*self.numberLineMax
        largFrameS,hautFrameS = largParent,19
        bgParent = 'red'
        bgFrameB = 'green'
        bgFrameM = 'blue'
        bgCanvas = 'grey'
        bgFrame = 'yellow'
        bgWindow = 'magenta'
        ##########################################################
        #               END OF PARAMETERS                        #
        ##########################################################
        if parent==None:
            parent = tk.Toplevel()
        if not closable:
            parent.protocol("WM_DELETE_WINDOW", lambda:None) # prevent close window:
        parent.title("Trajectory Maker")
        parent.resizable(False, False)
        self.parent = parent
        self.backgroundImageId = -1 # no image to show yet
        parent.geometry(f"{largParent}x{hautParent}") # the window for the entry
        self.frameB = ttk.Frame(parent) # B for Button
        self.frameM = ttk.Frame(parent,width=largFrameM,height=hautFrameM-10*hautFrameS) # M for Main
        self.frameB.pack(expand=True)
        self.frameM.pack(expand=True)
        # creation du canvas et des scrollbars dans ce frame
        self.canvas = tk.Canvas(self.frameM,width=largCan,height=hautCan)
        self.scrollbar_y = ttk.Scrollbar(self.frameM, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        
        # Creation d'un autre frame a l'interieur du canvas pour contenir d'autres widget: THE FRAME
        self.frame = ttk.Frame(self.canvas, width=largFrame,height=hautFrame)
        self.style = ttk.Style()
        self.style.configure("red.TLabel", background="red")
        defColor = self.style.lookup("TLabel","background")
        self.style.configure("default.TLabel", background=defColor)
        if colorSpecialAsHelpToWork: # positionning helper
            parent.config(bg=bgParent)
            self.style.configure("FrameM.TFrame", background=bgFrameM)
            self.style.configure("FrameB.TFrame", background=bgFrameB)
            self.style.configure("Frame.TFrame", background=bgFrame)
            self.style.configure("white.TLabel", background="white")
            self.frameM.config(style="FrameM.TFrame")
            self.frameB.config(style="FrameB.TFrame")
            self.frame.config(style="Frame.TFrame")
            self.canvas.config(bg=bgCanvas)
        self.frame.pack(expand=True)
        # To place the self.frame in the self.canvas.canvas 
        self.windowId = self.canvas.create_window((0, 0), window=self.frame, anchor="nw",width=largWind,height=hautWind)
        # Mise a jour de la taille du canvas en fonction du contenu
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        def on_canvas_resize(event):
            # print(f"on_canvas_resize: entering event.width,event.height={event.width,event.height}")
            canvas_width = self.frameM.winfo_width() #event.width
            canvas_height = self.frameM.winfo_height() #event.height
            self.canvas.config( width=canvas_width, height=canvas_height)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
        self.canvas.bind("<Configure>", on_canvas_resize)
        self.widthCanv = widthCanv  
        self.heightCanv = heightPhysical/widthPhysical * widthCanv
        self.widthPhysical = widthPhysical
        self.heightPhysical = heightPhysical
        # Below the entry for the physical dimensions are installed
        labelHeight = ttk.Label(self.frameB,text="Height in mm (y)")
        self.physHeightVar = tk.StringVar()
        self.physHeightVar.set("%d"%heightPhysical)
        entryHeight = ttk.Entry(self.frameB,width=4,textvariable=self.physHeightVar)
        #
        labelWidth = ttk.Label(self.frameB,text="Width in mm (x)")
        self.physWidthVar = tk.StringVar()
        self.physWidthVar.set("%d"%widthPhysical)
        entryWidth = ttk.Entry(self.frameB,width=4,textvariable=self.physWidthVar)
        #
        bdel = ttk.Button(self.frameB,text="Delete selected lines",command=self.delSelectLines)
        badd = ttk.Button(self.frameB,text="Add a line",command=self.addLine)
        bSAll = ttk.Button(self.frameB,text="Select all",command=self.selectAll)
        bSNone = ttk.Button(self.frameB,text="Select none",command=self.deselectAll)
        bSave = ttk.Button(self.frameB,text="Show / Save",command=self.go)
        bLoad = ttk.Button(self.frameB,text="Load",command=lambda : self.loadFile(''))
        bdel.grid(row=1,column=0)
        badd.grid(row=1,column=1)
        bSAll.grid(row=1,column=2)
        bSNone.grid(row=1,column=3)
        bSave.grid(row=2,column=1)
        bLoad.grid(row=2,column=2)
        labelWidth.grid(row=0,column=0,sticky='e')
        entryWidth.grid(row=0,column=1,sticky='w')
        labelHeight.grid(row=0,column=2,sticky='e')
        entryHeight.grid(row=0,column=3,sticky='w')

        self.topDraw = 0
        self.copyed = [] # copyed line as dictionnary to be pasted if asked
        # below some initial sections
        if True:
            self.addLine("type=line xF=100 yF=100 zF=0 speed=5 plasma=1")
        if False:
            xc,yc=100,200
            xf,yf=100+100*cos(0.45),200+100*sin(0.45)
            self.addLine(f"type=arc2 xF={xf} yF={yf} xC={xc} yC={yc} sens=1  speed=8 plasma=0") # xf yf xc yc sens speed plasma
        if False:
            self.addLine("type=arc1 xF=200 yF=100 xP=150 yP=180 speed=12 plasma=0") # xf yf xp yp  speed plasma
        if False:
            self.addLine("type=circ1 xP1=200 yP1=120 xP2=150 yP2=180 speed=12 plasma=0") #
        if False:
            self.addLine("type=circ2 xC=200 yC=100 speed=12 sens=0 plasma=0") #
        if False:
            self.addLine("type=ezsqx xF=300 yF=320 nZigZag=5 speed=23 plasma=0") # xf yf nzigzag speed plasma
        if False:
            self.addLine("type=ezsqy xF=400 yF=400 nZigZag=9 speed=23 plasma=0") # xf yf nzigzag speed plasma
    # FIN def __init__(self,master=None, **kwargs):
    # ################################################################################

    def onDestroyTopDraw(self,event):
        self.backgroundImageId=-1
        
    def proccessTraj(self):
        """
        draw the trajectory OR write a file OR do it directly
        section : a string="type finalX finalY finale par_1 ... par_n speed plasma"
        """
        # print(f"proccesTraj: entering {self.trajDescript}")
        self.heightPhysical = int(self.physHeightVar.get())
        self.widthPhysical = int(self.physWidthVar.get())
        self.heightCanv = round(self.heightPhysical/self.widthPhysical * self.widthCanv)

        r = self.frame.size()
        if self.topDraw!=0:
            self.topDraw.destroy()
        self.topDraw = tk.Toplevel(width=self.widthCanv+10,height=self.heightCanv+100)
        self.topDraw.title("TRAJECTORY")
        self.topDraw.resizable(False,False)
        self.topDraw.bind("<Destroy>",self.onDestroyTopDraw) # so prevent hidding destroyed image !
        self.btn = ttk.Button(self.topDraw,text="save to file",command=self.saveToFile)
        self.btnBack = ttk.Button(self.topDraw,text="background",command=self.toggleBackgroundImage)
        # label with physical dim and mouse position
        labelContent = f"Physical dimensions={self.widthPhysical,self.heightPhysical}"
        self.labPhysicalDim = ttk.Label(self.topDraw,text=labelContent)
        w = 520 # self.topDraw.winfo_width()
        self.btn.place(x=1,y=20)
        self.btnBack.place(x=w-85,y=20)
        self.labPhysicalDim.place(x=w/2-100,y=20)
        convFactor = self.widthCanv/self.widthPhysical
        self.heightCan = convFactor*self.heightPhysical
        self.canvasImage = tk.Canvas(self.topDraw,width=self.widthCanv,height=self.heightCanv)
        self.canvasImage.config(bg='ivory')
        self.canvasImage.place(x=5,y=55)
        self.canvasImage.bind("<Motion>", lambda event: self.labPhysicalDim.configure(text=labelContent + f" {int((event.x)/convFactor),int((event.y)/convFactor)}"))
        # Background Image
        if withPil:
            try:
                self.image = Image.open(self.backgroundImageName)
                self.backgroundImage = ImageTk.PhotoImage(self.image)
                self.backgroundImageId = self.canvasImage.create_image(0, 0, anchor=tk.NW, image=self.backgroundImage)
            except :
                self.backgroundImageId = -1
                self.btnBack["state"] = tk.DISABLED
        else:
            self.btnBack["state"] = tk.DISABLED
            
        e = 2 # Line at x=0 or y=0 NOT seen if e=0
        xcur = 0
        ycur = 0
        for cpt,section in enumerate(self.trajDescript):
            # param common to all type of section
            x0 = xcur # debut de la section
            y0 = ycur # debut de la section
            localDico =dict()
            for ss in section.split():
                try:
                    k,v=ss.split("=")
                except:
                    print(f"processTraj: exception line 446 |section={section}| |ss={ss}|")
                localDico[k]=v
            type = localDico["type"]
            if type=="w" or type=="start" or type=="end":
                continue
            speed = localDico["speed"]
            plasma = localDico["plasma"]
            color = 'red' if plasma=="1" else 'green'
            w = int(speed)//10+1
            if type=='line':
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                zF = float(localDico["zF"])
                if xF>self.widthPhysical or yF>self.heightPhysical:
                    msg=f"line {cpt} (line) the final point is out of the frame"
                    messagebox.showerror("fatal",msg)
                    return
                self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xF+e,convFactor*yF+e, fill=color, width=2)
                xcur = xF
                ycur = yF
            elif type=="ezsqx":
                # first: a straight line         _
                # second: n              times _| |
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                if xF>self.widthPhysical or yF>self.heightPhysical:
                    msg=f"line {cpt} (ezsqx) the final point is out of the frame"
                    messagebox.showerror("fatal",msg)
                    return
                n = int(localDico["nZigZag"])
                LX = xF-xcur
                LY = yF-ycur
                L = LY
                l = LX/(2.0*n) if n!=0 else L
                self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*(ycur+L)+e, fill=color, width=w)
                ycur += L
                if n==0:
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*(xcur+l)+e,convFactor*ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur+l,ycur)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*(xcur+l)+e,convFactor*ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur-L)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*(ycur-L)+e, fill=color, width=w)
                    ycur -= L
                    # (xcur,ycur)->(xcur+l,ycur)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*(xcur+l)+e,convFactor*ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur+L)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*(ycur+L)+e, fill=color, width=w)
                    ycur += L
            elif type=="ezsqy":
                # first: a straight line         _
                # second: n          
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                if xF>self.widthPhysical or yF>self.heightPhysical:
                    msg=f"line {cpt} (ezsqy) the final point is out of the frame"
                    messagebox.showerror("fatal",msg)
                    return
                n = int(localDico["nZigZag"])
                LX = xF-xcur
                LY = yF-ycur
                L = LX
                l = LY/(2.0*n) if n!=0 else L
                self.canvasImage.create_line(convFactor*(xcur+L)+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*ycur+e, fill=color, width=w)
                xcur += L
                if n==0:
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*(ycur+l)+e,convFactor*xcur+e,convFactor*ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur,ycur+l)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*(ycur+l)+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur-L,ycur)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*(xcur-L)+e,convFactor*ycur+e, fill=color, width=w)
                    xcur -= L
                    # (xcur,ycur)->(xcur,ycur+l)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*xcur+e,convFactor*(ycur+l)+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur+L,ycur)
                    self.canvasImage.create_line(convFactor*xcur+e,convFactor*ycur+e,convFactor*(xcur+L)+e,convFactor*ycur+e, fill=color, width=w)
                    xcur += L
            elif type=="arc1": # pt final et pt passage
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xp = float(localDico["xP"]) # point de passage
                yp = float(localDico["yP"]) # point de passage
                status,a,b,c,d,start,extent = create_arcParameter(xd,yd,xF,yF,xp,yp)
                self.canvasImage.create_arc(convFactor*a+e,convFactor*b+e,convFactor*c+e,convFactor*d+e,start=start,extent=extent,style=tk.ARC,outline=color,width=w)
                if status!='ok':
                    messagebox.showinfo("information",status)
                # here test if the trajectory always in the frame
                xmin,ymin,xmax,ymax = rectangleExinscritEPS(xd, yd, xp, yp, xF, yF)
                if False: #show the rectangle exinscrit
                    self.canvasImage.create_rectangle(convFactor*xmin+e,convFactor*ymin+e,convFactor*xmax+e,convFactor*ymax+e)
                if xmin<0 or xmax>self.widthPhysical or ymax<0 or ymax>self.heightPhysical:
                    msg=f"line {cpt} (arc1) a part of the trajectory is out of the frame"
                    messagebox.showerror("fatal",msg)
                    return
                   
                xcur = xF
                ycur = yF
            elif type=="arc2": # pt final, centre et sens
                sens = int(localDico["sens"]) # sens
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                xc = float(localDico["xC"]) # x center
                if self.arc2Fake:
                    yc=0.5*(-2*xc*xF + xF**2 + yF**2 + 2*xc*xd - xd**2 - yd**2)/(yF-yd)
                    messagebox.showinfo("",f"ai force yc={yc} et je ne teste pas que la traj. reste dans le cadre")
                else:
                    yc = float(localDico["yC"]) # y center
                # print(f"xc,yc,sens={xc,yc,sens}") # bidon
                R2 = (xd-xc)**2 + (yd-yc)**2 # rayon calcule avec point courant
                R2a = (xF-xc)**2 + (yF-yc)**2 # rayon calcule avec point cible
                if abs(R2-R2a)>0.1: # les rayons sont de l'ordre de 10 a 100 
                    messagebox.showerror("Error",f"Inconsistent data for arc2 {R2,R2a} d,F,c={xd,yd,xF,yF,xc,yc}")
                    return
                R = sqrt(R2)
                AdR = atan2(yd-yc,xd-xc) # angle polaire debut
                AfR = atan2(yF-yc,xF-xc) # angle polaire fin
                if AdR<0:AdR += 2*pi
                if AfR<0:AfR += 2*pi
                ad = AdR*180/pi
                af = AfR*180/pi
                extent = (ad-af) if sens>0 else (ad-af)-360
                # print(f"self.canvasImage.create_arc({xc-R,yc-R,xc+R,yc+R},start={-ad},extent={extent},style={tk.ARC})") bidon
                self.canvasImage.create_arc(convFactor*(xc-R)+e,convFactor*(yc-R)+e,convFactor*(xc+R)+e,convFactor*(yc+R)+e,start=-ad,extent=extent,style=tk.ARC,outline=color,width=w)
                # if status!='ok':                    messagebox.showinfo("information",status)
                if False: # voir pourquoi ca ne marche pas
                    X,u,v= rectangleExinscritCES(xc, yc, xd, yd, xF, yF, sens)
                    xmin,ymin,xmax,ymax = X
                    print(f"u,v={u,v}")
                    self.canvasImage.create_oval(convFactor*(u)-2+e,convFactor*(v)-2+e,convFactor*(u)+2+e,convFactor*(v)+2+e)# visualieation du pt de passage
                    self.canvasImage.create_rectangle(convFactor*xmin+e,convFactor*ymin+e,convFactor*xmax+e,convFactor*ymax+e)
                xcur = xF
                ycur = yF
            elif type=="circ1": # pt de passage 1 pt de passage 2
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xP1 = float(localDico["xP1"]) # x passge1
                yP1 = float(localDico["yP1"]) # x passge1
                xP2 = float(localDico["xP2"]) # x passage2
                yP2 = float(localDico["yP2"]) # y passage2
                stat,xC,yC,R = fromPtsToCenterR(xd,yd,xP1,yP1,xP2,yP2)
                if stat!='ok':
                    messagebox.showerror("","Incompatible data for circ1 (probably the points are aligned)")
                    return
                if xC-R<0 or xC+R>self.widthPhysical or yC-R<0 or yC+R>self.heightPhysical:
                    msg=f"line {cpt} (circ1) some part of the trajectory is out of frame"
                    print(f"proccessTraj: circ1  stat,xC,yC,R={ stat,xC,yC,R}")
                    messagebox.showerror("fatal",msg)
                    return
                self.canvasImage.create_oval(convFactor*(xC-R)+e,convFactor*(yC-R)+e,convFactor*(xC+R)+e,convFactor*(yC+R)+e,outline=color,width=w)
                xF = xcur
                yF = ycur
            elif type=="circ2": #  centre et sens
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xC = float(localDico["xC"]) # x center
                yC = float(localDico["yC"]) # y center
                R = sqrt((xcur-xC)**2 + (ycur-yC)**2)
                sens = int(localDico["sens"]) 
                if xC-R<0 or xC+R>self.widthPhysical or yC-R<0 or yC+R>self.heightPhysical:
                    msg=f"line {cpt} (circ2) some part of the trajectory is out of frame"
                    messagebox.showerror("fatal",msg)
                    return
                self.canvasImage.create_oval(convFactor*(xC-R)+e,convFactor*(yC-R)+e,convFactor*(xC+R)+e,convFactor*(yC+R)+e,outline=color,width=w)
                xF = xd # closed circle
                yF = yd # closed circle
            else:
                messagebox.showinfo("information",f"processTraj: {type} not yet implemented")
            if (xcur-xF)**2 + (ycur-yF)**2 >1e-5:
                messagebox.showinfo("Erreur Grave",f"type={type} Pt final {xcur,ycur} loin de celui demande={xF,yF}")
        # fin du traitement de la section
    # FIN def proccessTraj(self):
    # ################################################################################

    def go(self):
        """
        section : a string="type finalX finalY finale par_1 ... par_n speed plasma"
        """
        c,r = self.frame.grid_size()
        self.trajDescript = []
        # checking syntax
        for l in range(r):
            if self.frame.grid_slaves(row=l,column=0)==[]:
                continue
            if not self.frame.grid_slaves(row=l,column=c-1)[0].get(): # not selected
                continue
            w = self.frame.grid_slaves(row=l,column=0)[0]
            type = w.get()
            if type =="":
                continue
            if not type in self.implementedTypes:
                messagebox.showinfo("information","one of the types is not implemented")
                return  # since the type is not yet implemented (TODO)
            # here a type implemented
            dico = self.Dico[type]
            params=dico.keys()
            parameters= "type="+type+" "
            for key in dico.keys():
                k = dico[key]
                val = self.frame.grid_slaves(row=l,column=k)[0].get()
                if val==True:
                    val="1"
                elif val==False:
                    val="0"
                if key!="type":
                    # Check that is it a string representing a float
                    ok = True
                    try:
                        x = float(val)
                    except:
                        ok = False
                    if not ok:
                        messagebox.showerror("Can't proccess",f"A wrong entry on line {l} column {k} value={val}")
                        print(f"line {l} column {k} value={val} type={type} key={key}")
                        return
                parameters += key+"="+val+" "
            self.trajDescript.append(parameters)
        self.proccessTraj()
    # FIN def go(self):
    # ################################################################################

    def toggleBackgroundImage(self):
        """
        toggle the background image in the canvas if present, else do nothing
        """
        if self.backgroundImageId==-1:
            return
        if self.canvasImage.itemconfigure(self.backgroundImageId)['state'][-1]=='hidden':
            self.showBackgroundImage()
        else:
            self.hideBackgroundImage()
    # FIN def toggleBackgroundImage(self)
    # ################################################################################

    def hideBackgroundImage(self):
        """
        hide the background image in the canvas if present, else do nothing
        """
        # print(f"hideBackgroundImage: entering self.backgroundImageId={self.backgroundImageId}")
        if self.backgroundImageId==-1:
            return
        self.canvasImage.itemconfigure(self.backgroundImageId,state="hidden")
    # FIN def hideBackgroundImage(self)
    # ################################################################################

    def showBackgroundImage(self):
        """
        show the background image in the canvas if present, else do nothing
        """
        if self.backgroundImageId==-1:
            return
        self.canvasImage.itemconfigure(self.backgroundImageId,state="normal")
    # FIN def showBackgroundImage(self)
    # ################################################################################

    def delAll(self):
        """
        the line is still in the grid but all cells of the are none
        """
        c,r = self.frame.grid_size()
        print(f"delAll: entering  c,r={c,r} at {time.time()}")
        self.frame.update_idletasks()
        tDeb = time.time()
        for w in self.frame.grid_slaves():
            w.destroy()
        self.frame.after_idle(lambda : print(f"loadFile callback: {r,tDeb,(time.time()-tDeb)}"))
        print(f"delAll: leaving at {time.time()}")
    # FIN def delAll(self):
    # ################################################################################

    def delSelectLines(self):
        """
        the line is still in the grid but all cells of the are none
        """
        c,r = self.frame.grid_size()
        print(f"delSelectLines: entering  c,r={c,r} at {time.time()}")
        kept=[]
        for irow in range(r):
            if self.frame.grid_slaves(row=irow,column=0)==[]:
                continue
            doIt = self.frame.grid_slaves(row=irow,column=11)[0].get()
            if doIt: # selectelines
                self.delLine(irow)
        print(f"delSelectLines: leaving at {time.time()}")
    # FIN def delSelectLines(self):
    # ################################################################################

    def overWriteLine1ByLine2(self,line1,line2):
        """
        line1 is REPLACED by line2,
        therefore line2 appears twice and line1 does not appear anymore
        """
        c,r = self.frame.grid_size()
        print(f"overWriteLine1ByLine2: entering c,r={c,r}")
        if line1>=r or line2>=r:
            return
        for icol in range(c):
            w = self.frame.grid_slaves(row=line2,column=icol)[0]
            self.frame.grid_slaves(row=line1,column=icol)[0].destroy()
            input("?")
            w.grid(row=line1,column=icol)
            input("??")
    # FIN def overWriteLine1ByLine2(self,line1,line2)
    # ################################################################################
    
    def delLine(self,line):
        """
        all cells of line are destroy (ie contains []),
        therefore the number of row is NOT changed, but empy line are not shown
        """
        c,r = self.frame.grid_size()
        # print(f"delLine: entering c,r,line={c,r,line}")
        # self.frame.update_idletasks()
        if line<0 or line>= r :
            return
        # delete line
        for icol in range(c):
            if self.frame.grid_slaves(row=line,column=icol) != []:
                self.frame.grid_slaves(row=line,column=icol)[0].destroy()
        #self.renumber()
        # print(f"delLine: leaving  c,r={self.frame.grid_size()}")
    # FIN def delLine (self,line)
    # ################################################################################
            
    def deselectAll(self):
        c,r = self.frame.grid_size()
        for i in range(r):
            self.frame.grid_slaves(row=i,column=11)[0].set(False) # selected lines
    # FIN def deselectAll(self):
    # ################################################################################

    def selectAll(self):
        c,r = self.frame.grid_size()
        for i in range(r):
            if self.frame.grid_slaves(row=i,column=11)==[]:
                continue
            self.frame.grid_slaves(row=i,column=11)[0].set(True)
    # FIN def selectAll(self):
    # ################################################################################

    def comboboxSelect(self,event,irow):
        """
        called by the combobox of row=irow and column=0 
        """
        c,r=self.frame.grid_size()
        #print(f"comboSelect: entering  c,r={c,r}")
        w = self.frame.grid_slaves(row=irow,column=0)[0]
        newType = w.get()
        # reset common for all type
        for k in range(1,9):
            self.frame.grid_slaves(row=irow,column=k)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=k)[0].config(state="disabled")
        self.frame.grid_slaves(row=irow,column=8)[0].config(state="normal") # speed
        self.frame.grid_slaves(row=irow,column=8)[0].delete(0,tk.END)
        self.frame.grid_slaves(row=irow,column=8)[0].insert(0,"Speed")
        self.frame.grid_slaves(row=irow,column=9)[0].config(state="normal")
        self.frame.grid_slaves(row=irow,column=9)[0].config(state="selected") # plasma checkbutton
        # specific reset for different type
        if newType=="line":
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=irow,column=3)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=3)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=3)[0].insert(0,"Zend")
        elif newType=="ezsqx" or newType=="ezsqy":
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=irow,column=4)[0].config(state="normal")
            self.frame.grid_slaves(row=irow,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=4)[0].insert(0,"Nzigzag")
        elif newType=="arc1" :
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal") # xFin
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal") # yFin
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=irow,column=4)[0].config(state="normal") # xPassage
            self.frame.grid_slaves(row=irow,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=4)[0].insert(0,"xPass")
            self.frame.grid_slaves(row=irow,column=5)[0].config(state="normal") # yPassage
            self.frame.grid_slaves(row=irow,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=5)[0].insert(0,"yPass")
        elif newType=="arc2":
            if self.arc2Fake:
                messagebox.showinfo("Warning","This is a test version: the yCenter is DEDUCED from xFinal,yFinal,xCenter")
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal") # xFin
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal") # yFin
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=irow,column=4)[0].config(state="normal") # xCenter
            self.frame.grid_slaves(row=irow,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=4)[0].insert(0,"xCenter")
            self.frame.grid_slaves(row=irow,column=5)[0].config(state="normal") # yCenter
            self.frame.grid_slaves(row=irow,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=5)[0].insert(0,"yCenter")
            self.frame.grid_slaves(row=irow,column=6)[0].config(state="normal") # sens
            self.frame.grid_slaves(row=irow,column=6)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=6)[0].insert(0,"sens<>0")
        elif newType=="circ1":
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal") # xPassage1
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"xPas1")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal") # yPassage1
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"yPas1")
            self.frame.grid_slaves(row=irow,column=4)[0].config(state="normal") # xPassage2
            self.frame.grid_slaves(row=irow,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=4)[0].insert(0,"xPas2")
            self.frame.grid_slaves(row=irow,column=5)[0].config(state="normal") # yPassage2
            self.frame.grid_slaves(row=irow,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=5)[0].insert(0,"yPas2")
        elif newType=="circ2":
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal") # xCenter
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"xCenter")
            self.frame.grid_slaves(row=irow,column=2)[0].config(state="normal") # yCenter
            self.frame.grid_slaves(row=irow,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=2)[0].insert(0,"yCenter")
            self.frame.grid_slaves(row=irow,column=6)[0].config(state="normal") # sens
            self.frame.grid_slaves(row=irow,column=6)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=6)[0].insert(0,"sens<>0")
        elif newType=="w":
            self.frame.grid_slaves(row=irow,column=1)[0].config(state="normal")  # waiting time
            self.frame.grid_slaves(row=irow,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=1)[0].insert(0,"t 1/10s")
            self.frame.grid_slaves(row=irow,column=8)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=8)[0].config(state="disabled") # speed
        elif newType=="end":                                                      # end
            self.frame.grid_slaves(row=irow,column=8)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=8)[0].config(state="disabled") # speed
            self.frame.grid_slaves(row=irow,column=8)[0].config(state="normal")   # speed
            self.frame.grid_slaves(row=irow,column=8)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=8)[0].insert(0,"Speed")
        elif newType== "start":                                                   # start
            self.frame.grid_slaves(row=irow,column=8)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=irow,column=8)[0].config(state="disabled") # speed
        else:
            messagebox.showinfo("Show info","Not yet implemented")
    # FIN def comboboxSelect(self,event,r):
    # ################################################################################

    def insertLineBelow(self,line,toplevelEditLine,lineToInsert=[]):
        """
        insert an empty line after line k, 0<=k<r
        """
        c,r = self.frame.grid_size()
        if line<0 or line>=r:
            toplevelEditLine.destroy()
            return
        print(f"Entering insertLineBelow duplique decale vers le bas les lignes {line} .. derniere ")
        c,r = self.frame.size()
        self.addLine()
        if line==r-1:
            toplevelEditLine.destroy()
            return           
        # duplication des combobox de choix de type column=0
        for irow in range(r-1,line,-1):
            print(f"insertLineBelow: irow={irow}")
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            print(f"insertLineBelow:type={type}")
            self.frame.grid_slaves(row=irow+1,column=0)[0].set(type)
        self.frame.grid_slaves(row=line+1,column=0)[0].set("")
        # duplications des parametres de col 1 a col 9
        for icol in range(1,9):
            for irow in range(r-1,line,-1):
                if 'disabled' in self.frame.grid_slaves(row=irow,column=icol)[0].state():
                    self.frame.grid_slaves(row=irow+1,column=icol)[0].delete(0,tk.END)
                    self.frame.grid_slaves(row=irow+1,column=icol)[0].config(state="disabled")
                    continue
                self.frame.grid_slaves(row=irow+1,column=icol)[0].config(state="enabled")
                val = self.frame.grid_slaves(row=irow,column=icol)[0].get()
                val2 = self.frame.grid_slaves(row=irow+1,column=icol)[0].get()
                print(f"moving row {irow} with {val} to {irow+1} with {val2}")
                self.frame.grid_slaves(row=irow+1,column=icol)[0].delete(0,tk.END)
                self.frame.grid_slaves(row=irow+1,column=icol)[0].insert(0,val)
            self.frame.grid_slaves(row=line+1,column=icol)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=line+1,column=icol)[0].insert(0,"")
        toplevelEditLine.destroy()
        self.renumber()
        return
        # FIN def insertLineBelow(self,line,toplevelEditLine):
    # ################################################################################

    def insertLineAbove(self,line,toplevelEditLine,lineToInsert=[]):
        """
        insert an empty line after line, 0<=k<r moving 
        """
        c,r = self.frame.grid_size()
        if line<0 or line>=r:
            toplevelEditLine.destroy()
            return
        print("duplique decale vers le bas les lignes {line} .. derniere ")
        c,r = self.frame.size()
        self.addLine()
        # duplication des combobox de choix de type column=0
        for irow in range(r-1,line-1,-1):
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            self.frame.grid_slaves(row=irow+1,column=0)[0].set(type)
        self.frame.grid_slaves(row=line,column=0)[0].set("")
        # duplications des parametres de col 1 a col 9
        for icol in range(1,9):
            for irow in range(r-1,line-1,-1):
                if 'disabled' in self.frame.grid_slaves(row=irow,column=icol)[0].state():
                    self.frame.grid_slaves(row=irow+1,column=icol)[0].delete(0,tk.END)
                    self.frame.grid_slaves(row=irow+1,column=icol)[0].config(state="disabled")
                    continue
                self.frame.grid_slaves(row=irow+1,column=icol)[0].config(state="enabled")
                val = self.frame.grid_slaves(row=irow,column=icol)[0].get()
                val2 = self.frame.grid_slaves(row=irow+1,column=icol)[0].get()
                print(f"moving row {irow} with {val} to {irow+1} with {val2}")
                self.frame.grid_slaves(row=irow+1,column=icol)[0].delete(0,tk.END)
                self.frame.grid_slaves(row=irow+1,column=icol)[0].insert(0,val)
            self.frame.grid_slaves(row=line,column=icol)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=line,column=icol)[0].insert(0,"")
        toplevelEditLine.destroy()
        self.renumber()
        return
        # FIN def insertLineAbove(self,line,toplevelEditLine):
    # ################################################################################
    
    def removeLine(self,line,toplevelEditLine):
        print(f"removeLine: entering with {line} {toplevelEditLine}")
        for icol in range(11):
            self.frame.grid_slaves(row=line,column=icol)[0].grid_remove()
        toplevelEditLine.destroy()
        self.renumber()
    # FIN def removeLine(self,line,toplevelEditLine)
    # ################################################################################
    
    def copyLine(self,line,toplevelEditLine):
        c,r = self.frame.grid_size()
        ok = True
        try:
            type = self.frame.grid_slaves(row=line,column=0)[0].get()
            paramDico = self.Dico[type]
        except:
            ok = False
        if not ok:
            messagebox.showerror("fatal error","type not accessible")
            toplevelEditLine.destroy()
            return
        toplevelEditLine.destroy()
        dicoCopied= {}
        for key in paramDico.keys():
            w = self.frame.grid_slaves(row=line,column=paramDico[key])[0]
            print(f"copyLine: {paramDico[key],w}")
            val = w.get()
            print(f"val={val}")
            dicoCopied[key]=val
        print(f"insertLineBelow: copied={dicoCopied}")
        self.copyed.append(dicoCopied)
        self.renumber()
    # FIN def copyLine(self,line,toplevelEditLine)
    # ################################################################################
        
    def pasteLine(self,line,toplevelEditLine):
        c,r = self.frame.grid_size()
        if len(self.copyed)==0:
            return
        # on va REMPLACER la ligne courante
        for icol in range(1,9): # le combobox reste le meme
            self.frame.grid_slaves(row=line,column=icol)[0].delete(0,tk.END)
        paramDico = self.copyed[0]
        type = paramDico["type"]
        self.dicoToLine(line,paramDico)
        toplevelEditLine.destroy()
        self.renumber()
    # FIN def pasteLine(self,line,toplevelEditLine)
    # ################################################################################

    def addLine(self,line=""):
        def close(event = ""):
            # print(f"je ferme {event}")
            return
        def editLine(event,line):
            print("entering editLine ",line)
            toplevelEditLine = tk.Toplevel()
            toplevelEditLine.title("Edit")
            toplevelEditLine.protocol("WM_DELETE_WINDOW",close )
            toplevelEditLine.bind("<Destroy>", close)
            # while this toplevel is living NO other action is possible :
            toplevelEditLine.focus_force()
            toplevelEditLine.wait_visibility()
            toplevelEditLine.grab_set()
            lab = ttk.Label(toplevelEditLine,text="Line %d"%(line+1),width=17)
            butInsBel = ttk.Button(toplevelEditLine,text="Insert line below",width=17,command=lambda :self.insertLineBelow(line,toplevelEditLine))
            butInsAbo = ttk.Button(toplevelEditLine,text="Insert line above",width=17,command=lambda :self.insertLineAbove(line,toplevelEditLine))
            butDel = ttk.Button(toplevelEditLine,text="Delete line",width=17,command=lambda :self.removeLine(line,toplevelEditLine))
            butCop = ttk.Button(toplevelEditLine,text="Copy line",width=17,command=lambda :self.copyLine(line,toplevelEditLine))
            butPas = ttk.Button(toplevelEditLine,text="Paste line",width=17,command=lambda :self.pasteLine(line,toplevelEditLine))
            butCancel = ttk.Button(toplevelEditLine,text="Cancel",width=17,command= lambda: toplevelEditLine.destroy())
            lab.grid(column=0,row=0)
            butInsAbo.grid(column=0,row=1)
            butInsBel.grid(column=0,row=2)
            butDel.grid(column=0,row=3)
            butCop.grid(column=0,row=4)
            butPas.grid(column=0,row=5)
            butCancel.grid(column=0,row=6)
        # FIN def editLine(event):
        # THE WIDGETS:
        # ################################################################
        #      0          1..8          9           10         11        #
        # ttk.Combobox 8xttk.Entry jcCheckButton ttk.Label jcCheckbutton #
        ##################################################################
        c,r = self.frame.grid_size()
        if r >= self.numberLineMax-1:
            messagebox.showerror("error",f"maximum number of line {self.numberLineMax} reached")
            return
        w = ttk.Combobox(self.frame,values=self.types,width=self.widthCell,state="readonly")
        w.bind("<<ComboboxSelected>>", lambda  event : self.comboboxSelect(event,r))
        w.grid(row=r,column=0) # choix de prochain section
        for k in range(1,9):
            w = ttk.Entry(self.frame,width=self.widthCell)
            w.config(state="disabled")
            w.grid(row=r,column=k) # position finale du premier section
        w = jcCheckbutton(self.frame,text="Plasma",width=self.widthCell+1)
        w.set(False);
        w.grid(row=r,column=9) # plasma
        w = ttk.Label(self.frame,text="%d"%(r+1),borderwidth=0.5,width=4,relief="solid")
        w.grid(row=r,column=10) # label
        w.bind('<Button-1>', lambda event : editLine(event,r))
        w.bind("<Enter>", lambda event :event.widget.config(style="red.TLabel"))
        w.bind("<Leave>", lambda event :event.widget.config(style="default.TLabel"))
        w = jcCheckbutton(self.frame,width=0)
        w.set(True);
        w.grid(row=r,column=11) # selecteur        
        if line=="":
            return
        # ######################## HERE WE add ADD line GIVEN AS ARGUMENT ########################
        # line is a STRING "type=xxx xF=xxx       speed=xxx plasma=xxx
        dico = self.strToDico(line)
        self.dicoToLine(r,dico)
        return
    # FIN def addLine(self,line=""):
    # ################################################################################        

    def xchangeWidgets(self,column0=0,row0=0,column1=1,row1=1):
        """
        exchange the two widgets in position (row0,column0) and (row1,column1)
        """
        c,r = self.frame.grid_size()
        if row0<0 or row0>=r or row1<0 or row1>=r:
            return
        w0 = self.frame.grid_slaves(row=row0,column=column0)[0]
        w1 = self.frame.grid_slaves(row=row1,column=column1)[0]
        w0.grid_remove()
        w1.grid_remove()
        w0.grid(row=row1,column=column1)
        w1.grid(row=row0,column=column0)

    def renumber(self):
        c,r = self.frame.grid_size()
        z = 1
        for i in range(r):
            if self.frame.grid_slaves(row=i,column=10)!= []:
                self.frame.grid_slaves(row=i,column=10)[0]["text"] = "%d"%z
                z += 1
    # FIN def renumber(self):
    # ################################################################################
    
    def loadFile(self,name=""):
        """
        load the choosen file, update the GUI accordingly
        """
        c,r = self.frame.grid_size()
        # print(f"loadFile: entering  c,r={c,r}")
        # tDeb= time.time()
        if name=="":
            dataFile = filedialog.askopenfile()
        else:
            try:
                dataFile = open(name,"r")
            except:
                dataFile = None
        if dataFile is None:
            return
        try :
            lines =dataFile.readlines()
            ok = True
        except:
            messagebox.showerror("Error",f"Could not open the file {dataFile} for reading")
            ok = False
        if not ok:
            return
        # creat a warning window
        topWarner = tk.Toplevel()
        topWarner.title("warning")
        w = self.frameM.winfo_width()
        h = self.frameM.winfo_height()
        x = self.frameM.winfo_rootx()
        y = self.frameM.winfo_rooty()
        topWarner.geometry(f"{w}x{h}+{x}+{y}")
        lab = ttk.Label(topWarner,text="This operation can be long ...")
        lab.pack()
        topWarner.transient() # rend la fenetre modale ie plus d'interaction avec les autres
        topWarner.grab_set() # tous les evnements sont envoyés a ta
        topWarner.update()
        # ESSAI D'ACCELERATION DE LOAD
        self.frame.grid_propagate(False)
        self.frame.update_idletasks()
        # FIN ESSAI D'ACCELERATION DE LOAD
        # update the gui
        for w in self.frame.grid_slaves():
            w.destroy()
        for cpt,line in enumerate(lines):
            self.frame.update_idletasks()
            if cpt>=self.numberLineMax:
                break
            self.addLine(line)
        # self.frame.after_idle(lambda : print(f"loadFile callback: n,tDeb,duree={r,tDeb,(time.time()-tDeb)}"))
        topWarner.destroy()
        # print(f"loadFile: leaving")
    # FIN def loadFile(self)
    # ################################################################################
    
    def saveToFile(self):
        """
        Save with the format imposed by plasmagui
        """
        c,r = self.frame.grid_size()
        print(f"saveToFile: entering c,r={c,r}")
        fileName = filedialog.asksaveasfilename()
        if fileName=='':
            return # since "cancel" has been used
        try:
            f = open(fileName,"w")
            ok = True
        except:
            messagebox.showerror("Could not open the file {fileName} for writing")
            ok = False
        if not ok:
            return
        # f.writelines(enTete)
        sections = ""
        for irow in range(r):
            if self.frame.grid_slaves(row=irow,column=0)==[]:
                continue
            paramDico=self.lineToDico(irow)
            section = self.dicoToStr(paramDico) + '\n'
            sections += section
        f.writelines(sections)
        f.close()
    # FIN def saveToFile(self)
    # ################################################################################        

    def strToDico(self,line):
        """
        return the dictionnary obtained from line
        line is key=val ... ley=val
        """
        ans = {}
        ls = line.split()
        for i in ls:
            ok = True
            try:
                key,val = i.split("=")
            except:
                ok = False
            if not ok:
                aux = line.replace("\n","") # windows needs that !
                messagebox.showerror("in strToDico",f"line {aux} not OK")
                sys.exit(0)
            ans[key] = val
        return ans
    # FIN def strToDico(self,line)
    # ################################################################################

    def dicoToStr(self,dico):
        """
        return a string representing the dico
        line is key=val ... ley=val
        """
        ans=""
        for key,val in dico.items():
            ans +=f"{key}={val} "
        return ans
    # FIN def strToDico(self,line)
    # ################################################################################
    
    def insertSelectedLineInPlace(self,line):
        """
        replace the single "line" by the list of lines of the selected lines       
        """
        c,r = self.frame.grid_size()
        print(f"insertSelectedLineInPlace: entering  c,r={c,r}")
        for irow in range(r):
            if  not self.frame.grid_slaves(row=irow,column=11)[0].get():
                continue
            # a line to insert : make the corresponding dictionnary
            paramDico={}
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            localDico = self.Dico[type]
            for key in localDico.keys():
                col = localDico[key]
                val = self.frame.grid_slaves(row=irow,column=col)[0].get()
                paramDico[key] = val
            print(f"{paramDico}")
    # FIN def insertSelectedLineInPlace(self)
    # ################################################################################

    def lineToDico(self,line):
        """
        return the dictionnary corresponding line
        """
        # print(f"lineToDico: entering")
        c,r = self.frame.grid_size()
        if line >=r or line<0:
            return
        paramDico={}
        type = self.frame.grid_slaves(row=line,column=0)[0].get()
        localDico = self.Dico[type]
        for key in localDico.keys():
            col = localDico[key]
            val = self.frame.grid_slaves(row=line,column=col)[0].get()
            paramDico[key] = val
        return paramDico
    # FIN  def lineToDico(self,line):
    # ################################################################################
    
    def dicoToLine(self,irow,paramDico):
        """
        set line irow of grid to paramDico, OVERWRITING the actual content
        """
        c,r = self.frame.grid_size()
        # print(f"dicoToLine: entering with r,c={r,c} irow={irow}")
        if irow >=r or irow<0:
            return
        # remove acutal line irow
        typeActual = self.frame.grid_slaves(row=irow,column=0)[0].get() # le type en colonne 0
        if typeActual!='':
            print(f"dicoToLine: removing typeActual={typeActual}")
            for icol in self.Dico[typeActual].values():
                print(f"dicoToLine: removing {irow,icol}")
                w = self.frame.grid_slaves(row=irow,column=icol)[0]
                if isinstance(w,ttk.Entry):
                    self.frame.grid_slaves(row=irow,column=icol)[0].delete(0,tk.END)
                    self.frame.grid_slaves(row=irow,column=icol)[0].config(state="disabled")
        # set new values
        type = paramDico["type"]            
        for key in paramDico.keys():
            col = self.Dico[type][key]
            val = paramDico[key]
            #print(f"lineToDico: en {col} mettre {val}")
            w = self.frame.grid_slaves(row=irow,column=col)[0]
            w.config(state="enabled")
            if isinstance(w,ttk.Combobox):
                w.set(val)
            elif isinstance(w,ttk.Entry):
                w.insert(0,val)
            elif isinstance(w,ttk.Label):
                w.insert(0,val)
            elif isinstance(w,jcCheckbutton):
                w.set(val)
            else:
                messagebox.showerror("","aucun des 4 types connus")
                return        
    # FIN  def lineToDico(self,line):
    # ################################################################################

    def dim(self):
        """
        output the width of pribcipal widget
        """
        print(f"self.parent={self.parent.winfo_width()}")
        print(f"self.frameB={self.frameB.winfo_width()}")
        print(f"self.frameM={self.frameM.winfo_width()}")
        print(f"self.canvas={self.canvas.winfo_width()}")
        #print(f"self.window={self.window}")
        print(f"self.frame={self.frame.winfo_width()}")
        print(f"self.scrollbar_y={self.scrollbar_y.winfo_width()}")

    def guiToTable(self):
        c,r = self.frame.grid_size()
        print(f"guiToDico: entering  c,r={c,r}")
        table=[]
        for irow in range(r):
            L=[]
            for icol in range(c):
                l = self.frame.grid_slaves(row=irow,column=icol)
                if l==[]:
                    L.append(None)
                else:
                    L.append(l[0])
            table.append(L)
        return table

if __name__=='__main__':
    root = tk.Tk()
    root.title("ROOT")
    my=trajMaker(root,widthPhysical=800,heightPhysical=600)
    if 'test' in sys.argv:
        import os
        fichiers = os.listdir("examples")
        for f in fichiers:
            print(f)
            my.loadFile("examples/%s"%f)
            my.go()
            my.backgroundImageId = 1
            my.hideBackgroundImage()
            input("?")
    # root.mainloop()


