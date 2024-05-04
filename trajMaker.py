import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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

######################################################################################
#                                CLASS MATRIX                                        #
######################################################################################
def rien():
    pass
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

    11 columns:
        0      1    ...   8        9     10
    combobbox entry ... entry  checkbox label
    """
    types = ["line","ezsqx","ezsqy","arc1","arc2","circ1","circ2","start","end","w"]
    implementedTypes = ["line","ezsqx","ezsqy","arc1","arc2"]
    widthCell = 6
    def __init__(self,parent=None, **kwargs):
        if parent==None:
            parent = tk.Toplevel()
            # parent.overrideredirect(True) widget indeplacable
            # prevent close window:
            # parent.protocol("WM_DELETE_WINDOW", lambda:None)
            self.parent = parent
        self.frameB = tk.Frame(parent)
        self.frame = tk.Frame(parent)
        self.frameB.pack()
        self.frame.pack()
        bdel = tk.Button(self.frameB,text="Delete last line",command=self.delLastLine)
        badd = tk.Button(self.frameB,text="Add a line",command=self.addLine)
        bOK = tk.Button(self.frameB,text="Ok",command=self.go)
        bdel.pack(side='left')
        badd.pack(side='left')
        bOK.pack(side='left')
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
        self.canvas = tk.Canvas(self.topDraw,width=400,height=500,bg='ivory')
        self.canvas.place(x=5,y=5)

        e = 2
        xcur = 0
        ycur = 0
        for section in self.trajDescript:
            # param common to all type of section
            x0 = xcur # debut de la section
            y0 = ycur # debut de la section
            ts = section.split()
            type = ts[0]
            xf = float(ts[1])
            yf = float(ts[2])
            speed = float(ts[-2])
            plasma = ts[-1]
            color = 'red' if plasma=="True" else 'green'
            w = int(speed)//10+1
            print(f"dans proccessTraj section={section}, plasma={plasma}, color={color} w={w}")
            if type=='line':
                self.canvas.create_line(xcur+e,ycur+e,xf+e,yf+e, fill=color, width=2)
                xcur = xf
                ycur = yf
            elif type=="ezsqx":
                # first: a straight line         _
                # second: n              times _| |
                n = int(ts[4])
                LX = xf-xcur
                LY = yf-ycur
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
                n = int(ts[4])
                LX = xf-xcur
                LY = yf-ycur
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
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xp = float(ts[4]) # point de passage
                yp = float(ts[5]) # point de passage
                status,a,b,c,d,start,extent = create_arcParameter(xd,yd,xf,yf,xp,yp)
                self.canvas.create_arc(a,b,c,d,start=start,extent=extent,style=tk.ARC,outline=color,width=w)
                if status!='ok':
                    messagebox.showinfo("information",status)
                xcur = xf
                ycur = yf
            elif type=="arc2": # pt final, centre et sens
                print(f"{ts}")
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xc = float(ts[4]) # x center
                yc = float(ts[5]) # y center
                sens = int(ts[7])
                # print(f"xc,yc,sens={xc,yc,sens}") # bidon
                R2 = (xd-xc)**2 + (yd-yc)**2 # rayon calule avec point courant
                R2a = (xf-xc)**2 + (yf-yc)**2 # rayon calule avec point cible
                if abs(R2-R2a)>0.1: # les rayons sont de l'ordre de 10 a 100 
                    messagebox.showerror("Error",f"Inconsistent data for arc2 {R2,R2a}")
                    return
                R = sqrt(R2)
                AdR = atan2(yd-yc,xd-xc) # angle polaire debut
                AfR = atan2(yf-yc,xf-xc) # angle polaire fin
                if AdR<0:AdR += 2*pi
                if AfR<0:AfR += 2*pi
                ad = AdR*180/pi
                af = AfR*180/pi
                extent = (ad-af) if sens>0 else (ad-af)-360
                # print(f"self.canvas.create_arc({xc-R,yc-R,xc+R,yc+R},start={-ad},extent={extent},style={tk.ARC})") bidon
                self.canvas.create_arc(xc-R,yc-R,xc+R,yc+R,start=-ad,extent=extent,style=tk.ARC,outline=color,width=w)
                # if status!='ok':                    messagebox.showinfo("information",status)
                xcur = xf
                ycur = yf
            else:
                messagebox.showinfo("information",f"processTraj: {type} not yet implemented")
            if (xcur-xf)**2 + (ycur-yf)**2 >1e-5:
                messagebox.showinfo("Erreur Grave",f"Pt final {xcur,ycur} loin de celui demande={xf,yf}")
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
            # print("dans go ",l) # bidon
            w = self.frame.grid_slaves(row=l,column=0)[0]
            type = w.get()
            if type =="":
                continue
            if not type in self.implementedTypes:
                messagebox.showinfo("information","one of the types is not implemented")
                return  # since the type is not yet implemented (TODO)
            # here a type implemented
            ok = True
            try:
                XFin = float(self.frame.grid_slaves(row=l,column=1)[0].get())
                YFin = float(self.frame.grid_slaves(row=l,column=2)[0].get())
                S = float(self.frame.grid_slaves(row=l,column=8)[0].get()) # speed
                P = "selected" in self.frame.grid_slaves(row=l,column=9)[0].state() # plasma
            except:
                messagebox.showinfo("Information",f"Syntax error on at least one field on line {l+1} (common parameters)")
                ok = False
            if not ok:
                return
            # here a type implemented and syntax ok            
            ZFin = 0
            if type == "line":
                # no extra parameter
                section = f"{type} {XFin} {YFin} {ZFin} {S} {P}"
                self.trajDescript.append(section)
            elif type=="ezsqx" or type=="ezsqy":
                # extraparameter = number of zigzag
                ok=True
                try:
                    N = int(self.frame.grid_slaves(row=l,column=4)[0].get())
                except:
                    ok=False
                if not ok:
                    messagebox.showinfo("Information",f"Syntax error on at least one field on line {l+1} (ezsqx/y parameter)")
                    return
                section = f"{type} {XFin} {YFin} {ZFin} {N} {S} {P}"
                self.trajDescript.append(section)
            elif type=="arc1":
                XP = float(self.frame.grid_slaves(row=l,column=4)[0].get()) # X passage
                YP = float(self.frame.grid_slaves(row=l,column=5)[0].get()) # Y passage
                ZP = 0
                section=f"{type} {XFin} {YFin} {ZFin} {XP} {YP} {ZP} {S} {P}"
                self.trajDescript.append(section)
            elif type=="arc2":
                XC = float(self.frame.grid_slaves(row=l,column=4)[0].get()) # X center
                YC = float(self.frame.grid_slaves(row=l,column=5)[0].get()) # Y center
                ZC = 0
                sens = int(self.frame.grid_slaves(row=l,column=6)[0].get()) # sens
                section=f"{type} {XFin} {YFin} {ZFin} {XC} {YC} {ZC} {sens} {S} {P}"
                # print(f"dans go et arc2 on append {section}") # bidon
                self.trajDescript.append(section)
            else:
                messagebox.showinfo("Information","unexpected type")
        self.proccessTraj()
        # FIN def go(self):
    # ################################################################################
            
    def delLastLine(self):
        c,r = self.frame.grid_size()
        if r==1:
            return
        # delete line r-1
        for k in range(c):
            w = self.frame.grid_slaves(row=r-1, column=k)[0]
            w.grid_remove()
    # FIN def delLastLine(self):
    # ################################################################################

    def delLine(self,line):
        c,r = self.frame.grid_size()
        if r==1:
            return
        if line<0 or line >= r :
            pass
        # delete line r-1
        for k in range(c):
            w = self.frame.grid_slaves(row=line, column=k)[0]
            w.grid_remove()
    # FIN def delLastLine(self):
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
        elif newType=="arc1" or newType=="arc2":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,"Xend")
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,"Yend")
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            msg = "Xpass" if newType=="arc1" else "Xcenter"
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,msg)
            msg = "Ypass" if newType=="arc1" else "Ycenter"
            self.frame.grid_slaves(row=r,column=5)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=5)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r,column=5)[0].insert(0,msg)
            if newType=='arc2':
                self.frame.grid_slaves(row=r,column=6)[0].config(state="normal")
                self.frame.grid_slaves(row=r,column=6)[0].delete(0,tk.END)
                self.frame.grid_slaves(row=r,column=6)[0].insert(0,"Sens")
        elif newType=="circ1" or newType=="circ2":
            self.frame.grid_slaves(row=r,column=1)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=1)[0].delete(0,tk.END)
            msg = "Xpass1" if newType=="circ1" else "Xcenter"
            self.frame.grid_slaves(row=r,column=1)[0].insert(0,msg)
            self.frame.grid_slaves(row=r,column=2)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=2)[0].delete(0,tk.END)
            msg = "Ypass1" if newType=="circ1" else "Ycenter"
            self.frame.grid_slaves(row=r,column=2)[0].insert(0,msg)
            self.frame.grid_slaves(row=r,column=4)[0].config(state="normal")
            self.frame.grid_slaves(row=r,column=4)[0].delete(0,tk.END)
            msg = "Xpass2" if newType=="circ1" else "Sens"
            self.frame.grid_slaves(row=r,column=4)[0].insert(0,msg)
            if  newType=="circ1":
                self.frame.grid_slaves(row=r,column=5)[0].config(state="normal")
                self.frame.grid_slaves(row=r,column=5)[0].delete(0,tk.END)
                self.frame.grid_slaves(row=r,column=5)[0].insert(0,"Ypass2")
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
        return
        # FIN def insertLineBelow(self,line,tl):
    # ################################################################################

    def insertLineAbove(self,line,tl):
        """
        insert an empty line after line k, 0<=k<r
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
        return
        # FIN def insertLineAbove(self,line,tl):
    # ################################################################################
    
    def removeLine(self,line,tl):
        print(f"entering removeLine with {line} {tl}")
        for icol in range(11):
            self.frame.grid_slaves(row=line,column=icol)[0].grid_remove()
        tl.destroy()
    # FIN def removeLine(self,line,tl)
    # ################################################################################
    
    def copyLine(self,line,tl):
        messagebox.showinfo("","copyLine not yet implemented")
        tl.destroy()
    # FIN def cpoyLine(self,line,tl)
    # ################################################################################
        
    def pasteLine(self,line,tl):
        messagebox.showinfo("","pasteLine not yet implemented")
        tl.destroy()
    # FIN def cpoyLine(self,line,tl)
    # ################################################################################

    def addLine(self,line=""):
        def editLine(event,line):
            print("entering editLine ",line)
            tl = tk.Toplevel()
            tl.title("Edit")
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
        w = ttk.Checkbutton(self.frame,text="Plasma",width=self.widthCell)
        w.config(state="selected")
        w.grid(row=r,column=9) # plasma
        w = tk.Label(self.frame,text="%d"%(r+1),borderwidth=0.5,width=2,relief="solid",bg="white")
        w.grid(row=r,column=10)
        w.bind('<Button-1>', lambda event : editLine(event,r))
        w.bind("<Enter>", lambda event : event.widget.config(bg="red"))
        w.bind("<Leave>", lambda event : event.widget.config(bg="white"))
        if line=="":
            return

        # here we add the line line
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




def creop(fr,k):
    c,r = fr.grid_size()
    for ic in range(c):
        w = fr.grid_slaves(row=k,column=ic)[0]
        w.grid(row=k+1,column=ic)





    
if __name__=='__main__':
    root = tk.Tk()
    root.title("ROOT")
    root.geometry("600x300")
    v = tk.Scrollbar()
    v.pack(side = tk.LEFT, fill = tk.Y)  
    my=trajMaker(root)
    fr = my.frame
    # root.mainloop()
