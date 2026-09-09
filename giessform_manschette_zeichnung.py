import math, giessform_manschette as F, manschette as M

def kontur(f, x0, x1, y0, y1, n):
    segs=[]; dx=(x1-x0)/n; dy=(y1-y0)/n
    v=[[f(x0+i*dx, y0+j*dy) for j in range(n+1)] for i in range(n+1)]
    for i in range(n):
        for j in range(n):
            p=[(x0+i*dx,y0+j*dy,v[i][j]),(x0+(i+1)*dx,y0+j*dy,v[i+1][j]),
               (x0+(i+1)*dx,y0+(j+1)*dy,v[i+1][j+1]),(x0+i*dx,y0+(j+1)*dy,v[i][j+1])]
            kr=[]
            for k in range(4):
                a=p[k]; b=p[(k+1)%4]
                if (a[2]<0)!=(b[2]<0):
                    t=a[2]/(a[2]-b[2])
                    kr.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
            if len(kr)==2: segs.append((kr[0],kr[1]))
            elif len(kr)==4: segs.append((kr[0],kr[1])); segs.append((kr[2],kr[3]))
    return segs

def pfad(segs, tr, farbe, w=1.1):
    d=[]
    for a,b in segs:
        ax,ay=tr(*a); bx,by=tr(*b)
        d.append(f"M{ax:.2f} {ay:.2f}L{bx:.2f} {by:.2f}")
    return (f'<path d="{"".join(d)}" fill="none" stroke="{farbe}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')

S=4.2   # mm -> px
out=[]
W,H=1180,1000
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#F2F4F1"/>')
def txt(x,y,s,size=15,farbe="#161A17",w=600,anchor="start"):
    out.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Condensed,'
               f'DejaVu Sans Condensed,sans-serif" font-size="{size}" '
               f'font-weight="{w}" fill="{farbe}" text-anchor="{anchor}">{s}</text>')

INK="#161A17"; AKZ="#C7422A"; SOFT="#5E665E"; LIN="#B9C1B7"

# --- Ansicht 1: Trennflaeche Haelfte A (Blick auf x = 0) -------------------
ox,oy=70,120
tr1=lambda y,z:(ox+(y-F.Y_UNTEN)*S, oy+(F.Z_OBEN-z)*S)
txt(ox,oy-58,"1  Trennfläche Hälfte A",19,INK,700)
txt(ox,oy-36,"Blick auf die Ebene x = 0. Alles Sichtbare ist in diese Hälfte "
             "gefräst.",13,SOFT,400)
f=lambda y,z: F.feld_a(-0.02,y,z)
out.append(pfad(kontur(f,F.Y_UNTEN-1,F.Y_OBEN+1,F.Z_UNTEN-1,F.Z_OBEN+1,300),tr1,INK,1.2))
g=lambda y,z: M.feld(-0.02,y,z)
out.append(pfad(kontur(g,F.Y_UNTEN-1,F.Y_OBEN+1,F.Z_UNTEN-1,F.Z_OBEN+1,300),tr1,AKZ,1.6))

def marke(y,z,s,dy=0,anchor="start"):
    px,py=tr1(y,z); txt(px+8,py+4+dy,s,12,SOFT,500,anchor)
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{AKZ}"/>')
marke(F.LAUF_Y,20,"Lauf Ø6")
marke(F.LAUF_Y,F.Z_OBEN-1.5,"Trichter Ø9")
marke(-20,F.ANSCHNITT_Z,"Anschnitt Ø4 – hier tritt das Silikon ein")
marke(F.STEIGER_Y,30,"Steiger Ø3")
marke(F.ENTL_Y,30,"Entlüftung Ø1,5")
marke(F.Y_ZENTRIER,-3,"Zentrierzapfen")
marke(-F.Y_ZENTRIER,-3,"Zentriernut",14)

# --- Ansicht 2: Querschnitt z = 14 ----------------------------------------
ox2,oy2=760,150
tr2=lambda x,y:(ox2+(x+34)*S, oy2+(F.Y_OBEN-y)*S)
txt(ox2-40,oy2-88,"2  Querschnitt z = 14 mm",19,INK,700)
txt(ox2-40,oy2-66,"Beide Hälften zusammengesteckt. Rot: das Silikonteil.",13,SOFT,400)
fa=lambda x,y: F.feld_a(x,y,14.0)
fb=lambda x,y: F.feld_b(x,y,14.0)
for ff in (fa,fb):
    out.append(pfad(kontur(ff,-18,18,F.Y_UNTEN-1,F.Y_OBEN+1,300),tr2,INK,1.2))
gm=lambda x,y: M.feld(x,y,14.0)
out.append(pfad(kontur(gm,-18,18,F.Y_UNTEN-1,F.Y_OBEN+1,300),tr2,AKZ,1.6))
px,py=tr2(0,-30.5); txt(px,py+18,"Trennebene x = 0",11,SOFT,500,"middle")
out.append(f'<path d="M{tr2(0,F.Y_OBEN+2)[0]:.1f} {tr2(0,F.Y_OBEN+2)[1]:.1f}'
           f'L{tr2(0,F.Y_UNTEN-1)[0]:.1f} {tr2(0,F.Y_UNTEN-1)[1]:.1f}" '
           f'stroke="{LIN}" stroke-width="1" stroke-dasharray="5 4"/>')

# --- Ansicht 3: Laengsschnitt y = 0 ---------------------------------------
ox3,oy3=760,600
tr3=lambda x,z:(ox3+(x+34)*S, oy3+(F.Z_OBEN-z)*S)
txt(ox3-40,oy3-58,"3  Längsschnitt y = 0 mm",19,INK,700)
txt(ox3-40,oy3-36,"Der Bohrungskern steht in beiden Stirnwänden.",13,SOFT,400)
for ff in (lambda x,z: F.feld_a(x,0.0,z), lambda x,z: F.feld_b(x,0.0,z)):
    out.append(pfad(kontur(ff,-18,18,F.Z_UNTEN-1,F.Z_OBEN+1,300),tr3,INK,1.2))
out.append(pfad(kontur(lambda x,z: M.feld(x,0.0,z),-18,18,F.Z_UNTEN-1,F.Z_OBEN+1,300),
                tr3,AKZ,1.6))

txt(70,H-40,"Türzwerg · Gießform Klinkenmanschette · Maße in mm · "
            "rot = Silikonteil, schwarz = Formkörper",12,SOFT,400)
out.append("</svg>")
open("tuerzwerg-giessform-manschette.svg","w").write("\n".join(out))
print("geschrieben")
