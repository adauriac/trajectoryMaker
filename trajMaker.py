import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from math import atan2,sin,cos,pi,sqrt

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

def create_arcParameter(xd,yd,xf,yf,xp,yp):
    """
    (xd,yd)=INITIAL POINT,  (xf,yf)=FINAL POINT,   (xp,yp)=INTERMEDIATE POINT
    return the status and the 4 positional parameters and start ans extent parameter as
    ("ok",x1,y1,x2,y2,start,extent) or ("message",0,0,0,0,0,0
    """
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
    stat,xc,yc,R = fromPtsToCenterR(xd,yd,xf,yf,xp,yp)
    # print(f"ds create_arcParameter xc,yc,R={xc,yc,R}") #bidon
    if stat!='ok':
        return stat,0,0,0,0,0,0
    # angles determination in Rd
    Ad = atan2(yd-yc,xd-xc)
    Af = atan2(yf-yc,xf-xc)
    Ap = atan2(yp-yc,xp-xc)
    if Ad<0:Ad += 2*pi
    if Af<0:Af += 2*pi
    if Ap<0:Ap += 2*pi
    # print(f"ds create_ArcP les 3 pts: {xc+R*cos(Ad),yc+R*sin(Ad)},{xc+R*cos(Af),yc+R*sin(Af)},{xc+R*cos(Ap),yc+R*sin(Ap)}")
    # swtich to degree for tkinter
    ad = Ad*180/pi
    af = Af*180/pi
    ap = Ap*180/pi
    # print(f"ds sub en rd Ad,Af,Ap={Ad,Af,Ap}") # bidon
    # print(f"ds sub en dg ad,af,ap={ad,af,ap}") # bidon
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
        return "impossible error!",0,0,0,0,0,0
    if type==0 or type==3:
        extent  = ad-af
    else:
        extent= 360-(af-ad) if ad<af else -(af-ad)-360
        # print(f"ok,{xc-R},{yc-R},{xc+R},{yc+R},{ad},{extent}") #ok
    return "ok",xc-R,yc-R,xc+R,yc+R,-ad,extent
# FIN def create_arcParameter(xd,yd,xf,yf,xp,yp)

class jcCheckbutton(ttk.Checkbutton):
    """
    a tk.Checkbutton which can be set or unset with .set(True) or .set(False)
    and read with .get() (return the state)
    """
    def __init__(self, parent,  **kwargs):
        variable = tk.BooleanVar()
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
        0      1    ...   8        9     10     11
    combobbox entry ... entry  checkbox label selected
    """
    types = ["line","ezsqx","ezsqy","arc1","arc2","circ1","circ2","start","end","w"]
    implementedTypes = ["line","ezsqx","ezsqy","arc1","arc2"]
    widthCell = 6
    Dico={"line":{"xF":1,"yF":2,"zF":3,"speed":8,"plasma":9},        # point final
          "ezsqx":{"xF":1,"yF":2,"nZigZag":4,"speed":8,"plasma":9},  # point final nb de zigzag
          "ezsqy":{"xF":1,"yF":2,"nZigZag":4,"speed":8,"plasma":9},  # point final nb de zigzag
          "arc1":{"xF":1,"yF":2,"xP":4,"yP":5,"speed":8,"plasma":9}, # point final point de passage (3 pts ==> OK)
          "arc2":{"xF":1,"yF":2,"xC":4,"yC":5,"sens":6,"speed":8,"plasma":9}, # point final centre sens PAS FOPRCEMENT CONSISTENT
          "circ1":{"xP1":1,"yP1":2,"xP2":4,"yP2":5,"speed":8,"plasma":9}, # point de passage 1  point de passage 2 (3 pts OK)
          "circ2":{"xC":1,"yC":2,"sens":4}                                # centre et sens 
          }

    def __init__(self,parent=None, **kwargs):
        if parent==None:
            parent = tk.Toplevel()
            # parent.overrideredirect(True) widget indeplacable
            # prevent close window:
            # parent.protocol("WM_DELETE_WINDOW", lambda:None)
            self.parent = parent
        parent.geometry("800x200")
        self.frameB = tk.Frame(parent)
        self.frame = tk.Frame(parent)
        self.frameB.pack()
        self.frame.pack()
        bdel = tk.Button(self.frameB,text="Delete selected lines",command=self.delSelectLines)
        badd = tk.Button(self.frameB,text="Add a line",command=self.addLine)
        bSAll = tk.Button(self.frameB,text="Select all",command=self.selectAll)
        bSNone = tk.Button(self.frameB,text="Select none",command=self.deselectAll)
        bSave = tk.Button(self.frameB,text="Save/show",command=self.go)
        bLoad = tk.Button(self.frameB,text="Load",command=self.loadFile)
        bdel.grid(row=0,column=0)
        badd.grid(row=0,column=1)
        bSAll.grid(row=0,column=2)
        bSNone.grid(row=0,column=3)
        bSave.grid(row=1,column=1)
        bLoad.grid(row=1,column=2)
        self.topDraw = 0
        if True:
            self.addLine("line 100 100 1 5 1")
        if True:
            xc,yc=100,200
            xf,yf=100+100*cos(0.45),200+100*sin(0.45)
            self.addLine(f"arc2 {xf} {yf} {xc} {yc} 1  8 0") # xf yf xc yc sens speed plasma
        if True:
            self.addLine("arc1 200 100 150 180  0") # xf yf xp yp sens speed plasma
        if True:
            self.addLine("ezsqx 300 320 5 23 0") # xf yf nzigzag speed plasma
        if True:
            self.addLine("ezsqy 400 400 9 2 0") # xf yf nzigzag speed plasma
    # FIN def __init__(self,master=None, **kwargs):
    # ################################################################################

    def proccessTraj(self):
        """
        draw the trajectory OR write a file OR do it directly
        section : a string="type finalX finalY finale par_1 ... par_n speed plasma"
        """
        # print(f"Proccessing {self.trajDescript}")
        c,r = self.frame.size()
        if self.topDraw!=0:
            self.topDraw.destroy()
        self.topDraw = tk.Toplevel(width=410,height=510)
        self.topDraw.title("TRAJECTORY")
        btn = ttk.Button(self.topDraw,text="save to file",command=self.saveToFile)
        btn.place(x=self.topDraw.winfo_width()/2,y=20)
        self.canvas = tk.Canvas(self.topDraw,width=400,height=500,bg='ivory')
        self.canvas.place(x=5,y=55)

        e = 2
        xcur = 0
        ycur = 0
        for section in self.trajDescript:
            # param common to all type of section
            x0 = xcur # debut de la section
            y0 = ycur # debut de la section
            print(section)
            localDico =dict()
            for ss in section.split():
                k,v=ss.split("=")
                localDico[k]=v
            type = localDico["type"]
            speed = localDico["speed"]
            plasma = localDico["plasma"]
            color = 'red' if plasma=="1" else 'green'
            w = int(speed)//10+1
            if type=='line':
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                zF = float(localDico["zF"])
                self.canvas.create_line(xcur+e,ycur+e,xF+e,yF+e, fill=color, width=2)
                xcur = xF
                ycur = yF
            elif type=="ezsqx":
                # first: a straight line         _
                # second: n              times _| |
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                n = int(localDico["nZigZag"])
                LX = xF-xcur
                LY = yF-ycur
                L = LY
                l = LX/(2.0*n) if n!=0 else L
                self.canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+L+e, fill=color, width=w)
                ycur += L
                if n==0:
                    self.canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur+l,ycur)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur-L)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+e,ycur-L+e, fill=color, width=w)
                    ycur -= L
                    # (xcur,ycur)->(xcur+l,ycur)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur+L)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+L+e, fill=color, width=w)
                    ycur += L
            elif type=="ezsqy":
                # first: a straight line         _
                # second: n          
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                n = int(localDico["nZigZag"])
                LX = xF-xcur
                LY = yF-ycur
                L = LX
                l = LY/(2.0*n) if n!=0 else L
                self.canvas.create_line(xcur+L+e,ycur+e,xcur+e,ycur+e, fill=color, width=w)
                xcur += L
                if n==0:
                    self.canvas.create_line(xcur+e,ycur+l+e,xcur+e,ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur,ycur+l)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+l+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur-L,ycur)
                    self.canvas.create_line(xcur+e,ycur+e,xcur-L+e,ycur+e, fill=color, width=w)
                    xcur -= L
                    # (xcur,ycur)->(xcur,ycur+l)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+l+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur+L,ycur)
                    self.canvas.create_line(xcur+e,ycur+e,xcur+L+e,ycur+e, fill=color, width=w)
                    xcur += L
            elif type=="arc1": # pt final et pt passage
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xp = float(localDico["xP"]) # point de passage
                yp = float(localDico["yP"]) # point de passage
                status,a,b,c,d,start,extent = create_arcParameter(xd,yd,xF,yF,xp,yp)
                self.canvas.create_arc(a,b,c,d,start=start,extent=extent,style=tk.ARC,outline=color,width=w)
                if status!='ok':
                    messagebox.showinfo("information",status)
                xcur = xF
                ycur = yF
            elif type=="arc2": # pt final, centre et sens
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xF = float(localDico["xF"])
                yF = float(localDico["yF"])
                xc = float(localDico["xC"]) # x center
                yc = float(localDico["yC"]) # y center
                sens = int(localDico["sens"]) # sens
                # print(f"xc,yc,sens={xc,yc,sens}") # bidon
                R2 = (xd-xc)**2 + (yd-yc)**2 # rayon calule avec point courant
                R2a = (xF-xc)**2 + (yF-yc)**2 # rayon calule avec point cible
                if abs(R2-R2a)>0.1: # les rayons sont de l'ordre de 10 a 100 
                    messagebox.showerror("Error",f"Inconsistent data for arc2 {R2,R2a}")
                    return
                R = sqrt(R2)
                AdR = atan2(yd-yc,xd-xc) # angle polaire debut
                AfR = atan2(yF-yc,xF-xc) # angle polaire fin
                if AdR<0:AdR += 2*pi
                if AfR<0:AfR += 2*pi
                ad = AdR*180/pi
                af = AfR*180/pi
                extent = (ad-af) if sens>0 else (ad-af)-360
                # print(f"self.canvas.create_arc({xc-R,yc-R,xc+R,yc+R},start={-ad},extent={extent},style={tk.ARC})") bidon
                self.canvas.create_arc(xc-R,yc-R,xc+R,yc+R,start=-ad,extent=extent,style=tk.ARC,outline=color,width=w)
                # if status!='ok':                    messagebox.showinfo("information",status)
                xcur = xF
                ycur = yF
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
            if not self.frame.grid_slaves(row=l,column=c-1)[0].get():
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
                if val==True:val="1"
                if val==False: val="0"
                parameters += key+"="+val+" "
            self.trajDescript.append(parameters)
        self.proccessTraj()
    # FIN def go(self):
    # ################################################################################
            
    def delSelectLines(self):
        c,r = self.frame.grid_size()
        print(f"entering delSelectLines,c,r={c,r}")
        while True:
            somethingDone = False
            c,r = self.frame.grid_size()
            for i in range(r):
                doIt = self.frame.grid_slaves(row=i,column=11)[0].get()
                if not doIt: # selectelines
                    continue
                self.delLine(i)
                somethingDone = True
                break
            if not somethingDone:
                break
    # FIN def delSelectLines(self):
    # ################################################################################

    def delLine(self,line):
        """
        delete the line of the gris therefore the number of line is decremented by one
        """
        c,r = self.frame.grid_size()
        # print(f"entering delLine c,r,line={c,r,line}")
        if line<0 or line>= r :
            return
        # delete line
        for icol in range(c):
            self.frame.grid_slaves(row=line,column=icol)[0].destroy()
        for irow in range(line+1,r):
            for icol in range(c):
                w =  self.frame.grid_slaves(row=irow,column=icol)[0]
                w.grid(row=irow-1,column=icol)
        self.renumber()
        # print(f"leaving delLine c,r={self.frame.grid_size()}")
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
            self.frame.grid_slaves(row=i,column=11)[0].set(True)
    # FIN def selectAll(self):
    # ################################################################################

    def comboboxSelect(self,event,r):
        """
        called by the combobox of row=r and column=0 
        """
        c,r1=self.frame.grid_size()
        print("entering comboSelect c=",c," r=",r)
        print(f"{self.frame.grid_slaves(row=r,column=0)}")
        w = self.frame.grid_slaves(row=r,column=0)[0]
        newType = w.get()
        # reset common for all type
        for k in range(1,9):
            self.frame.grid_slaves(row=r,column=k)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=k)[0].config(state="disabled")
        self.frame.grid_slaves(row=r,column=9)[0].config(state="selected") # plasma checkbutton
        # specific reset for different type
        self.frame.grid_slaves(row=r,column=8)[0].config(state="normal")
        self.frame.grid_slaves(row=r,column=8)[0].delete(0,tk.END)
        self.frame.grid_slaves(row=r,column=8)[0].insert(0,"Speed")
        if newType=="line":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=r,column=3)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=3)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=3)[0].insert(0,"Zend")
        elif newType=="ezsqx" or newType=="ezsqy":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,"Nzigzag")
        elif newType=="arc1" :
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal") # xFin
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal") # yFin
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal") # xPassage
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,"xPass")
            self.frame.grid_slaves(row=r,column=5)[0].config(state="normal") # yPassage
            self.frame.grid_slaves(row=r,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=5)[0].insert(0,"yPass")
        elif newType=="arc2":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal") # xFin
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal") # yFin
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal") # xCenter
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,"xCenter")
            self.frame.grid_slaves(row=r,column=5)[0].config(state="normal") # yCenter
            self.frame.grid_slaves(row=r,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=5)[0].insert(0,"yCenter")
            self.frame.grid_slaves(row=r,column=6)[0].config(state="normal") # sens
            self.frame.grid_slaves(row=r,column=6)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=6)[0].insert(0,"Sens")
        elif newType=="circ1":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal") # xPassage1
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"xPas1")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal") # yPassage1
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"yPas1")
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal") # xPassage2
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,"xPas2")
            self.frame.grid_slaves(row=r,column=5)[0].config(state="normal") # yPassage2
            self.frame.grid_slaves(row=r,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,"yPas2")
        elif newType=="circ2":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal") # xCenter
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"xCenter")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal") # yCenter
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"yCenter")
        else:
            messagebox.showinfo("Show info","Not yet implemented")
    # FIN def comboboxSelect(self,event,r):
    # ################################################################################

    def insertLineBelow(self,line,tl):
        """
        insert an empty line after line k, 0<=k<r
        """
        c,r = self.frame.grid_size()
        if line<0 or line>=r:
            tl.destroy()
            return
        print(f"duplique decale vers le bas les lignes {line} .. derniere ")
        c,r = self.frame.size()
        self.addLine()
        if line==r-1:
            tl.destroy()
            return           
        # duplication des combobox de choix de type column=0
        for irow in range(r-1,line,-1):
            print(f"irow={irow}")
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            print(f"type={type}")
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
        tl.destroy()
        self.renumber()
        return
        # FIN def insertLineBelow(self,line,tl):
    # ################################################################################

    def insertLineAbove(self,line,tl):
        """
        insert an empty line after line, 0<=k<r moving 
        """
        c,r = self.frame.grid_size()
        if line<0 or line>=r:
            tl.destroy()
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
        tl.destroy()
        self.renumber()
        return
        # FIN def insertLineAbove(self,line,tl):
    # ################################################################################
    
    def removeLine(self,line,tl):
        print(f"entering removeLine with {line} {tl}")
        for icol in range(11):
            self.frame.grid_slaves(row=line,column=icol)[0].grid_remove()
        tl.destroy()
        self.renumber()
    # FIN def removeLine(self,line,tl)
    # ################################################################################
    
    def copyLine(self,line,tl):
        messagebox.showinfo("","copyLine not yet implemented")
        tl.destroy()
        self.renumber()
    # FIN def cpoyLine(self,line,tl)
    # ################################################################################
        
    def pasteLine(self,line,tl):
        messagebox.showinfo("","pasteLine not yet implemented")
        tl.destroy()
        self.renumber()
    # FIN def copyLine(self,line,tl)
    # ################################################################################

    def addLine(self,line=""):
        def close(event = ""):
            # print(f"je ferme {event}")
            return
        def editLine(event,line):
            print("entering editLine ",line)
            tl = tk.Toplevel()
            tl.title("Edit")
            tl.protocol("WM_DELETE_WINDOW",close )
            tl.bind("<Destroy>", close)
            # while this toplevel is living NO other action is possible :
            tl.focus_force()
            tl.wait_visibility()
            tl.grab_set()
            lab = tk.Label(tl,text="Line %d"%(line+1),width=17)
            butInsBel = tk.Button(tl,text="Insert line below",width=17,command=lambda :self.insertLineBelow(line,tl))
            butInsAbo = tk.Button(tl,text="Insert line above",width=17,command=lambda :self.insertLineAbove(line,tl))
            butDel = tk.Button(tl,text="Delete line",width=17,command=lambda :self.removeLine(line,tl))
            butCop = tk.Button(tl,text="Copy line",width=17,command=lambda :self.copyLine(line,tl))
            butPas = tk.Button(tl,text="Paste line",width=17,command=lambda :self.pasteLine(line,tl))
            butCancel = tk.Button(tl,text="Cancel",width=17,command= lambda: tl.destroy())
            lab.grid(column=0,row=0)
            butInsAbo.grid(column=0,row=1)
            butInsBel.grid(column=0,row=2)
            butDel.grid(column=0,row=3)
            butCop.grid(column=0,row=4)
            butPas.grid(column=0,row=5)
            butCancel.grid(column=0,row=6)
        # FIN def editLine(event):
        # #############################################################
        
        c,r = self.frame.grid_size()
        w = ttk.Combobox(self.frame,values=self.types,width=self.widthCell,state="readonly")
        w.bind("<<ComboboxSelected>>", lambda  event : self.comboboxSelect(event,r))
        w.grid(row=r,column=0) # choix de prochain section
        for k in range(1,9):
            w = ttk.Entry(self.frame,width=self.widthCell)
            w.config(state="disabled")
            w.grid(row=r,column=k) # position finale du premier section
        w = jcCheckbutton(self.frame,text="Plasma",width=self.widthCell)
        w.set(False);
        w.grid(row=r,column=9) # plasma
        w = tk.Label(self.frame,text="%d"%(r+1),borderwidth=0.5,width=2,relief="solid",bg="white")
        w.grid(row=r,column=10) # label
        w.bind('<Button-1>', lambda event : editLine(event,r))
        w.bind("<Enter>", lambda event : event.widget.config(bg="red"))
        w.bind("<Leave>", lambda event : event.widget.config(bg="white"))
        w = jcCheckbutton(self.frame,width=self.widthCell)
        w.set(True);
        w.grid(row=r,column=11) # selecteur        
        if line=="":
            return

        # here we add the line line given as arguments
        ls = line.split()
        type = ls[0]
        if type not in self.implementedTypes:
            messagebox.showinfo(type+" not yet implemented")
            return
        # here a correct type is to be used
        w = self.frame.grid_slaves(row=r,column=0)[0]
        w.set(type)
        print(type)
        w = self.frame.grid_slaves(row=r,column=1)[0]
        w.config(state="normal")
        w.insert(0,ls[1]) #Xfin
        w = self.frame.grid_slaves(row=r,column=2)[0]
        w.config(state="normal")
        w.insert(0,ls[2]) #Yfin
        if type=="line":
            w = self.frame.grid_slaves(row=r,column=3)[0]
            w.config(state="normal")
            w.insert(0,ls[3]) #Zfin
            w = self.frame.grid_slaves(row=r,column=8)[0] # speed
            w.config(state="normal")
            w.insert(0,ls[4])
        elif type=="arc1":
            w = self.frame.grid_slaves(row=r,column=4)[0] # xPassage
            w.config(state="normal")
            w.insert(0,ls[3])
            w = self.frame.grid_slaves(row=r,column=5)[0] # yPassage
            w.config(state="normal")
            w.insert(0,ls[4])
            w = self.frame.grid_slaves(row=r,column=8)[0] # speed
            w.config(state="normal")
            w.insert(0,ls[3])
        elif type=="arc2":
            w = self.frame.grid_slaves(row=r,column=4)[0] # xCenter
            w.config(state="normal")
            w.insert(0,ls[3])
            w = self.frame.grid_slaves(row=r,column=5)[0] # yCenter
            w.config(state="normal")
            w.insert(0,ls[4])
            w = self.frame.grid_slaves(row=r,column=6)[0] # sens
            w.config(state="normal")
            w.insert(0,ls[5])
            w = self.frame.grid_slaves(row=r,column=8)[0] # speed
            w.config(state="normal")
            w.insert(0,ls[6])
        elif type =="ezsqx" or type =="ezsqy":
            w = self.frame.grid_slaves(row=r,column=4)[0] # n zigzag
            w.config(state="normal")
            w.insert(0,ls[3])
            w = self.frame.grid_slaves(row=r,column=8)[0] # n speed
            w.config(state="normal")
            w.insert(0,ls[4])

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
        for i in range(r):
            self.frame.grid_slaves(row=i,column=10)[0]["text"] = "%d"%(i+1)
    # FIN def renumber(self):
    # ################################################################################
    
    def loadFile(self):
        """
        copy line l0 into line l1 which is therefore lost
        """
        c,r = self.frame.grid_size()
        print(f"entering loadFile c,r={c,r}")
        fileName = filedialog.askopenfilename()
        try :
            lines = open(fileName).readlines()
            ok = True
        except:
            message.error("Could not open the file {fileName} for reading")
            ok = False
        if not ok:
            return
        # update the gui
        self.selectAll()
        self.delSelectLines()
        for line in lines:
            print(line)
            self.addLine(line)
            
    # FIN def loadFile(self)
    # ################################################################################        
    
    def saveToFile(self):
        """
        Save with the format imposed by plasmagui
        """
        enTete = """Numero d'article;XYZ;;;;;;;;;;;;
Numero de serie;789;;;;;;;;;;;;
;;;;;;;;;;;;;
;;;;;;;;;;;;;
Puissance Plasma (W);1000;;;;;;;;;;;;
Debit Plasma (l/mn);40;;;;;;;;;;;;
;;;;;;;;;;;;;
Description trajectoire;;L;EZSQX;EZSQY;A1;A2;C1;C2;W;START;END;;
Numero d'operation;type;distance;angle;;;;;vitesse;temps (x 1/10 s);0 ou 1;0 ou 1;0 ou 1;0 ou 1
"""
        c,r = self.frame.grid_size()
        print(f"entering saveToFile c,r={c,r}")
        fileName = filedialog.asksaveasfilename()
        if fileName=='':
            return # since "cancel" has been used
        try:
            f = open(fileName,"w")
            ok = True
        except:
            message.error("Could not open the file {fileName} for writing")
            ok = False
        if not ok:
            return
        # f.writelines(enTete)
        for irow in range(r):
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            xF = self.frame.grid_slaves(row=irow,column=1)[0].get()+" "
            yF = self.frame.grid_slaves(row=irow,column=2)[0].get()+" "
            speed = self.frame.grid_slaves(row=irow,column=8)[0].get()+" "
            plasma = self.frame.grid_slaves(row=1,column=9)[0].get()
            plasma = str(int(plasma))
            if type == 'line':
                zF = self.frame.grid_slaves(row=irow,column=3)[0].get() + " "
                line = type + " " + xF + yF + zF + speed + plasma
            elif type == 'ezsqx' or type == 'ezsqy':
                nZigZag = self.frame.grid_slaves(row=irow,column=4)[0].get() + " "
                line = type + " " + xF + yF + nZigZag + speed + plasma
            elif type == 'arc1':
                xP = self.frame.grid_slaves(row=irow,column=4)[0].get() + " "
                yP = self.frame.grid_slaves(row=irow,column=5)[0].get() + " "
                line = type + " " + xP + yP + speed + plasma
            elif type == 'circ1':
                xP1 = self.frame.grid_slaves(row=irow,column=1)[0].get() + " "
                yP1 = self.frame.grid_slaves(row=irow,column=2)[0].get() + " "
                xP2 = self.frame.grid_slaves(row=irow,column=4)[0].get() + " "
                yP2 = self.frame.grid_slaves(row=irow,column=5)[0].get() + " "
                line = type + " " + xP1 + yP1 + xP2 + yP2 +speed + plasma
            elif type == 'arc2':
                xC = self.frame.grid_slaves(row=irow,column=4)[0].get() + " "
                yC = self.frame.grid_slaves(row=irow,column=5)[0].get() + " "
                sens = self.frame.grid_slaves(row=irow,column=6)[0].get() + " "
                line = type + " " + xF + yF + xC + yC + sens +speed + plasma
            elif type == 'circ2':
                xC = self.frame.grid_slaves(row=irow,column=1)[0].get() + " "
                yC = self.frame.grid_slaves(row=irow,column=2)[0].get() + " "
                sens = self.frame.grid_slaves(row=irow,column=4)[0].get() + " "
                line = type + " " + xC + yC + sens +speed + plasma
            print(line)
            f.writelines(line+'\n')
        f.close()
    # FIN def loadFile(self)
    # ################################################################################        

    """
    Mes conventions
    """
if __name__=='__main__':
    root = tk.Tk()
    root.title("ROOT")
    root.geometry("600x300")
    v = tk.Scrollbar()
    v.pack(side = tk.LEFT, fill = tk.Y)  
    my=trajMaker(root)
    fr = my.frame
    # root.mainloop()


