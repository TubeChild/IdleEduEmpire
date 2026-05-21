"""
CampusView — isometric campus renderer for Idle Edu Empire.
Day/night cycle, seasonal decorations, holiday events, polished buildings.
"""
import math, random, pygame, os as _os

# ── Time ─────────────────────────────────────────────────────────────────────
DAY_CYCLE = 60.0   # real seconds per game day (visual + calendar)

# ── Calendar ──────────────────────────────────────────────────────────────────
_SEASONS = {1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',
            6:'Summer',7:'Summer',8:'Summer',9:'Autumn',
            10:'Autumn',11:'Autumn',12:'Winter'}
_HOLIDAY: dict[tuple,str] = {
    (1,1):'new_year',(2,14):'valentine',(4,7):'easter',
    (6,21):'midsummer',(10,31):'halloween',
    (12,24):'christmas',(12,25):'christmas',(12,31):'new_year_eve',
}
_MON = ['','January','February','March','April','May','June',
        'July','August','September','October','November','December']

# ── Building colours ──────────────────────────────────────────────────────────
_BC: dict[str,tuple] = {
    "Classroom":(185,162,120),"Library":(118,98,165),
    "Science Lab":(68,158,155),"Computer Lab":(62,102,185),
    "Sports Hall":(188,105,52),"Art Studio":(185,78,128),
    "University Wing":(92,145,92),"Research Centre":(52,62,168),
    "Innovation Hub":(168,140,35),"Space Academy":(40,46,108),
    "World Campus":(70,168,95),"Quantum Institute":(108,40,168),
    "Nexus of Knowledge":(168,80,38),
}
_SLOTS = [( 0, 0),( 1, 0),( 0, 1),(-1, 0),( 0,-1),
          ( 1, 1),(-1, 1),(-1,-1),( 1,-1),
          ( 2, 0),( 0, 2),(-2, 0),( 0,-2)]
_NAMES = ["Classroom","Library","Science Lab","Computer Lab","Sports Hall",
          "Art Studio","University Wing","Research Centre","Innovation Hub",
          "Space Academy","World Campus","Quantum Institute","Nexus of Knowledge"]

# Kenney isometric-building tile assignments for zone 1 buildings
_TILE_MAP: dict[str, str] = {
    "Classroom":          "buildingTiles_001.png",
    "Library":            "buildingTiles_030.png",
    "Science Lab":        "buildingTiles_015.png",
    "Computer Lab":       "buildingTiles_010.png",
    "Sports Hall":        "buildingTiles_025.png",
    "Art Studio":         "buildingTiles_020.png",
    "University Wing":    "buildingTiles_035.png",
    "Research Centre":    "buildingTiles_055.png",
    "Innovation Hub":     "buildingTiles_040.png",
    "Space Academy":      "buildingTiles_050.png",
    "World Campus":       "buildingTiles_100.png",
    "Quantum Institute":  "buildingTiles_045.png",
    "Nexus of Knowledge": "buildingTiles_005.png",
}
_TILE_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                           "assets", "kenney_isometric-buildings", "PNG")

# ── Sky keyframes (tod 0..1, top_rgb, bot_rgb) ────────────────────────────────
_SKY = [(0.00,(6,10,32),(4,7,22)),(0.20,(14,18,55),(10,14,40)),
        (0.25,(255,118,58),(200,76,38)),(0.29,(195,158,118),(155,118,78)),
        (0.33,(118,172,228),(78,138,210)),(0.50,(82,158,222),(48,118,205)),
        (0.65,(118,172,228),(78,138,210)),(0.71,(252,128,48),(212,88,28)),
        (0.75,(218,78,48),(168,48,33)),(0.79,(55,32,78),(38,22,58)),
        (0.83,(12,18,48),(6,10,32)),(1.00,(6,10,32),(4,7,22))]

# ── Window positions per stage (u,v on face 0..1) ─────────────────────────────
_WP = {1:[(0.50,0.42)],
       2:[(0.50,0.28),(0.50,0.68)],
       3:[(0.50,0.20),(0.50,0.52),(0.50,0.80)],
       4:[(0.30,0.18),(0.70,0.18),(0.30,0.50),(0.70,0.50),(0.30,0.80),(0.70,0.80)],
       5:[(0.20,0.14),(0.50,0.14),(0.80,0.14),
          (0.20,0.42),(0.50,0.42),(0.80,0.42),
          (0.20,0.68),(0.50,0.68),(0.80,0.68)]}

# Pre-baked star field (x_frac 0..1, y_frac of sky 0..1)
_STARS = [(random.Random(i*97+13).random(),
           random.Random(i*31+7).random()*0.88) for i in range(80)]

# ── Pure helpers ──────────────────────────────────────────────────────────────
def _sh(c,a): return tuple(max(0,min(255,v+a)) for v in c)
def _lc(a,b,t): return tuple(int(x+(y-x)*t) for x,y in zip(a,b))

def _sky_cols(tod):
    for i in range(len(_SKY)-1):
        t0,tp0,tb0=_SKY[i]; t1,tp1,tb1=_SKY[i+1]
        if t0<=tod<=t1:
            f=(tod-t0)/(t1-t0)
            return _lc(tp0,tp1,f),_lc(tb0,tb1,f)
    return _SKY[-1][1],_SKY[-1][2]

def _amb(tod):
    if 0.29<=tod<=0.71:
        t=(tod-0.29)/0.42; return 0.78+0.22*math.sin(t*math.pi)
    elif 0.25<=tod<0.29: return 0.38+0.40*((tod-0.25)/0.04)
    elif 0.71<tod<=0.75: return 0.38+0.40*((0.75-tod)/0.04)
    return 0.38

def _stage(n):
    if n==0:return 0
    if n<5: return 1
    if n<15:return 2
    if n<30:return 3
    if n<50:return 4
    return 5

def _bh(s,tw): return int(tw*[0,0.38,0.62,0.88,1.14,1.45][s])

def _fp(A,B,C,D,u,v):
    """Bilinear interpolation on quad (A=TL,B=TR,C=BR,D=BL)."""
    tx=A[0]+u*(B[0]-A[0]); ty=A[1]+u*(B[1]-A[1])
    bx=D[0]+u*(C[0]-D[0]); by=D[1]+u*(C[1]-D[1])
    return (int(tx+v*(bx-tx)),int(ty+v*(by-ty)))

def _lit(bi,wi): return (bi*17+wi*7)%10>=4

def _arc(tod,rect,sky_h,rise,sett):
    if rise<sett:
        if not(rise<=tod<=sett): return None
        t=(tod-rise)/(sett-rise)
    else:
        span=1-rise+sett
        if tod>=rise:   t=(tod-rise)/span
        elif tod<=sett: t=(1-rise+tod)/span
        else: return None
    cx=rect.x+int(rect.width*t)
    cy=rect.y+8+int((sky_h-16)*(1-4*t*(1-t)))
    return cx,cy

# ── ISO draw ──────────────────────────────────────────────────────────────────
def _tile(surf,cx,cy,tw,th,col):
    hw,hh=tw//2,th//2
    pts=[(cx,cy),(cx+hw,cy+hh),(cx,cy+th),(cx-hw,cy+hh)]
    pygame.draw.polygon(surf,col,pts)
    pygame.draw.polygon(surf,_sh(col,-28),pts,1)

def _face_wins(surf,A,B,C,D,stage,bi,night,holiday):
    xc=[(235,55,55),(55,195,55),(55,95,235),(235,215,45)]
    wu,wv=0.20,0.14
    for i,(u,v) in enumerate(_WP.get(stage,[])):
        tl=_fp(A,B,C,D,u-wu/2,v-wv/2); tr=_fp(A,B,C,D,u+wu/2,v-wv/2)
        br=_fp(A,B,C,D,u+wu/2,v+wv/2); bl=_fp(A,B,C,D,u-wu/2,v+wv/2)
        if tl==tr or tl==bl: continue
        if night:
            if _lit(bi,i):
                wc=(255,105,15) if holiday=='halloween' else \
                   xc[i%4] if holiday in('christmas','christmas_eve') else \
                   (255,238,155)
            else:
                wc=(22,26,42)
        else:
            wc=(168,210,232)
        pygame.draw.polygon(surf,wc,[tl,tr,br,bl])
        pygame.draw.polygon(surf,_sh(wc,-45),[tl,tr,br,bl],1)

def _box(surf,cx,cy,tw,th,height,color,stage,night,bi,holiday,season):
    if height<=0: return
    hw,hh=tw//2,th//2
    tt=(cx,cy-height);tr=(cx+hw,cy+hh-height);tb=(cx,cy+th-height);tl=(cx-hw,cy+hh-height)
    gr=(cx+hw,cy+hh);gb=(cx,cy+th);gl=(cx-hw,cy+hh)

    pygame.draw.polygon(surf,_sh(color,-48),[gl,gb,tb,tl])  # left face
    pygame.draw.polygon(surf,_sh(color,-22),[gr,gb,tb,tr])  # right face

    roof = (218,232,248) if season=='Winter' else _sh(color,18)
    pygame.draw.polygon(surf,roof,[tt,tr,tb,tl])            # top / snow

    dk=_sh(color,-85)
    pygame.draw.lines(surf,dk,False,[gl,gb,gr],1)
    pygame.draw.lines(surf,dk,False,[tl,tt,tr],1)
    pygame.draw.line(surf,dk,tl,gl,1); pygame.draw.line(surf,dk,tr,gr,1)

    if stage>0 and tw>=18:
        _face_wins(surf,tl,tb,gb,gl,stage,bi,night,holiday)  # left
        _face_wins(surf,tb,tr,gr,gb,stage,bi,night,holiday)  # right

    if stage>=4 and tw>=20:
        fx,fy=cx,cy-height-2
        pygame.draw.line(surf,(55,55,55),(fx,fy),(fx,fy+9),1)
        pygame.draw.polygon(surf,(210,38,38),[(fx,fy),(fx+7,fy+2),(fx,fy+5)])

# ── Seasonal props ────────────────────────────────────────────────────────────
def _draw_midsommar(surf,x,y,h=72):
    pw=max(3,h//24)
    pygame.draw.line(surf,(90,55,25),(x,y),(x,y-h),pw)
    cby=y-int(h*0.74); cbw=int(h*0.46)
    pygame.draw.line(surf,(90,55,25),(x-cbw,cby),(x+cbw,cby),pw)
    # birch leaves on crossbar
    for lx in range(x-cbw,x+cbw+1,5):
        for dy in(-3,0,3):
            pygame.draw.circle(surf,(78,152,50),(lx,cby+dy),3)
    # two wreaths
    for sx in(-1,1):
        wx=x+sx*int(cbw*0.55); wy=cby+11
        pygame.draw.circle(surf,(50,118,40),(wx,wy),9,2)
        for a in range(0,360,60):
            r=math.radians(a)
            pygame.draw.circle(surf,(255,218,48),
                               (wx+int(math.cos(r)*9),wy+int(math.sin(r)*9)),2)
    # ribbons
    rcols=[(215,45,45),(45,215,45),(45,90,215),(215,215,45),(215,45,215)]
    for i,col in enumerate(rcols):
        rx=x-cbw+int(i*cbw*2/max(1,len(rcols)-1))
        pts=[]
        for s in range(9):
            t=s/8; wave=math.sin(t*math.pi*2.5+i*1.1)*5
            pts.append((rx+int(wave),cby+int(h*0.62*t)))
        if len(pts)>=2: pygame.draw.lines(surf,col,False,pts,2)
    # top birch crown
    for a in range(0,360,40):
        r=math.radians(a)
        pygame.draw.circle(surf,(72,148,45),
                           (x+int(math.cos(r)*9),y-h+int(math.sin(r)*5)),4)
    pygame.draw.circle(surf,(255,255,100),(x,y-h),4)

def _draw_xmas_tree(surf,x,y,h=55):
    tw2=int(h*0.55)
    for layer in range(3):
        ly=y-int(h*(0.28+layer*0.22))
        lw=tw2-layer*int(tw2*0.28)
        col=(38+layer*8,135-layer*12,48+layer*4)
        pygame.draw.polygon(surf,col,
                            [(x-lw,ly),(x+lw,ly),(x,ly-int(h*0.30))])
        for i in range(4):
            ox=x-lw+int(i*(lw*2/3)); oy=ly-4
            c=[(235,55,55),(55,195,55),(55,90,235),(235,215,45)][i%4]
            pygame.draw.circle(surf,c,(ox,oy),3)
    pygame.draw.rect(surf,(100,62,30),(x-4,y-int(h*0.12),8,int(h*0.12)))
    pygame.draw.polygon(surf,(255,240,60),
                        [(x,y-h-6),(x-5,y-h+2),(x+5,y-h+2)])

def _draw_pumpkin(surf,x,y,r=9):
    pygame.draw.circle(surf,(210,90,15),(x,y),r)
    pygame.draw.circle(surf,(185,70,10),(x,y),r,1)
    pygame.draw.line(surf,(45,100,25),(x,y-r),(x,y-r-5),2)
    # face
    ey=y-2; pygame.draw.polygon(surf,(30,20,10),
        [(x-5,ey-3),(x-3,ey),(x-1,ey-3)])
    pygame.draw.polygon(surf,(30,20,10),
        [(x+1,ey-3),(x+3,ey),(x+5,ey-3)])
    pygame.draw.lines(surf,(30,20,10),False,
        [(x-4,y+2),(x-2,y+4),(x,y+2),(x+2,y+4),(x+4,y+2)],1)

def _draw_heart(surf,x,y,s=8):
    col=(220,50,90)
    pygame.draw.circle(surf,col,(x-s//2,y-s//3),s//2)
    pygame.draw.circle(surf,col,(x+s//2,y-s//3),s//2)
    pygame.draw.polygon(surf,col,[(x-s,y-s//3),(x+s,y-s//3),(x,y+s//2)])

def _draw_egg(surf,x,y,col):
    pygame.draw.ellipse(surf,col,(x-5,y-7,10,14))
    pygame.draw.ellipse(surf,_sh(col,-40),(x-5,y-7,10,14),1)
    pygame.draw.line(surf,_sh(col,40),(x-3,y-3),(x+3,y-3),1)

def _draw_leaf_pile(surf,x,y,rng):
    cols=[(185,78,25),(210,120,20),(195,55,20),(170,140,30)]
    for _ in range(6):
        lx=x+rng.randint(-12,12); ly=y+rng.randint(-3,3)
        pygame.draw.ellipse(surf,rng.choice(cols),(lx-5,ly-3,10,6))

# ── Firework particle ─────────────────────────────────────────────────────────
class _FW:
    COLS=[(255,80,80),(80,255,80),(80,130,255),(255,220,50),(255,90,200),(80,255,220)]
    def __init__(self,x,y):
        self.x=x; self.y=y; self.r=0.0
        self.mr=random.randint(28,65)
        self.col=random.choice(self.COLS); self.alpha=255.0
    def update(self,dt):
        self.r+=48*dt
        if self.r>=self.mr: self.alpha-=280*dt
    def draw(self,surf):
        a=max(0,int(self.alpha)); ir=max(1,int(self.r))
        if a<=0: return
        s=pygame.Surface((ir*2+4,ir*2+4),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.col,a),(ir+2,ir+2),ir,2)
        surf.blit(s,(self.x-ir-2,self.y-ir-2))
    @property
    def alive(self): return self.alpha>0

def _make_cloud(w, h, alpha=165):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for cx, cy, rx, ry in [
        (w//2,  h//2,   w//3,  h//3),
        (w*3//8, h//2+h//10, w//4, h//4),
        (w*5//8, h//2+h//10, w//4, h//4),
        (w//4,  h//2+h//7,  w//5,  h//5),
        (w*3//4,h//2+h//7,  w//5,  h//5),
    ]:
        pygame.draw.ellipse(s, (255,255,255,alpha), (cx-rx, cy-ry, rx*2, ry*2))
    return s

# ── CampusView ────────────────────────────────────────────────────────────────
class CampusView:
    _CITY_SEED=1337

    def __init__(self):
        self._time=0.0; self._par_x=0.0
        self._city=self._gen_city()
        self._snow=[]; self._snow_acc=0.0
        self._fw=[]; self._fw_acc=0.0

        # Pre-baked glow surfaces
        self._sun_glow = pygame.Surface((80,80), pygame.SRCALPHA)
        pygame.draw.circle(self._sun_glow, (255,240,100,28), (40,40), 40)
        self._sun_inner = pygame.Surface((50,50), pygame.SRCALPHA)
        pygame.draw.circle(self._sun_inner, (255,255,190,52), (25,25), 25)
        self._moon_glow = pygame.Surface((50,50), pygame.SRCALPHA)
        pygame.draw.circle(self._moon_glow, (200,215,255,32), (25,25), 25)
        self._firefly_glow = pygame.Surface((16,16), pygame.SRCALPHA)
        pygame.draw.circle(self._firefly_glow, (220,220,80,75), (8,8), 8)

        # Cloud data: [x_frac, y_frac_of_sky, parallax_speed, surf]
        self._cloud_data = [
            [0.08, 0.18, 0.35, _make_cloud(180, 55, 160)],
            [0.52, 0.10, 0.22, _make_cloud(240, 65, 138)],
            [0.76, 0.25, 0.52, _make_cloud(150, 48, 152)],
            [0.33, 0.06, 0.30, _make_cloud(210, 60, 128)],
        ]

        # Building tile sprites (Kenney isometric-buildings)
        self._building_tiles: dict = {}
        self._tile_cache: dict = {}
        for name, fname in _TILE_MAP.items():
            path = _os.path.join(_TILE_DIR, fname)
            try:
                self._building_tiles[name] = pygame.image.load(path).convert_alpha()
            except Exception:
                pass

        # Holiday sprite: Christmas tree from roguelikeHoliday sheet
        self._xmas_sprite: pygame.Surface | None = None
        try:
            _hol_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                      "assets", "kenney_holiday-extras",
                                      "Tilesheet", "roguelikeHoliday_transparent.png")
            _hol = pygame.image.load(_hol_path).convert_alpha()
            # Cell (0,2) is a full Christmas tree (182px of green content)
            self._xmas_sprite = _hol.subsurface(0, 34, 17, 17)
        except Exception:
            pass

        # Theme weather particles
        self._theme = "classic"
        self._fireflies: list = []   # [x_frac, y_frac, vx, vy, phase, brightness]
        self._embers:    list = []   # [x_frac, y_frac, vx, vy, size, alpha]
        self._rain:      list = []   # [x_frac, y_frac, speed, length]

    # ── City ──────────────────────────────────────────────────────────────────
    def _gen_city(self):
        rng=random.Random(self._CITY_SEED); layers=[]
        for mnh,mxh,n in[(12,30,32),(22,58,24),(38,95,18)]:
            row=[]; x=0
            for _ in range(n):
                w=rng.randint(16,52); h=rng.randint(mnh,mxh)
                row.append((x,w,h)); x+=w+rng.randint(2,10)
            layers.append(row)
        return layers

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self,dt):
        self._time+=dt; self._par_x+=dt*1.6
        st=self._state()
        season=st['season']; holiday=st['holiday']

        # Snow
        if season=='Winter' or holiday in('christmas','christmas_eve'):
            self._snow_acc+=dt*18
            while self._snow_acc>=1:
                self._snow_acc-=1
                self._snow.append([random.random(),0.0,random.uniform(18,48)])
        for f in self._snow: f[1]+=f[2]*dt
        self._snow=[f for f in self._snow if f[1]<900]
        if len(self._snow)>220: self._snow=self._snow[-220:]

        # Fireworks
        if holiday=='new_year_eve':
            self._fw_acc+=dt
            if self._fw_acc>=random.uniform(0.6,1.8):
                self._fw_acc=0.0
                self._fw.append(_FW(random.randint(50,500),random.randint(30,160)))
        for f in self._fw: f.update(dt)
        self._fw=[f for f in self._fw if f.alive]

        # Theme weather particles
        if self._theme == "night":
            while len(self._fireflies) < 18:
                self._fireflies.append([
                    random.random(), random.uniform(0.3, 0.95),
                    random.uniform(-0.008, 0.008), random.uniform(-0.005, 0.005),
                    random.uniform(0, math.pi*2), random.randint(170, 255)
                ])
            for f in self._fireflies:
                f[0] = (f[0] + f[2] * dt) % 1.0
                f[1] += f[3] * dt
                if f[1] < 0.20 or f[1] > 0.95: f[3] *= -1
                f[4] += dt * random.uniform(1.5, 3.0)
        else:
            self._fireflies.clear()

        if self._theme == "sunset":
            while len(self._embers) < 22:
                self._embers.append([
                    random.random(), random.uniform(0.5, 1.0),
                    random.uniform(-0.008, 0.008), random.uniform(-0.06, -0.12),
                    random.randint(2, 4), random.randint(180, 255)
                ])
            for e in self._embers:
                e[0] = (e[0] + e[2] * dt) % 1.0
                e[1] += e[3] * dt
                e[5] = max(0, e[5] - 18 * dt)
                if e[1] < 0 or e[5] <= 0:
                    e[0] = random.random()
                    e[1] = random.uniform(0.7, 1.0)
                    e[5] = random.randint(180, 255)
        else:
            self._embers.clear()

        if self._theme == "storm":
            while len(self._rain) < 80:
                self._rain.append([
                    random.random(), random.uniform(-0.15, 1.0),
                    random.uniform(0.55, 0.90), random.randint(12, 24)
                ])
            for r in self._rain:
                r[1] += r[2] * dt
                if r[1] > 1.0:
                    r[0] = random.random()
                    r[1] = random.uniform(-0.2, 0.0)
        else:
            self._rain.clear()

    # ── State dict ────────────────────────────────────────────────────────────
    def _state(self):
        tod=(self._time%DAY_CYCLE)/DAY_CYCLE
        total_days=int(self._time/DAY_CYCLE)
        year=1+total_days//365
        doy=total_days%365
        month=1; day=doy
        for m,days in enumerate([31,28,31,30,31,30,31,31,30,31,30,31],1):
            if day<days: month=m; break
            day-=days
        else: month=12; day=min(day,30)
        day=max(1,day+1)
        season=_SEASONS.get(month,'Spring')
        holiday=_HOLIDAY.get((month,day))
        is_night=tod<0.22 or tod>0.82
        hour=int(tod*24); minute=int((tod*24-hour)*60)
        sky_t,sky_b=_sky_cols(tod)
        return dict(tod=tod,hour=hour,minute=minute,is_night=is_night,
                    ambient=_amb(tod),sky_top=sky_t,sky_bot=sky_b,
                    month=month,day=day,year=year,season=season,holiday=holiday)

    # ── Zone theme data ───────────────────────────────────────────────────────
    _ZONE_THEMES = {
        2:  dict(sky_top=(180,165,140), sky_bot=(210,195,165), ground=(150,125,85)),
        3:  dict(sky_top=(10,20,70),    sky_bot=(20,50,120),   ground=(80,90,105)),
        4:  dict(sky_top=(80,160,215),  sky_bot=(200,220,190), ground=(205,185,130)),
        5:  dict(sky_top=(5,8,18),      sky_bot=(15,22,50),    ground=(165,165,160)),
        6:  dict(sky_top=(40,10,75),    sky_bot=(90,25,145),   ground=(75,45,105)),
        7:  dict(sky_top=(205,125,45),  sky_bot=(235,175,70),  ground=(115,85,45)),
        8:  dict(sky_top=(255,250,220), sky_bot=(220,235,255), ground=(245,248,255)),
        9:  dict(sky_top=(18,5,5),      sky_bot=(55,12,12),    ground=(55,22,12)),
        10: dict(sky_top=(18,12,48),    sky_bot=(55,35,115),   ground=(58,52,72)),
    }

    # ── Main draw ─────────────────────────────────────────────────────────────
    def draw(self,surf,rect,game,tile_base=60,zone_id=1,theme=None):
        st=self._state()
        st['all_time_kp']=game.all_time_kp
        surf.set_clip(rect)
        sky_h=max(rect.height//3,55)
        horizon=rect.y+sky_h

        if zone_id==1:
            self._theme = theme or "classic"
            self._draw_sky(surf,rect,sky_h,st)
            self._draw_city(surf,rect,sky_h,horizon,st)
            gc=(138,178,112) if st['season']!='Winter' else (195,210,195)
            pygame.draw.rect(surf,gc,(rect.x,horizon,rect.width,rect.height-sky_h))
            self._draw_campus(surf,rect,horizon,game,tile_base,st)
            self._draw_snow(surf,rect,st)
            self._draw_fw(surf,rect,st)
            # Cosmetic theme tint for zone 1
            if theme and theme != "classic":
                from data import COSMETIC_THEMES as _CT
                _td = next((t for t in _CT if t["id"] == theme), None)
                if _td and _td.get("tint"):
                    _tsurf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    _r2, _g2, _b2 = _td["tint"]
                    _tsurf.fill((_r2, _g2, _b2, _td["tint_alpha"]))
                    surf.blit(_tsurf, (rect.x, rect.y))
            self._draw_theme_weather(surf, rect, st)
        else:
            theme=self._ZONE_THEMES.get(zone_id,{})
            sky_top=theme.get('sky_top',(10,20,70))
            sky_bot=theme.get('sky_bot',(20,50,120))
            ground=theme.get('ground',(80,90,80))
            tod=st['tod']
            # Draw zone sky gradient
            for i in range(sky_h):
                t=i/max(1,sky_h)
                pygame.draw.line(surf,_lc(sky_top,sky_bot,t),
                                 (rect.x,rect.y+i),(rect.x+rect.width,rect.y+i))
            # Zone 5: always draw stars
            if zone_id==5:
                for xf,yf in _STARS:
                    sx=rect.x+int(xf*rect.width); sy=rect.y+int(yf*sky_h)
                    a=random.randint(160,255)
                    pygame.draw.circle(surf,(a,a,a),(sx,sy),1)
            else:
                # Stars at night for non-moon zones
                if tod<0.26 or tod>0.80:
                    bright=1.0 if(tod<0.21 or tod>0.84) else \
                           min(1.0,(tod-0.80)/0.04) if tod>0.80 else min(1.0,(0.26-tod)/0.05)
                    for xf,yf in _STARS:
                        sx=rect.x+int(xf*rect.width); sy=rect.y+int(yf*sky_h)
                        a=int(bright*random.randint(140,220))
                        pygame.draw.circle(surf,(a,a,a),(sx,sy),1)
                # Moon arc
                mp=_arc(tod,rect,sky_h,0.75,0.25)
                if mp:
                    surf.blit(self._moon_glow,(mp[0]-25,mp[1]-25))
                    pygame.draw.circle(surf,(228,232,210),mp,max(5,sky_h//9))
                    pygame.draw.circle(surf,_lc(sky_top,sky_bot,0.1),
                                       (mp[0]-3,mp[1]-2),max(3,sky_h//14))
                # Sun arc — skip for underworld (zone 9) and hero world (zone 10) at night
                sun_blocked=(zone_id in (9,) and True) if False else False
                sp=_arc(tod,rect,sky_h,0.25,0.75)
                if sp and not sun_blocked:
                    surf.blit(self._sun_glow,(sp[0]-40,sp[1]-40))
                    surf.blit(self._sun_inner,(sp[0]-25,sp[1]-25))
                    pygame.draw.circle(surf,(255,230,80),sp,max(6,sky_h//8))
                    pygame.draw.circle(surf,(255,245,140),sp,max(3,sky_h//14))
            # Ground fill
            pygame.draw.rect(surf,ground,(rect.x,horizon,rect.width,rect.height-sky_h))
            # Zone-specific background buildings (replaces city parallax)
            self._zone_bg_buildings(surf,rect,sky_h,horizon,zone_id)
            # Zone-specific background elements
            self._zone_bg(surf,rect,sky_h,horizon,zone_id,sky_top,sky_bot,ground)
            # Zone 5: animated Earth + Sun in the sky/ground area
            if zone_id==5:
                self._draw_moon_objects(surf,rect)
            # Campus buildings tinted
            self._draw_campus(surf,rect,horizon,game,tile_base,st,zone_id=zone_id)

        self._draw_overlay(surf,rect,st,tile_base)
        surf.set_clip(None)

    # ── Theme weather particles ───────────────────────────────────────────────
    def _draw_theme_weather(self, surf, rect, st):
        if self._theme == "night":
            for f in self._fireflies:
                br = int(abs(math.sin(f[4])) * f[5])
                if br < 35: continue
                x = rect.x + int(f[0] * rect.width)
                y = rect.y + int(f[1] * rect.height)
                pygame.draw.circle(surf, (br, br, min(255, br//2+30)), (x, y), 2)
                self._firefly_glow.set_alpha(br // 4)
                surf.blit(self._firefly_glow, (x-8, y-8))
        elif self._theme == "sunset":
            for e in self._embers:
                if not (0.01 < e[1] < 0.99): continue
                x = rect.x + int(e[0] * rect.width)
                y = rect.y + int(e[1] * rect.height)
                g_rand = random.randint(90, 150)
                pygame.draw.circle(surf, (255, g_rand, 15), (x, y), e[4])
        elif self._theme == "storm":
            for r in self._rain:
                if not (0.0 < r[1] < 1.0): continue
                x = rect.x + int(r[0] * rect.width)
                y = rect.y + int(r[1] * rect.height)
                ex = x - int(r[3] * 0.22)
                ey = y + r[3]
                pygame.draw.line(surf, (155, 190, 228), (x, y), (ex, ey), 1)

    # ── Zone background buildings (replaces city parallax for non-zone-1) ────────
    def _zone_bg_buildings(self,surf,rect,sky_h,horizon,zone_id):
        """Draw zone-themed background building silhouettes near the horizon."""
        amb=0.72
        if zone_id==2:
            # Ruins: low crumbling stone blocks, no tall buildings
            pass  # wall silhouettes handled in _zone_bg
        elif zone_id==3:
            # The Future: tall rounded-top towers with dome caps
            col1=(38,58,105); col2=(28,44,82); col3=(20,32,65)
            buildings=[
                # (cx, width, height, style)  style: 0=dome-top 1=round-pillar 2=stepped
                (rect.x+30,  32, 95, 0),(rect.x+80,  20, 70, 1),(rect.x+118, 28, 112,0),
                (rect.x+162, 18, 58, 1),(rect.x+195, 36, 130,0),(rect.x+245, 22, 80, 1),
                (rect.x+278, 30, 100,0),(rect.x+316, 16, 50, 2),(rect.x+345, 38, 145,0),
                (rect.x+390, 24, 88, 1),(rect.x+420, 32, 108,0),
            ]
            for i,(bx,bw,bh,style) in enumerate(buildings):
                col=(col1,col2,col3)[i%3]
                by=horizon-bh
                pygame.draw.rect(surf,col,(bx-bw//2,by,bw,bh))
                if style==0:  # dome cap
                    pygame.draw.ellipse(surf,_sh(col,12),(bx-bw//2-2,by-bw//4,bw+4,bw//2))
                elif style==1:  # round pillar top
                    pygame.draw.circle(surf,_sh(col,8),(bx,by),bw//2)
                elif style==2:  # stepped top
                    pygame.draw.rect(surf,_sh(col,8),(bx-bw//2+3,by-8,bw-6,8))
                    pygame.draw.rect(surf,_sh(col,15),(bx-bw//2+7,by-14,bw-14,6))
                # Lit windows — small blue-white dots
                for wy in range(by+8,horizon-4,12):
                    for wx_off in range(4,bw-4,8):
                        if random.Random(bx*100+wy+wx_off).random()<0.55:
                            pygame.draw.rect(surf,(80,140,220),(bx-bw//2+wx_off,wy,4,3))
        elif zone_id==4:
            # Ancient Academy: Greek/Roman colonnaded structures
            pass  # columns handled in _zone_bg; keep clean
        elif zone_id==5:
            pass  # no background buildings on moon
        elif zone_id==6:
            # Magical Realm: pointy spires and wizard towers
            col1=(55,22,80); col2=(38,14,62); col3=(72,30,100)
            spires=[
                (rect.x+20,  12, 80, 3),(rect.x+52,  18,110, 4),(rect.x+88,  14, 65, 2),
                (rect.x+118, 22,135, 5),(rect.x+158, 10, 50, 2),(rect.x+185, 26,155, 6),
                (rect.x+228, 16, 90, 3),(rect.x+260, 20,120, 4),(rect.x+298, 12, 70, 2),
                (rect.x+328, 24,140, 5),(rect.x+368, 14, 80, 3),(rect.x+400, 28,160, 6),
            ]
            for i,(bx,bw,bh,floors) in enumerate(spires):
                col=(col1,col2,col3)[i%3]
                by=horizon-bh
                # Tower shaft
                pygame.draw.rect(surf,col,(bx-bw//2,by,bw,bh))
                # Pointy spire tip — sharp triangle
                tip_h=int(bh*0.35)
                pygame.draw.polygon(surf,_sh(col,20),
                    [(bx-bw//2-2,by),(bx+bw//2+2,by),(bx,by-tip_h)])
                # Magic window glow (purple/pink dots)
                for wy in range(by+6,horizon-4,14):
                    if random.Random(bx*77+wy).random()<0.4:
                        gc=(180,60,220) if i%2==0 else (220,100,180)
                        pygame.draw.circle(surf,gc,(bx,wy),2)
        elif zone_id==7:
            pass  # volcanoes in _zone_bg dominate; skip extra buildings
        elif zone_id==8:
            pass  # heavens — pearly gates in _zone_bg; keep sky clean
        elif zone_id==9:
            # Underworld: jagged dark fortress towers
            col1=(38,12,8); col2=(55,18,12); col3=(25,8,5)
            towers=[
                (rect.x+25,  28, 80, True),(rect.x+72,  20, 60,False),
                (rect.x+108, 32, 95, True),(rect.x+155, 18, 55,False),
                (rect.x+188, 36,110, True),(rect.x+240, 22, 70,False),
                (rect.x+272, 30, 90, True),(rect.x+318, 16, 48,False),
                (rect.x+348, 34,100, True),(rect.x+395, 24, 75,False),
            ]
            for i,(bx,bw,bh,has_battlements) in enumerate(towers):
                col=(col1,col2,col3)[i%3]
                by=horizon-bh
                pygame.draw.rect(surf,col,(bx-bw//2,by,bw,bh))
                if has_battlements:
                    for mb in range(bx-bw//2,bx+bw//2,7):
                        pygame.draw.rect(surf,col,(mb,by-6,4,6))
                # Lava-glow window slits (red/orange)
                for wy in range(by+10,horizon-6,16):
                    if random.Random(bx*33+wy).random()<0.35:
                        pygame.draw.rect(surf,(180,40,10),(bx-2,wy,4,6))
        elif zone_id==10:
            # Hero World: modern city skyline, darker/heroic
            col1=(30,28,60); col2=(22,20,48); col3=(42,38,75)
            buildings=[
                (rect.x+25,  24, 88),(rect.x+62,  16, 60),(rect.x+92,  30,110),
                (rect.x+138, 20, 72),(rect.x+172, 36,130),(rect.x+222, 18, 65),
                (rect.x+255, 28, 95),(rect.x+295, 14, 50),(rect.x+325, 32,120),
                (rect.x+372, 22, 80),(rect.x+408, 34,140),
            ]
            for i,(bx,bw,bh) in enumerate(buildings):
                col=(col1,col2,col3)[i%3]
                by=horizon-bh
                pygame.draw.rect(surf,col,(bx-bw//2,by,bw,bh))
                # Antenna on top
                pygame.draw.line(surf,_sh(col,15),(bx,by),(bx,by-8),1)
                # Blue-tinted windows
                for wy in range(by+5,horizon-4,10):
                    for wx_off in range(3,bw-3,7):
                        if random.Random(bx*55+wy+wx_off).random()<0.45:
                            pygame.draw.rect(surf,(60,80,160),(bx-bw//2+wx_off,wy,3,3))

    # ── Zone background elements ──────────────────────────────────────────────
    def _zone_bg(self,surf,rect,sky_h,horizon,zone_id,sky_top,sky_bot,ground):
        """Draw zone-specific decorative background elements."""
        if zone_id==2:
            # 2-3 crumbling wall silhouettes near horizon
            wall_col=(110,90,65)
            wall_data=[(rect.x+40, horizon-28,22,28),(rect.x+180,horizon-38,18,38),
                       (rect.x+275,horizon-24,20,24)]
            for wx,wy,ww,wh in wall_data:
                pygame.draw.rect(surf,wall_col,(wx,wy,ww,wh))
                # battlements
                for bx in range(wx,wx+ww,7):
                    pygame.draw.rect(surf,wall_col,(bx,wy-6,4,6))
                # cracks
                pygame.draw.line(surf,_sh(wall_col,-35),(wx+5,wy+4),(wx+9,wy+wh-4),1)
                pygame.draw.line(surf,_sh(wall_col,-35),(wx+12,wy+2),(wx+8,wy+wh//2),1)
            # Flickering torches on the walls
            torch_positions=[(rect.x+52,horizon-32),(rect.x+192,horizon-42),(rect.x+165,horizon-18)]
            for i,(tx,ty) in enumerate(torch_positions):
                flicker=0.6+0.4*math.sin(self._time*8+i*2.3)
                # pole
                pygame.draw.rect(surf,(80,55,30),(tx-1,ty,2,10))
                # flame body
                flame_h=int(7*flicker)
                flame_col=(int(255*flicker),int(120*flicker),20)
                inner_col=(255,230,80)
                pygame.draw.polygon(surf,flame_col,[(tx,ty-flame_h),(tx-3,ty+2),(tx+3,ty+2)])
                pygame.draw.polygon(surf,inner_col,[(tx,ty-flame_h+2),(tx-1,ty+1),(tx+1,ty+1)])
                # glow halo
                try:
                    gs=pygame.Surface((18,18),pygame.SRCALPHA)
                    alpha=int(80*flicker)
                    pygame.draw.circle(gs,(255,160,30,alpha),(9,9),7)
                    surf.blit(gs,(tx-9,ty-9))
                except Exception:
                    pass

        elif zone_id==3:
            # Neon accent lines on city-level buildings
            neon_cols=[(0,240,200),(200,0,255),(0,160,255)]
            for i,nc in enumerate(neon_cols):
                lx=rect.x+50+i*90; ly=horizon-10
                pygame.draw.line(surf,nc,(lx,ly),(lx,horizon-40),2)
                pygame.draw.line(surf,nc,(lx-10,horizon-40),(lx+10,horizon-40),2)

        elif zone_id==4:
            # Greek columns silhouette
            col_c=(210,200,170)
            col_positions=[rect.x+55,rect.x+130,rect.x+230,rect.x+290]
            cap_y=horizon-50
            for cpx in col_positions:
                # shaft
                pygame.draw.rect(surf,col_c,(cpx-5,cap_y,10,50))
                # capital
                pygame.draw.rect(surf,col_c,(cpx-9,cap_y-5,18,6))
                # base
                pygame.draw.rect(surf,col_c,(cpx-8,horizon-4,16,4))
            # entablature connecting columns
            pygame.draw.rect(surf,col_c,(col_positions[0]-9,cap_y-8,
                                         col_positions[-1]-col_positions[0]+18,4))

        elif zone_id==5:
            # Nothing extra; stars already drawn in draw()
            pass

        elif zone_id==6:
            # Sparkle particles (deterministic based on time for shimmering effect)
            t_seed=int(self._time*8)
            rng=random.Random(t_seed)
            for _ in range(12):
                px=rect.x+rng.randint(0,rect.width)
                py=rect.y+rng.randint(0,sky_h+30)
                br=rng.randint(160,255)
                pygame.draw.circle(surf,(br,br//2,br),(px,py),1)
            # Also a few larger sparkles in the ground area
            rng2=random.Random(t_seed+1)
            for _ in range(6):
                px=rect.x+rng2.randint(0,rect.width)
                py=horizon+rng2.randint(0,rect.height-sky_h)
                br=rng2.randint(140,220)
                pygame.draw.circle(surf,(br,br//3,br),(px,py),1)

        elif zone_id==7:
            # 3 volcanoes: 2 small smoking, 1 large erupting
            volcanoes=[
                dict(x=rect.x+65,  base_y=horizon, w=38, h=52, erupt=False),
                dict(x=rect.x+270, base_y=horizon, w=32, h=44, erupt=False),
                dict(x=rect.x+168, base_y=horizon, w=55, h=75, erupt=True),
            ]
            t_seed=int(self._time*6)
            rng=random.Random(t_seed)
            for v in volcanoes:
                vx=v['x']; vb=v['base_y']; vw=v['w']; vh=v['h']; erupt=v['erupt']
                # Volcano body triangle
                pts=[(vx,vb-vh),(vx+vw//2,vb),(vx-vw//2,vb)]
                pygame.draw.polygon(surf,(85,55,35),pts)
                pygame.draw.polygon(surf,_sh((85,55,35),-20),pts,1)
                # Crater
                pygame.draw.ellipse(surf,(110,60,30),(vx-vw//5,vb-vh-3,vw//2,8))
                if erupt:
                    # Eruption: lava blobs & fire particles
                    for i in range(8):
                        r2=random.Random(t_seed*100+i)
                        px=vx+r2.randint(-vw//6,vw//6)
                        py=vb-vh-r2.randint(4,vh//2)
                        c=r2.choice([(255,80,0),(255,160,0),(230,40,0)])
                        pygame.draw.circle(surf,c,(px,py),r2.randint(2,5))
                else:
                    # Smoke wisps
                    for i in range(4):
                        r2=random.Random(t_seed*50+i)
                        py=vb-vh-8-i*7
                        px=vx+r2.randint(-4,4)
                        a=120-i*25
                        sc=(160,155,155)
                        pygame.draw.circle(surf,sc,(px,py),3+i)

        elif zone_id==8:
            # Divine golden light rays across the sky
            ray_col=(255,240,150)
            ray_alpha_surf=pygame.Surface((rect.width,sky_h),pygame.SRCALPHA)
            ray_origins=[(rect.width//2+dx,0) for dx in(-60,-20,20,60,100)]
            for rx,ry in ray_origins:
                spread=80
                pts=[(rx-3,ry),(rx+3,ry),(rx+spread,sky_h),(rx-spread,sky_h)]
                pygame.draw.polygon(ray_alpha_surf,(*ray_col,28),pts)
            surf.blit(ray_alpha_surf,(rect.x,rect.y))
            # Pearly gates — golden pillars and arch near horizon
            gate_cx=rect.x+rect.width//2
            gate_y=horizon
            gold=(255,220,60); light_gold=(255,245,160); white=(245,245,235)
            pillar_w=10; pillar_h=52
            gap=38  # half-gap between pillars
            # Left pillar
            lp=gate_cx-gap-pillar_w//2
            pygame.draw.rect(surf,gold,(lp,gate_y-pillar_h,pillar_w,pillar_h))
            pygame.draw.rect(surf,light_gold,(lp+1,gate_y-pillar_h+2,3,pillar_h-4))
            pygame.draw.rect(surf,gold,(lp-4,gate_y-pillar_h-4,pillar_w+8,5))  # capital
            pygame.draw.rect(surf,gold,(lp-3,gate_y-3,pillar_w+6,4))           # base
            # Right pillar
            rp=gate_cx+gap-pillar_w//2
            pygame.draw.rect(surf,gold,(rp,gate_y-pillar_h,pillar_w,pillar_h))
            pygame.draw.rect(surf,light_gold,(rp+1,gate_y-pillar_h+2,3,pillar_h-4))
            pygame.draw.rect(surf,gold,(rp-4,gate_y-pillar_h-4,pillar_w+8,5))
            pygame.draw.rect(surf,gold,(rp-3,gate_y-3,pillar_w+6,4))
            # Arch over gate
            arch_cx=gate_cx; arch_cy=gate_y-pillar_h
            arch_rx=gap+pillar_w//2+4; arch_ry=24
            for a_deg in range(0,181,6):
                a=math.radians(a_deg)
                ax=int(arch_cx+arch_rx*math.cos(math.pi-a))
                ay=int(arch_cy-arch_ry*math.sin(a))
                pygame.draw.circle(surf,gold,(ax,ay),3)
            # Inner arch highlight
            for a_deg in range(10,171,8):
                a=math.radians(a_deg)
                ax=int(arch_cx+(arch_rx-3)*math.cos(math.pi-a))
                ay=int(arch_cy-(arch_ry-3)*math.sin(a))
                pygame.draw.circle(surf,light_gold,(ax,ay),1)
            # Gate cross-bar
            pygame.draw.rect(surf,gold,(lp,gate_y-pillar_h//2,rp-lp+pillar_w,5))
            # Shimmering gate fill (open gate glow)
            try:
                gs=pygame.Surface((gap*2-pillar_w,pillar_h//2),pygame.SRCALPHA)
                gs.fill((255,255,220,22))
                surf.blit(gs,(gate_cx-gap+pillar_w//2,gate_y-pillar_h//2))
            except Exception:
                pass

        elif zone_id==9:
            # 3 lava pools on the ground near horizon
            lava_cols=[(200,60,10),(220,80,10),(180,45,5)]
            pool_data=[(rect.x+60,horizon+8,50,12),(rect.x+170,horizon+6,65,14),
                       (rect.x+270,horizon+10,45,10)]
            for (px,py,pw,ph),lc in zip(pool_data,lava_cols):
                pygame.draw.ellipse(surf,lc,(px,py,pw,ph))
                pygame.draw.ellipse(surf,_sh(lc,40),(px+pw//4,py+2,pw//2,ph//2))
                pygame.draw.ellipse(surf,(255,120,20),(px,py,pw,ph),1)

        elif zone_id==10:
            # Sweeping searchlight beams across city sky
            t_s=int(self._time*3)
            for i,(ox,speed) in enumerate([(60,0.4),(180,0.7),(280,0.55)]):
                angle=math.sin(self._time*speed+i*2.1)*0.55
                bx=rect.x+ox; by=horizon
                ex=int(bx+math.sin(angle)*sky_h*1.2)
                ey=rect.y+4
                beam=pygame.Surface((rect.width,sky_h),pygame.SRCALPHA)
                pts=[(bx-rect.x-6,sky_h),(bx-rect.x+6,sky_h),
                     (ex-rect.x+22,0),(ex-rect.x-22,0)]
                pygame.draw.polygon(beam,(200,230,255,18),pts)
                surf.blit(beam,(rect.x,rect.y))
            # Occasional lightning flash in upper sky
            rng10=random.Random(t_s+zone_id*7)
            if rng10.random()<0.08:
                lx=rect.x+rng10.randint(20,rect.width-20)
                for seg in range(4):
                    y1=rect.y+seg*sky_h//4
                    y2=rect.y+(seg+1)*sky_h//4
                    lx2=lx+rng10.randint(-12,12)
                    pygame.draw.line(surf,(200,220,255),(lx,y1),(lx2,y2),1)
                    lx=lx2
            # Impact flashes near ground (battle explosions)
            rng10b=random.Random(t_s//4+zone_id*13)
            if rng10b.random()<0.25:
                fx=rect.x+rng10b.randint(30,rect.width-30)
                fy=horizon+rng10b.randint(10,40)
                pygame.draw.circle(surf,(255,220,80),(fx,fy),rng10b.randint(4,10))
                pygame.draw.circle(surf,(255,160,20),(fx,fy),rng10b.randint(2,5))

    # ── City parallax (tinted for zones) ─────────────────────────────────────
    def _draw_city_tinted(self,surf,rect,sky_h,horizon,sky_top,zone_id):
        """Draw city parallax with a zone-appropriate tint."""
        # Blend factor darkens city toward sky color to give depth
        amb=0.65
        speeds=[0.07,0.17,0.33]
        base_cols=[(172,178,190),(140,146,160),(108,114,130)]
        scales=[0.48,0.65,0.82]
        wrap=rect.width+220

        # Compute tint shift per zone
        tints={
            2:(150,130,100),3:(40,55,85),4:(160,150,110),
            5:(40,45,60),  6:(70,35,90),7:(140,100,50),
            8:(200,195,170),9:(60,25,20),10:(55,40,100),
        }
        zone_tint=tints.get(zone_id,(120,130,140))

        for li,(bldgs,bc,spd,sc) in enumerate(
                zip(self._city,base_cols,speeds,scales)):
            col=tuple(max(8,int((v*0.4+zone_tint[i]*0.6)*amb))
                      for i,v in enumerate(bc))
            off=(self._par_x*spd)%wrap
            for bx,bw,bh in bldgs:
                sx=rect.x+int((bx-off)%wrap)-100
                sh=int(bh*sc); sw=max(4,int(bw*sc)); sy=horizon-sh
                pygame.draw.rect(surf,col,(sx,sy,sw,sh+2))

    # ── Sky ───────────────────────────────────────────────────────────────────
    def _draw_sky(self,surf,rect,sky_h,st):
        tp,bt=st['sky_top'],st['sky_bot']
        tod=st['tod']

        # Horizon glow strength + colour
        if 0.22 <= tod <= 0.33:
            _gs = max(0.0, 1.0 - abs(tod - 0.275) * 9)
            _gc = (255, 135, 38)
        elif 0.66 <= tod <= 0.78:
            _gs = max(0.0, 1.0 - abs(tod - 0.72) * 9)
            _gc = (255, 100, 28)
        elif 0.33 < tod < 0.66:
            _gs = 0.13
            _gc = (255, 210, 130)
        else:
            _gs = 0.0
            _gc = (0, 0, 0)

        for i in range(sky_h):
            t = i / max(1, sky_h)
            col = _lc(tp, bt, t)
            if _gs > 0.01 and t > 0.68:
                gt = (t - 0.68) / 0.32
                col = _lc(col, _gc, gt * _gs * 0.65)
            pygame.draw.line(surf, col, (rect.x, rect.y+i), (rect.x+rect.width, rect.y+i))

        # Clouds (day only, fades at dawn/dusk)
        if 0.30 <= tod <= 0.70:
            cf = 1.0
            if tod < 0.36: cf = (tod - 0.30) / 0.06
            elif tod > 0.64: cf = (0.70 - tod) / 0.06
            for xf, yf, spd, csurf in self._cloud_data:
                cw = csurf.get_width()
                cx = int((xf*(rect.width+cw) - self._par_x*spd*0.28) % (rect.width+cw)) - cw
                cy = rect.y + int(yf * sky_h)
                csurf.set_alpha(int(cf * 255))
                surf.blit(csurf, (rect.x + cx, cy))

        is_night=st['is_night']
        # Stars
        if tod<0.26 or tod>0.80:
            bright=1.0 if(tod<0.21 or tod>0.84) else \
                   min(1.0,(tod-0.80)/0.04) if tod>0.80 else min(1.0,(0.26-tod)/0.05)
            for xf,yf in _STARS:
                sx=rect.x+int(xf*rect.width); sy=rect.y+int(yf*sky_h)
                a=int(bright*random.randint(160,255))
                pygame.draw.circle(surf,(a,a,a),(sx,sy),1)
        # Moon
        mp=_arc(tod,rect,sky_h,0.75,0.25)
        if mp:
            surf.blit(self._moon_glow, (mp[0]-25, mp[1]-25))
            pygame.draw.circle(surf,(228,232,210),mp,max(5,sky_h//9))
            pygame.draw.circle(surf,_lc(tp,bt,0.1),
                               (mp[0]-3,mp[1]-2),max(3,sky_h//14))
        # Sun
        sp=_arc(tod,rect,sky_h,0.25,0.75)
        if sp:
            surf.blit(self._sun_glow,  (sp[0]-40, sp[1]-40))
            surf.blit(self._sun_inner, (sp[0]-25, sp[1]-25))
            pygame.draw.circle(surf,(255,230,80),sp,max(6,sky_h//8))
            pygame.draw.circle(surf,(255,245,140),sp,max(3,sky_h//14))

    # ── City ──────────────────────────────────────────────────────────────────
    def _draw_city(self,surf,rect,sky_h,horizon,st):
        approach=min(1.0,math.log10(max(10,st.get('all_time_kp',10)))/14.0) \
                 if hasattr(st,'get') else 0.0
        is_night=st['is_night']; amb=st['ambient']
        speeds=[0.07,0.17,0.33]
        base_cols=[(172,178,190),(140,146,160),(108,114,130)]
        scales=[0.48,0.65,0.82]
        wrap=rect.width+220
        for li,(bldgs,bc,spd,sc) in enumerate(
                zip(self._city,base_cols,speeds,scales)):
            col=tuple(max(8,int(v*amb*0.75)) for v in bc)
            off=(self._par_x*spd)%wrap
            for bx,bw,bh in bldgs:
                sx=rect.x+int((bx-off)%wrap)-100
                sh=int(bh*sc); sw=max(4,int(bw*sc)); sy=horizon-sh
                pygame.draw.rect(surf,col,(sx,sy,sw,sh+2))
                if is_night and sw>8:
                    for wy in range(sy+4,sy+sh-6,8):
                        for wx in range(sx+3,sx+sw-5,7):
                            if(wx*3+wy*7)%10>4:
                                pygame.draw.rect(surf,(255,240,150),(wx,wy,3,4))
                elif li<2 and sh>22:
                    wc=_sh(col,28)
                    for wy in range(sy+4,sy+sh-7,9):
                        for wx in range(sx+3,sx+sw-5,7):
                            pygame.draw.rect(surf,wc,(wx,wy,3,4))
        pygame.draw.rect(surf,(158,182,140),(rect.x,horizon-3,rect.width,5))

    # ── Campus buildings ──────────────────────────────────────────────────────
    def _draw_campus(self,surf,rect,horizon,game,tile_base,st,zone_id=1):
        scale=max(0.42,1.0-game.prestige_count*0.07)
        tw=max(14,int(tile_base*scale)); th=max(7,tw//2)
        ox=rect.x+rect.width//2; oy=horizon+th+2
        amb=st['ambient']; is_night=st['is_night']
        holiday=st['holiday']; season=st['season']
        counts=game.building_counts

        entries=sorted(
            [(col,row,name,counts.get(name,0))
             for name,(col,row) in zip(_NAMES,_SLOTS)],
            key=lambda e:e[0]+e[1])

        # Zone tile color overrides
        _zone_tile={
            2: ((145,120,85),(128,105,70)),
            3: ((70,85,100),(60,75,90)),
            4: ((195,175,125),(178,158,108)),
            5: ((155,155,150),(138,138,133)),
            6: ((80,50,110),(68,40,95)),
            7: ((110,80,45),(95,68,35)),
            8: ((230,235,245),(215,222,235)),
            9: ((50,25,15),(40,18,10)),
            10:((90,80,125),(72,64,100)),
        }
        if zone_id!=1 and zone_id in _zone_tile:
            gc_b_base,gc_e_base=_zone_tile[zone_id]
            gc_b=tuple(max(8,int(v*amb)) for v in gc_b_base)
            gc_e=tuple(max(8,int(v*amb)) for v in gc_e_base)
        else:
            gc_b=tuple(max(8,int(v*amb)) for v in (145,188,118))
            gc_e=tuple(max(8,int(v*amb)) for v in (128,165,105))
            if season=='Winter':
                gc_b=tuple(max(8,int(v*amb)) for v in (195,210,195))
                gc_e=tuple(max(8,int(v*amb)) for v in (180,198,182))

        for col,row,name,cnt in entries:
            sx,sy=self._iso(col,row,tw,th,ox,oy)
            if sx+tw+4<rect.x or sx-tw-4>rect.right: continue
            if sy+th<rect.y-20 or sy>rect.bottom+160: continue
            _tile(surf,sx,sy,tw,th,gc_b if cnt>0 else gc_e)
            s=_stage(cnt)
            if s>0:
                bi=_NAMES.index(name)
                if zone_id==1:
                    tile=self._get_tile(name,tw)
                    if tile is not None:
                        tw_s,th_s=tile.get_size()
                        surf.blit(tile,(sx-tw_s//2, sy+th-th_s))
                    else:
                        bc=_BC.get(name,(150,150,150))
                        bc=tuple(max(10,int(v*amb)) for v in bc)
                        _box(surf,sx,sy,tw,th,_bh(s,tw),bc,s,is_night,bi,holiday,season)
                else:
                    self._draw_zone_tile(surf,sx,sy,tw,th,s,zone_id,amb,is_night,bi,holiday,season)

        # Seasonal props — zone 1 only (decorations make no sense in space/ruins/etc.)
        if zone_id == 1:
            self._draw_props(surf,rect,horizon,st,tw,th,ox,oy,game)

    def _draw_props(self,surf,rect,horizon,st,tw,th,ox,oy,game):
        holiday=st['holiday']; season=st['season']
        counts=game.building_counts

        def pos(col,row,dx=0,dy=0):
            sx,sy=self._iso(col,row,tw,th,ox,oy)
            return sx+dx, sy+th//2+dy

        if holiday=='midsummer':
            mx,my=pos(0,0,0,-8)
            _draw_midsommar(surf,mx,my,max(35,tw*2))

        if holiday in('christmas','christmas_eve'):
            tx,ty=pos(0,0,-tw//2-8,0)
            if self._xmas_sprite is not None:
                sz=max(28,int(tw*1.4))
                xsurf=pygame.transform.scale(self._xmas_sprite,(sz,sz))
                surf.blit(xsurf,(tx-sz//2,ty-sz))
            else:
                _draw_xmas_tree(surf,tx,ty,max(28,int(tw*1.4)))

        if holiday=='halloween':
            rng=random.Random(42)
            for col,row in[(0,0),(1,0),(0,1)]:
                if counts.get(_NAMES[_SLOTS.index((col,row))],0)>0:
                    px,py=pos(col,row,rng.randint(-tw//3,tw//3),
                              rng.randint(0,6))
                    _draw_pumpkin(surf,px,py,max(5,tw//7))

        if holiday=='valentine':
            rng=random.Random(int(self._time*0.5))
            for col,row in[(0,0),(1,0),(0,-1)]:
                hx,hy=pos(col,row,rng.randint(-tw//2,tw//2),
                          rng.randint(-tw,0))
                _draw_heart(surf,hx,hy,max(5,tw//6))

        if holiday=='easter':
            rng=random.Random(99)
            ecols=[(220,180,230),(230,220,160),(180,220,200),(230,190,210)]
            for i,(col,row) in enumerate([(0,0),(1,0),(0,1),(-1,0),(0,-1)]):
                if counts.get(_NAMES[_SLOTS.index((col,row))],0)>0:
                    ex,ey=pos(col,row,rng.randint(-tw//2,tw//2),0)
                    _draw_egg(surf,ex,ey,ecols[i%len(ecols)])

        if season=='Autumn':
            rng=random.Random(77)
            for col,row in _SLOTS[:6]:
                if counts.get(_NAMES[_SLOTS.index((col,row))],0)>0:
                    lx,ly=pos(col,row,rng.randint(-tw,tw),4)
                    _draw_leaf_pile(surf,lx,ly,rng)

    # ── Snow & fireworks ──────────────────────────────────────────────────────
    def _draw_snow(self,surf,rect,st):
        season=st['season']; holiday=st['holiday']
        if season!='Winter' and holiday not in('christmas','christmas_eve'):
            return
        for xf,y,_ in self._snow:
            sx=rect.x+int(xf*rect.width); sy=rect.y+int(y)
            if rect.y<=sy<=rect.bottom:
                pygame.draw.circle(surf,(225,238,252),(sx,sy),1)

    def _draw_fw(self,surf,rect,st):
        if st['holiday']!='new_year_eve': return
        for f in self._fw: f.draw(surf)

    # ── Overlay (date / time / season) ───────────────────────────────────────
    def _draw_overlay(self,surf,rect,st,tile_base):
        if tile_base<50: return   # skip on mini view
        ampm='AM' if st['hour']<12 else 'PM'
        h12=st['hour']%12 or 12
        text=(f"Year {st['year']}  ·  {_MON[st['month']]} {st['day']}"
              f"  ·  {st['season']}  ·  {h12}:{st['minute']:02d} {ampm}")
        try:
            font=pygame.font.SysFont("DejaVu Sans",13)
        except Exception:
            font=pygame.font.Font(None,14)
        ts=font.render(text,True,(220,230,245))
        pad=6
        bx=rect.right-ts.get_width()-pad*2-4
        by=rect.y+4
        bg=pygame.Surface((ts.get_width()+pad*2,ts.get_height()+pad),pygame.SRCALPHA)
        bg.fill((0,0,0,120))
        surf.blit(bg,(bx,by))
        surf.blit(ts,(bx+pad,by+pad//2))

        # Holiday label
        if st['holiday']:
            labels={'new_year':'🎆 New Year!','valentine':'💛 Valentine\'s Day',
                    'easter':'🐣 Easter','midsummer':'🌿 Midsommar',
                    'halloween':'🎃 Halloween','christmas':'🎄 Christmas',
                    'christmas_eve':'🎄 Christmas Eve','new_year_eve':'🎆 New Year\'s Eve'}
            lbl=labels.get(st['holiday'],'')
            if lbl:
                hs=font.render(lbl,True,(255,230,80))
                hbx=rect.x+4; hby=rect.y+4
                hbg=pygame.Surface((hs.get_width()+pad*2,hs.get_height()+pad),pygame.SRCALPHA)
                hbg.fill((0,0,0,120))
                surf.blit(hbg,(hbx,hby))
                surf.blit(hs,(hbx+pad,hby+pad//2))

    # ── Building tile sprite helper ───────────────────────────────────────────
    def _get_tile(self, name: str, tw: int):
        """Return a scaled building tile surface, or None if not available."""
        key = (name, tw)
        cached = self._tile_cache.get(key)
        if cached is not None:
            return cached
        orig = self._building_tiles.get(name)
        if orig is None:
            return None
        ow, oh = orig.get_size()
        scale = tw / ow
        nw = max(1, int(ow * scale))
        nh = max(1, int(oh * scale))
        scaled = pygame.transform.smoothscale(orig, (nw, nh))
        self._tile_cache[key] = scaled
        return scaled

    # ── Zone-specific building tile drawing ───────────────────────────────────
    def _draw_zone_tile(self,surf,cx,cy,tw,th,stage,zone_id,amb,is_night,bi,holiday,season):
        """Draw a zone-appropriate building at iso position (cx,cy).
        Falls through to standard _box for zone 1."""
        h=_bh(stage,tw)
        if h<=0:
            return

        if zone_id==1:
            # Standard — not called for zone 1 (handled by existing code)
            pass

        elif zone_id==2:
            # Crumbled brick towers — shorter, brown/grey, jagged tops
            col=(140,120,90); shadow=(100,85,65); top=(160,140,110)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            # Reduce height to look crumbled (80%)
            bh=max(4,int(h*0.80))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            # Jagged top (broken battlements) — small random notches
            rng=random.Random(bi*31+stage)
            top_pts=[tl,tt,tr]
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Draw crack lines on the right face
            if tw>=16:
                for _ in range(2):
                    sx=cx+rng.randint(2,max(3,hw-2)); sy=cy-bh+rng.randint(2,max(3,bh-2))
                    pygame.draw.line(surf,_sh(col,-30),(sx,sy),(sx+rng.randint(-3,3),sy+rng.randint(4,10)),1)
            # Battlement notches on top
            for nx in range(int(tl[0]),int(tr[0]),max(3,tw//5)):
                pygame.draw.rect(surf,_sh(shadow,-10),(nx,int(tt[1])-4,max(2,tw//8),4))

        elif zone_id==3:
            # Tall glass towers with neon accents
            col=(50,60,80); shadow=(35,45,65); top=(70,80,100)
            neon=(0,200,255)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            # Extra tall: multiply height by 1.3
            bh=max(6,int(h*1.30))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Neon vertical stripe on right face
            if tw>=14:
                mid_x=(cx+cx+hw)//2; mid_y_top=cy+hh-bh; mid_y_bot=cy+hh
                neon_a=tuple(max(8,int(v*amb)) for v in neon)
                pygame.draw.line(surf,neon_a,(mid_x,int(mid_y_top)+2),(mid_x,int(mid_y_bot)-2),2)
            # Neon stripe on left face
            if tw>=16:
                lmid_x=(cx+cx-hw)//2;
                pygame.draw.line(surf,neon_a,(lmid_x,int(cy+hh-bh)+2),(lmid_x,int(cy+hh)-2),2)

        elif zone_id==4:
            # White marble Greek temples with columns and pediment
            col=(240,238,230); shadow=(220,218,210); top=(255,253,248)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            bh=max(4,int(h*0.90))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # 3 column pillars on right face
            if tw>=16:
                face_top_y=int(cy+hh-bh); face_bot_y=int(cy+hh)
                face_left_x=int(cx); face_right_x=int(cx+hw)
                col_w=max(1,tw//10)
                for ci in range(3):
                    t_frac=(ci+0.5)/3.0
                    cpx=int(face_left_x+t_frac*(face_right_x-face_left_x))
                    pygame.draw.line(surf,_sh(col,-20),(cpx,face_top_y),(cpx,face_bot_y),col_w)
            # Triangular pediment on top face
            if tw>=18:
                ped_mid=(int(tt[0]),int(tt[1])-max(3,tw//6))
                pygame.draw.polygon(surf,_sh(col,10),[
                    (int(tl[0]),int(tl[1])),
                    (int(tr[0]),int(tr[1])),
                    ped_mid
                ])

        elif zone_id==5:
            # Moon base structures: domes, habitat tubes, antennae
            hw,hh=tw//2,th//2
            bh=max(4,int(h*0.70))
            silver=tuple(max(8,int(v*amb)) for v in (195,200,210))
            dark=tuple(max(8,int(v*amb)) for v in (140,145,155))
            glass=tuple(max(8,int(v*amb)) for v in (100,180,220))
            struct_type=bi%3   # 0=dome, 1=habitat module, 2=antenna
            if struct_type==0:
                # Geodesic dome sitting on isometric base
                dom_r=max(5,min(hw,bh//2+2))
                dom_cx=cx; dom_cy=cy-dom_r+4
                pygame.draw.circle(surf,silver,(dom_cx,dom_cy),dom_r)
                pygame.draw.circle(surf,dark,(dom_cx,dom_cy),dom_r,1)
                # Grid lines
                if dom_r>=7:
                    for a in range(0,180,45):
                        r2=math.radians(a)
                        pygame.draw.line(surf,dark,
                            (int(dom_cx+math.cos(r2)*dom_r),int(dom_cy+math.sin(r2)*dom_r)),
                            (int(dom_cx-math.cos(r2)*dom_r),int(dom_cy-math.sin(r2)*dom_r)),1)
                    pygame.draw.ellipse(surf,dark,(dom_cx-dom_r,dom_cy-dom_r//3,dom_r*2,dom_r//3*2),1)
                # Glass window highlight
                pygame.draw.circle(surf,glass,(dom_cx+dom_r//4,dom_cy-dom_r//4),max(2,dom_r//4))
                # Airlock base tube
                pygame.draw.rect(surf,dark,(dom_cx-3,dom_cy+dom_r-2,6,max(4,bh//4)))
            elif struct_type==1:
                # Rectangular habitat module
                mw=max(6,tw-4); mh=max(4,bh//2)
                mx=cx-mw//2; my=cy-mh-2
                pygame.draw.rect(surf,silver,(mx,my,mw,mh),border_radius=3)
                pygame.draw.rect(surf,dark,(mx,my,mw,mh),1,border_radius=3)
                # Porthole windows
                if mw>=10:
                    for wi in range(min(3,mw//8)):
                        wx=mx+4+wi*(mw//3); wy=my+mh//3
                        pygame.draw.circle(surf,glass,(wx,wy),max(2,mw//10))
                # Solar panel arm
                pygame.draw.line(surf,dark,(cx,my+mh//2),(cx+hw+4,my+mh//2),1)
                pygame.draw.rect(surf,glass,(cx+hw+2,my+mh//2-3,max(4,tw//3),6))
            else:
                # Antenna tower with dish
                ath=max(8,bh)
                pygame.draw.line(surf,dark,(cx,cy-2),(cx,cy-ath),2)
                # Dish arc
                dish_y=cy-ath+4
                pygame.draw.arc(surf,silver,pygame.Rect(cx-max(4,hw//2),dish_y-2,
                    max(8,hw),max(5,ath//3)),0,math.pi,2)
                # Blinky light
                t_blink=int(self._time*2+bi)%3
                bcol=(255,60,60) if t_blink==0 else (80,80,80)
                pygame.draw.circle(surf,bcol,(cx,cy-ath),max(2,3))

        elif zone_id==6:
            # Crystal spires — tall, thin, jewel-like with pointed tops
            col=(200,100,220); shadow=(180,80,200); top=(240,140,255)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            # Very tall and thin
            bh=max(8,int(h*1.5))
            thin_hw=max(3,hw//2)  # thinner than normal
            # Use thin isometric coords
            tt=(cx,cy-bh);tr=(cx+thin_hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-thin_hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-thin_hw,cy+hh);gr=(cx+thin_hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            # Pointed tip instead of flat top
            tip=(cx,int(tt[1])-max(4,tw//3))
            pygame.draw.polygon(surf,top,[tl,tr,tip])

        elif zone_id==7:
            # Stone huts — low, squat shapes with arc doorway
            col=(130,110,85); shadow=(110,90,65); top=(150,130,100)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            # Squat: 65% height
            bh=max(3,int(h*0.65))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Circular arc doorway on right face
            if tw>=14 and bh>=8:
                face_mid_x=(cx+cx+hw)//2
                door_y=int(cy+hh)-2
                arc_r=max(3,min(bh//3,hw//3))
                pygame.draw.arc(surf,_sh(shadow,-20),
                    pygame.Rect(face_mid_x-arc_r,door_y-arc_r*2,arc_r*2,arc_r*2),
                    0,math.pi,2)

        elif zone_id==8:
            # White/gold cloud palaces with arched windows
            col=(255,255,248); shadow=(240,235,210); top=(255,255,255)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            bh=max(4,int(h*0.95))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Arched window on right face
            if tw>=16 and bh>=12:
                face_mid_x=(cx+cx+hw)//2
                win_y=int(cy+hh-bh//2)
                win_r=max(3,min(bh//5,hw//4))
                gold=tuple(max(8,int(v*amb)) for v in (218,165,30))
                pygame.draw.arc(surf,gold,
                    pygame.Rect(face_mid_x-win_r,win_y-win_r*2,win_r*2,win_r*2),
                    0,math.pi,2)
                pygame.draw.rect(surf,gold,(face_mid_x-win_r,win_y-win_r,win_r*2,win_r))

        elif zone_id==9:
            # Dark basalt obsidian towers with lava cracks
            col=(40,20,15); shadow=(25,10,5); top=(80,30,20)
            col=tuple(max(8,int(v*amb)) for v in col)
            shadow=tuple(max(8,int(v*amb)) for v in shadow)
            top=tuple(max(8,int(v*amb)) for v in top)
            hw,hh=tw//2,th//2
            bh=max(4,int(h*1.10))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Glowing orange crack lines on right face
            if tw>=14 and bh>=8:
                lava_col=(200,80,10)
                rng=random.Random(bi*17+stage)
                num_cracks=2 if tw<20 else 3
                for _ in range(num_cracks):
                    sx=cx+rng.randint(2,max(3,hw-2)); sy=cy+hh-bh+rng.randint(2,max(3,bh-2))
                    pygame.draw.line(surf,lava_col,(sx,sy),(sx+rng.randint(-2,2),sy+rng.randint(3,8)),1)
        elif zone_id==10:
            # Tall urban hero towers with neon-blue accent stripes
            col=tuple(max(8,int(v*amb)) for v in (50,40,140))
            shadow=tuple(max(8,int(v*amb)) for v in (35,28,110))
            top=tuple(max(8,int(v*amb)) for v in (80,65,190))
            hw,hh=tw//2,th//2
            bh=max(6,int(h*1.25))
            tt=(cx,cy-bh);tr=(cx+hw,cy+hh-bh);tb=(cx,cy+th-bh);tl=(cx-hw,cy+hh-bh)
            gb=(cx,cy+th);gl=(cx-hw,cy+hh);gr=(cx+hw,cy+hh)
            pygame.draw.polygon(surf,shadow,[gl,gb,tb,tl])
            pygame.draw.polygon(surf,col,[gr,gb,tb,tr])
            pygame.draw.polygon(surf,top,[tt,tr,tb,tl])
            # Neon accent stripe on right face
            if tw>=14:
                accent=tuple(max(8,int(v*amb)) for v in (100,180,255))
                mid_x=(cx+cx+hw)//2
                pygame.draw.line(surf,accent,(mid_x,int(cy+hh-bh)+2),(mid_x,int(cy+hh)-2),2)
            # "H" hero symbol on top face for larger advanced buildings
            if tw>=20 and stage>=3:
                hx,hy=int(tt[0]),int(tt[1])+2
                gold=(255,220,60)
                pygame.draw.line(surf,gold,(hx-3,hy),(hx-3,hy+5),1)
                pygame.draw.line(surf,gold,(hx+3,hy),(hx+3,hy+5),1)
                pygame.draw.line(surf,gold,(hx-3,hy+2),(hx+3,hy+2),1)

    # ── Moon Colony special objects ────────────────────────────────────────────
    def _draw_moon_objects(self,surf,rect):
        """Draw animated Earth and Sun orbs for zone 5 (Moon Colony)."""
        t=self._time
        cx=rect.x+rect.width//2
        # Sky region: from rect.y to horizon (~rect.y + sky_h). Keep objects in upper 2/3 of sky.
        sky_top=rect.y+8

        # --- Sun: tiny, very high upper-left (far from moon) ---
        sun_angle=t*0.07
        sun_r=8
        sun_ox=rect.x+rect.width//5; sun_oy=sky_top+20
        sun_orb_r=14
        sx=int(sun_ox+math.cos(sun_angle)*sun_orb_r)
        sy=int(sun_oy+math.sin(sun_angle)*sun_orb_r*0.35)
        # Glow halo
        try:
            glow=pygame.Surface((sun_r*6,sun_r*6),pygame.SRCALPHA)
            pygame.draw.circle(glow,(255,240,100,50),(sun_r*3,sun_r*3),sun_r*3)
            pygame.draw.circle(glow,(255,255,180,35),(sun_r*3,sun_r*3),sun_r*2)
            surf.blit(glow,(sx-sun_r*3,sy-sun_r*3))
        except Exception:
            pass
        pygame.draw.circle(surf,(255,240,100),(sx,sy),sun_r)
        pygame.draw.circle(surf,(255,255,200),(sx,sy),sun_r//2)

        # --- Earth: medium, right-of-center, high in sky ---
        earth_angle=t*0.20+1.2
        earth_r=30
        earth_ox=cx+rect.width//6; earth_oy=sky_top+36
        earth_orb_r=12
        ex=int(earth_ox+math.cos(earth_angle)*earth_orb_r)
        ey=int(earth_oy+math.sin(earth_angle)*earth_orb_r*0.4)
        # Ocean base
        pygame.draw.circle(surf,(30,80,180),(ex,ey),earth_r)
        # Green continent patches
        green=(60,140,60)
        patches=[
            [(ex-11,ey-10),(ex-4,ey-15),(ex+5,ey-11),(ex+7,ey-4),(ex-2,ey-2)],
            [(ex+7,ey+2),(ex+14,ey-2),(ex+17,ey+6),(ex+12,ey+11),(ex+4,ey+9)],
            [(ex-15,ey+5),(ex-9,ey+2),(ex-6,ey+10),(ex-12,ey+14),(ex-18,ey+11)],
        ]
        for patch in patches:
            try:
                ps=pygame.Surface((earth_r*2+4,earth_r*2+4),pygame.SRCALPHA)
                shifted=[(p[0]-ex+earth_r+2,p[1]-ey+earth_r+2) for p in patch]
                pygame.draw.polygon(ps,(*green,220),shifted)
                surf.blit(ps,(ex-earth_r-2,ey-earth_r-2))
            except Exception:
                pygame.draw.polygon(surf,green,patch)
        # Cloud arc swirls
        cloud_angle=t*0.08
        for i in range(3):
            a=cloud_angle+i*2.1
            bx=int(ex+math.cos(a)*earth_r*0.6)
            by=int(ey+math.sin(a)*earth_r*0.45)
            try:
                cs=pygame.Surface((14,5),pygame.SRCALPHA)
                pygame.draw.ellipse(cs,(255,255,255,130),(0,0,14,5))
                surf.blit(cs,(bx-7,by-2))
            except Exception:
                pass
        # Earth outline
        pygame.draw.circle(surf,(20,50,130),(ex,ey),earth_r,1)

    @staticmethod
    def _iso(col,row,tw,th,ox,oy):
        return (ox+(col-row)*tw//2, oy+(col+row)*th//2)
