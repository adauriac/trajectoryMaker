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
    print(f"ds create_p xc,yc,R={xc,yc,R}")
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
    print(f"ds sub en rd Ad,Af,Ap={Ad,Af,Ap}")
    print(f"ds sub en dg ad,af,ap={ad,af,ap}")
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
    print(f"ok,{xc-R},{yc-R},{xc+R},{yc+R},{ad},{extent}")
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
    implementedTypes = ["line","ezsqx","ezsqy","arc1"]
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
        bBidon = tk.Button(self.frameB,text="pour tester",command=self.test)
        bdel.pack(side='left')
        badd.pack(side='left')
        bOK.pack(side='left')
        bBidon.pack(side='left')
        self.topDraw = 0
        self.addLine("line 100 100 1 0")
        self.addLine("arc1 200 200 150 180 1 0")
        self.addLine("ezsqx 300 320 5  1 0")
    # FIN def __init__(self,master=None, **kwargs):
    # ################################################################################

    def test(self,k=3):
        print("duplique les k derniere lignes ")
        c,r = self.frame.size()
        self.addLine()
        # duplication des combobox de choix de type column=0
        for irow in range(r-1,r-1-k,-1):
            type = self.frame.grid_slaves(row=irow,column=0)[0].get()
            self.frame.grid_slaves(row=irow+1,column=0)[0].set(type)
        self.frame.grid_slaves(row=r-k,column=0)[0].set("")
        # duplications des parametres de col 1 a col 9
        for icol in range(1,9):
            for irow in range(r-1,r-1-k,-1):
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
            self.frame.grid_slaves(row=r-k,column=icol)[0].delete(0,tk.END)
            self.frame.grid_slaves(row=r-k,column=icol)[0].insert(0,"")
        return
        cur=[]
        for i in range(9):
            cur.append(self.frame.grid_slaves(row=r-1,column=i)[0].get())
            self.frame.grid_slaves(row=r-1,column=i)[0].delete(0,tk.END)
            if i!=0: # le combobox de type
                self.frame.grid_slaves(row=r-1,column=i)[0].config(state="disabled")
            else:
                self.frame.grid_slaves(row=r-1,column=i)[0].set("")
        cur.append('selected' in (my.frame.grid_slaves(row=1,column=9)[0].state()))
        print(f"type={cur}")
        
        w = ttk.Combobox(self.frame,values=self.types,width=self.widthCell,state="readonly")
        w.bind("<<ComboboxSelected>>", lambda  event : self.comboboxSelect(event,r))
        w.set(cur[0])
        w.grid(row=r,column=0) # le type
        for i in range(1,9): # les 8 ttk.Entry
            if cur[i] == '':
                continue
            entry = ttk.Entry(self.frame,width=self.widthCell)
            entry.insert(0, cur[i])   # Insère la nouvelle valeur dans l'Entry
            entry.grid(row=r,column=i) # le type
    # FIN     def test(self):
    # ################################################################################

    def testOK(self):
        print("duplique la dernier ligne")
        c,r = self.frame.size()
        self.addLine()
        cur=[]
        for i in range(9):
            cur.append(self.frame.grid_slaves(row=r-1,column=i)[0].get())
            self.frame.grid_slaves(row=r-1,column=i)[0].delete(0,tk.END)
            if i!=0: # le combobox de type
                self.frame.grid_slaves(row=r-1,column=i)[0].config(state="disabled")
            else:
                self.frame.grid_slaves(row=r-1,column=i)[0].set("")
        cur.append('selected' in (my.frame.grid_slaves(row=1,column=9)[0].state()))
        print(f"type={cur}")
        #
        w = ttk.Combobox(self.frame,values=self.types,width=self.widthCell,state="readonly")
        w.bind("<<ComboboxSelected>>", lambda  event : self.comboboxSelect(event,r))
        w.set(cur[0])
        w.grid(row=r,column=0) # le type
        for i in range(1,9): # les 8 ttk.Entry
            if cur[i] == '':
                continue
            entry = ttk.Entry(self.frame,width=self.widthCell)
            entry.insert(0, cur[i])   # Insère la nouvelle valeur dans l'Entry
            entry.grid(row=r,column=i) # le type
    # FIN     def testOK(self):
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
        canvas = tk.Canvas(self.topDraw,width=400,height=500,bg='ivory')
        canvas.place(x=5,y=5)

        e = 2
        xcur = 0
        ycur = 0
        for section in self.trajDescript:
            # param common to all type of section
            x0 = xcur # debut de la section
            y0 = ycur # debut de la section
            ts = section.split()
            type = ts[0]
            xf = int(ts[1])
            yf = int(ts[2])
            speed = ts[-2]
            plasma = ts[-1]
            color = 'red' if plasma=="1" else 'green'
            w = 1 
            if type=='line':
                canvas.create_line(xcur+e,ycur+e,xf+e,yf+e, fill=color, width=2)
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
                canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+L+e, fill=color, width=w)
                ycur += L
                if n==0:
                    canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur+l,ycur)
                    canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur-L)
                    canvas.create_line(xcur+e,ycur+e,xcur+e,ycur-L+e, fill=color, width=w)
                    ycur -= L
                    # (xcur,ycur)->(xcur+l,ycur)
                    canvas.create_line(xcur+e,ycur+e,xcur+l+e,ycur+e, fill=color, width=w)
                    xcur += l
                    # (xcur,ycur)->(xcur,ycur+L)
                    canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+L+e, fill=color, width=w)
                    ycur += L
            elif type=="ezsqy":
                # first: a straight line         _
                # second: n          
                n = int(ts[4])
                LX = xf-xcur
                LY = yf-ycur
                L = LX
                l = LY/(2.0*n) if n!=0 else L
                canvas.create_line(xcur+L+e,ycur+e,xcur+e,ycur+e, fill=color, width=w)
                xcur += L
                if n==0:
                    canvas.create_line(xcur+e,ycur+l+e,xcur+e,ycur+e, fill=color, width=w)
                    xcur += l
                    continue
                for i in range(n):
                    # (xcur,ycur)->(xcur,ycur+l)
                    canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+l+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur-L,ycur)
                    canvas.create_line(xcur+e,ycur+e,xcur-L+e,ycur+e, fill=color, width=w)
                    xcur -= L
                    # (xcur,ycur)->(xcur,ycur+l)
                    canvas.create_line(xcur+e,ycur+e,xcur+e,ycur+l+e, fill=color, width=w)
                    ycur += l
                    # (xcur,ycur)->(xcur+L,ycur)
                    canvas.create_line(xcur+e,ycur+e,xcur+L+e,ycur+e, fill=color, width=w)
                    xcur += L
            elif type=="arc1":
                xd = xcur # debut de la trajectoire
                yd = ycur # debut de la trajectoire
                xp = int(ts[4]) # point de passage
                yp = int(ts[5]) # point de passage
                status,a,b,c,d,start,extent = create_arcParameter(xd,yd,xf,yf,xp,yp)
                canvas.create_arc(a,b,c,d,start=start,extent=extent,style=tk.ARC)
                if status!='ok':
                    messagebox.showinfo("information",status)
                xcur = xf
                ycur = yf
            else:
                messagebox.showinfo("information","Not yet implemented")
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
            w = self.frame.grid_slaves(row=l,column=0)[0]
            type = w.get()
            if type =="":
                continue
            if not type in self.implementedTypes:
                messagebox.showinfo("information","one of the types is implemented")
                return  # since the type is not yet implemented (TODO)
            # here a type implemented
            ok = True
            try:
                XFin = int(self.frame.grid_slaves(row=l,column=1)[0].get())
                YFin = int(self.frame.grid_slaves(row=l,column=2)[0].get())
                S = int(self.frame.grid_slaves(row=l,column=c-2)[0].get())
                P = "selected" in self.frame.grid_slaves(row=l,column=c-1)[0].state()
            except:
                messagebox.showinfo("Information","Syntax error on one or more field(s)")
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
                    messagebox.showinfo("Information","Syntax error on one or more field(s)")
                    return
                section = f"{type} {XFin} {YFin} {ZFin} {N} {S} {P}"
                self.trajDescript.append(section)
            elif type=="arc1":
                XP = int(self.frame.grid_slaves(row=l,column=4)[0].get())
                YP = int(self.frame.grid_slaves(row=l,column=5)[0].get())
                ZP = 0
                section=f"{type} {XFin} {YFin} {ZFin} {XP} {YP} {ZP} {S} {P}"
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
        self.frame.grid_slaves(row=r,column=9)[0].config(state="normal") #checkbutton
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

    def insertBelow(self,k):
        """
        insert an empty line after line k, 0<=k<r
        """
        c,r = self.frame.grid_size()
        if k<0 or k>=r:
            return
        for row in range(r,k,-1):
            for col in range(c):
                print(f"row-1={row-1} col={col}")
                w = self.frame.grid_slaves(row=row-1,column=col)[0]
                print("w lu")
                w.grid(row=row,column=col)

        # FIN def insertBelow(self,k):
    # ################################################################################
    def removeLine(self,line,tl):
        print(f"entering removeLine with {line} {tl}")
        tl.destroy()
        
        
    def addLine(self,line=""):
        def editLine(event,line):
            # print("entering editLine ",line)
            tl = tk.Toplevel()
            # while this toplevel is living NO other action is possible :
            tl.focus_force()
            tl.wait_visibility()
            tl.grab_set()
            lab = tk.Label(tl,text="Line %d"%(line+1))
            butInsBel = tk.Button(tl,text="Insert line below")
            butDel = tk.Button(tl,text="Delete line",command=lambda :self.removeLine(line,tl))
            butCop = tk.Button(tl,text="Copy line")
            butPas = tk.Button(tl,text="Paste line")
            lab.pack()
            butInsBel.pack()
            butDel.pack()
            butCop.pack()
            butPas.pack()
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
        w.grid(row=r,column=9)
        w.config(state="disabled")
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
            w = self.frame.grid_slaves(row=r,column=8)[0]# speed
            w.config(state="normal")
            w.insert(0,ls[4])
        elif type=="arc1":
            w = self.frame.grid_slaves(row=r,column=4)[0] #xPassage
            w.config(state="normal")
            w.insert(0,ls[3])
            w = self.frame.grid_slaves(row=r,column=5)[0] #yPassage
            w.config(state="normal")
            w.insert(0,ls[4])
            w = self.frame.grid_slaves(row=r,column=8)[0]# speed
            w.config(state="normal")
            w.insert(0,ls[3])
        elif type =="ezsqx":
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
