#!/usr/bin/env python2.7
import os, sys, datetime, grads, color_table
period = 6
os.umask(0002)
fmt = "%Y%m%d_%H%M"; fmt2="%Y-%m-%d_%H00"; fmt3="%Hz%d%b%Y"; fmt4="%Y%m";
fmt5 = "%Y%m%d"

GRADS = "/opt/grads-2.1.0.oga.1/Classic/bin/grads -bp"
ga = grads.GaNum(Bin=GRADS,Echo=False,Window="None")
GASHP = "/opt/grads-2.1.0.oga.1/Classic/data"
pngquant = "/opt/grads-2.0.1.oga.1/Contents/Linux/Versions/2.0.1.oga.1/x86_64/pngquant"

script_path = os.path.realpath(__file__)
workdir = os.path.dirname(script_path)

##### inputdir #####
GT_dir = "/nas_study/NWPdata/GTctl/YYYYMM"
BC_dir = "/nas_study/NWPdata/BC/YYYYMM"
#BCw_dir = "/users2/Jing/work.GFE/BC/data"
GFE_dir = "/nas_study/NWPdata/GFE/YYYYMM"

##### outputdir #####
ATmax_dir = "/nas_study/Jing/ApparentTemp/ATmax/YYYYMM"
ATmin_dir = "/nas_study/Jing/ApparentTemp/ATmin/YYYYMM"
#png_dir = "/nas_study/Jing/BC/YYYYMM"
png_dir = "/nas_qpf/YYYYMM"


mdl = ["GT","GFE","NCEP","TWRF","WRFD","EC","JMA"] if not "-m" in sys.argv else [sys.argv[sys.argv.index("-m")+1]]
mdlname = {"GT":"GT","GFE":"GFE","NCEP":"NCEP","TWRF":"M05","JMA":"JMA","WRFD":"M04","EC":"ECMWF"}

now=datetime.datetime.utcnow()

def main():
  os.chdir(workdir)

  dt = 0.25 if not "-dt" in sys.argv else float(sys.argv[sys.argv.index("-dt")+1])
  sdt = datetime.datetime(now.year,now.month,now.day,now.hour-now.hour%period) if not "-now" in sys.argv else datetime.datetime.strptime(sys.argv[sys.argv.index("-now")+1],fmt)
  edt = sdt - datetime.timedelta(days = dt)
  edt = edt - datetime.timedelta(hours = edt.hour%period)

  while edt <= sdt :
    filetime = edt.strftime(fmt)
    print filetime

    pdir = png_dir.replace("YYYYMM",edt.strftime(fmt4))
    if not os.path.exists(pdir) : os.makedirs(pdir)


    if "GT" in mdl : draw_GT_MXMN(edt,pdir)
    if "GFE" in mdl : draw_GFE_MXMN(edt,pdir)
    draw_BC_MXMN(edt,pdir)

    edt = edt + datetime.timedelta(hours = period)

#====================================================================
def draw_GT_MXMN(edt,pdir) :
  t0d = 273.15

  #===== GT max =====
  if edt.hour == 12 :
    sfcst, fcst = edt - datetime.timedelta(hours = 12), edt

    #===== GT Tmax =====
    ga("reinit")
    ctl = "%s/%sT.ctl"%(GT_dir.replace("YYYYMM",edt.strftime(fmt4)),edt.strftime("%Y%m%d_0000"))
    if os.path.exists(ctl) :
      ga("open %s"%(ctl))
    else :
      return()

    getMask(ga)

    ppdir = "%s/GT/Tmax"%(pdir)
    if not os.path.exists(ppdir) : os.makedirs(ppdir)

    title = "%s max-T : %s"%("GT",fcst.strftime(fmt))
    pngname = "%s.png"%(fcst.strftime(fmt))
    ga("define aa = max(TMPsfc.1,time=%s,time=%s) - %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3),t0d))
    ga("define aa = lterp(aa,mask)")
    drawpic(ppdir,pngname,title)

    #===== GT ATmax =====
    ga("reinit")
    ctl = "%s/%sAT.ctl"%(GT_dir.replace("YYYYMM",edt.strftime(fmt4)),edt.strftime("%Y%m%d_0000"))
    if os.path.exists(ctl) :
      ga("open %s"%(ctl))
    else :
      return()

    getMask(ga)

    ppdir = "%s/GT/ATmax"%(pdir)
    if not os.path.exists(ppdir) : os.makedirs(ppdir)

    title = "%s max-AT : %s"%("GT",fcst.strftime(fmt))
    pngname = "%s.png"%(fcst.strftime(fmt))
    ga("define aa = max(APTMPsfc.1,time=%s,time=%s) - %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3),t0d))
    ga("define aa = lterp(aa,mask)")
    drawpic(ppdir,pngname,title)

  #===== GT min =====
  if edt.hour == 00 :
    sfcst, fcst = edt - datetime.timedelta(hours = 12), edt
    sdt = edt - datetime.timedelta(days = 1)

    #===== GT Tmin =====
    ga("reinit")
    ctl = "%s/%sT.ctl"%(GT_dir.replace("YYYYMM",sdt.strftime(fmt4)),sdt.strftime("%Y%m%d_0000"))
    if os.path.exists(ctl) :
      ga("open %s"%(ctl))
    else :
      return()

    getMask(ga)

    ppdir = "%s/GT/Tmin"%(pdir)
    if not os.path.exists(ppdir) : os.makedirs(ppdir)

    title = "%s min-T : %s"%("GT",fcst.strftime(fmt))
    pngname = "%s.png"%(fcst.strftime(fmt))
    ga("define aa = min(TMPsfc.1,time=%s,time=%s) - %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3),t0d))
    ga("define aa = lterp(aa,mask)")
    drawpic(ppdir,pngname,title)

    #===== GT ATmin =====
    ga("reinit")
    ctl = "%s/%sAT.ctl"%(GT_dir.replace("YYYYMM",sdt.strftime(fmt4)),sdt.strftime("%Y%m%d_0000"))
    if os.path.exists(ctl) :
      ga("open %s"%(ctl))
    else :
      return()

    getMask(ga)

    ppdir = "%s/GT/ATmin"%(pdir)
    if not os.path.exists(ppdir) : os.makedirs(ppdir)

    title = "%s min-AT : %s"%("GT",fcst.strftime(fmt))
    pngname = "%s.png"%(fcst.strftime(fmt))
    ga("define aa = min(APTMPsfc.1,time=%s,time=%s) - %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3),t0d))
    ga("define aa = lterp(aa,mask)")
    drawpic(ppdir,pngname,title)

#====================================================================
def draw_GFE_MXMN(edt,pdir) :
  t0d = 273.15

  if (now-edt).total_seconds()/3600. < 3 : print "GFE not in time"; return()

  ga("reinit")
  ctl = "%s/%s.ctl"%(GFE_dir.replace("YYYYMM",edt.strftime(fmt4)),edt.strftime(fmt))
  if os.path.exists(ctl) :
    ga("open %s"%(ctl))
  else :
    return()

  getMask(ga)

  tf = 193
  efcst = edt + datetime.timedelta(days = 8) + datetime.timedelta(hours = 24 - edt.hour%24 - 3)
  for t in range(0,tf,3) :
    if t > 180 : continue
    fcst = edt + datetime.timedelta(hours = t)
    sfcst = fcst - datetime.timedelta(hours = 12)
    if sfcst < edt : continue
    if fcst > efcst : continue

    #===== max =====
    if fcst.hour == 12 :
      ppdir = "%s/GFE/Tmax"%(pdir)
      if not os.path.exists(ppdir) : os.makedirs(ppdir)

      ga("clear"); ga("reset")
      title = "%s max-T : %s+(%d-%d)"%("GFE",edt.strftime(fmt),t-12,t)
      pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

      ga("define aa = mxt.1(time=%s)-%s"%(fcst.strftime(fmt3),t0d))
      ga("define aa = lterp(aa,mask)")

      drawpic(ppdir,pngname,title)

      #==AT==================
      ppdir = "%s/GFE/ATmax"%(pdir)
      if not os.path.exists(ppdir) : os.makedirs(ppdir)

      ga("clear"); ga("reset")
      title = "%s max-AT : %s+(%d-%d)"%("GFE",edt.strftime(fmt),t-12,t)
      pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

      ga("set time %s %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
      ga("define tt = t.1 -%s"%t0d)
      ga("define e = rh.1/100 * 6.105 * exp(17.27*tt/(237.7+tt))")
      ga("define atemp = 1.04*tt + 0.2*e -0.65*ws.1 -2.7")
      ga("define aa = max(atemp,time=%s,time=%s)"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
      ga("define aa = lterp(aa,mask)")

      ga("set time %s"%fcst.strftime(fmt3))
      drawpic(ppdir,pngname,title)


    #===== min =====
    if fcst.hour == 00 :
      ppdir = "%s/GFE/Tmin"%(pdir)
      if not os.path.exists(ppdir) : os.makedirs(ppdir)

      ga("clear"); ga("reset")
      title = "%s min-T : %s+(%d-%d)"%("GFE",edt.strftime(fmt),t-12,t)
      pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

      ga("define aa = mnt.1(time=%s)-%s"%(fcst.strftime(fmt3),t0d))
      ga("define aa = lterp(aa,mask)")

      drawpic(ppdir,pngname,title)

      #====================
      ppdir = "%s/GFE/ATmin"%(pdir)
      if not os.path.exists(ppdir) : os.makedirs(ppdir)

      ga("clear"); ga("reset")
      title = "%s min-AT : %s+(%d-%d)"%("GFE",edt.strftime(fmt),t-12,t)
      pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

      ga("set time %s %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
      ga("define tt = t.1 -%s"%t0d)
      ga("define e = rh.1/100 * 6.105 * exp(17.27*tt/(237.7+tt))")
      ga("define atemp = 1.04*tt + 0.2*e -0.65*ws.1 -2.7")

      ga("define aa = min(atemp,time=%s,time=%s)"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
      ga("define aa = lterp(aa,mask)")

      ga("set time %s"%fcst.strftime(fmt3))
      drawpic(ppdir,pngname,title)


#====================================================================
def draw_BC_MXMN(edt,pdir) :
  if (now-edt).total_seconds()/3600. < 8 : print "BC not in time"; return()

  t0d = 273.15

  ga("reinit")
  ctl = "%s/%s.ctl"%(BC_dir.replace("YYYYMM",edt.strftime(fmt4)),edt.strftime(fmt))
  ctlw = "%s/%sw.ctl"%(BC_dir.replace("YYYYMM",edt.strftime(fmt4)),edt.strftime(fmt))
  if os.path.exists(ctl) :
    ga("open %s"%(ctl))
    ga("open %s"%(ctlw))
  else :
    return()

#  ga("open %s/topo.ctl"%workdir)
#  ga("define mask=topo.3(t=1)-1.e-5")

  ga("open %s/Town.ctl"%workdir)
  ga("define mask=shp.3(t=1)")

  for m in mdl :
    if m == "GFE"  : continue
    if m == "GT"   : continue

    if "EC" in m and edt.hour%12 != 0 : continue

    tf = 241; p6 = 241
    if m == "JMA"  : p6 = 120; ens = 3; tf = 132
    if m == "NCEP" : p6 = 120; ens = 4
    if m == "EC"   : p6 =  96; ens = 5
    if m == "WRFD" : p6 =  84; ens = 6; tf = 121
    if m == "TWRF" : p6 =  84; ens = 7; tf = 121

    for t in range(0,tf,3) :
      fcst = edt + datetime.timedelta(hours = t)
      sfcst = fcst - datetime.timedelta(hours = 12)

      #===== max =====
      if fcst.hour == 12 :
        ppdir = "%s/%s/Tmax"%(pdir,mdlname[m])
        if not os.path.exists(ppdir) : os.makedirs(ppdir)

        #==Tmax==============
        ga("clear"); ga("reset")
        title = "%s max-T : %s+(%d-%d)"%(mdlname[m],edt.strftime(fmt),t-12,t)
        pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

        ga("define aa = mxt.1(time = %s, e = %d) -%s"%(sfcst.strftime(fmt3),ens,t0d))
        ga("define aa = lterp(aa,mask)")

        drawpic(ppdir,pngname,title)


        #==ATmax==============
        ppdir = "%s/%s/ATmax"%(pdir,mdlname[m])
        if not os.path.exists(ppdir) : os.makedirs(ppdir)

        ga("clear"); ga("reset")
        title = "%s max-AT : %s+(%d-%d)"%(mdlname[m],edt.strftime(fmt),t-12,t)
        pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

        try :
          ga("set time %s %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
          ga("define tt = t.1(e=%d) -%s"%(ens,t0d))
          ga("define e = rh.2(e=%d)/100 * 6.105 * exp(17.27*tt/(237.7+tt))"%ens)
          ga("define atemp = 1.04*tt + 0.2*e -0.65*ws.2(e=%d) -2.7"%ens)
          ga("define aa = max(atemp,time=%s,time=%s)"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
          ga("define aa = lterp(aa,mask)")

          ga("set time %s"%fcst.strftime(fmt3))
          drawpic(ppdir,pngname,title)

        except :
          pass


      #===== min =====
      if fcst.hour == 00 :
        ppdir = "%s/%s/Tmin"%(pdir,mdlname[m])
        if not os.path.exists(ppdir) : os.makedirs(ppdir)

        ga("clear"); ga("reset")
        title = "%s min-T : %s+(%d-%d)"%(mdlname[m],edt.strftime(fmt),t-12,t)
        pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

        ga("define aa = mnt.1(time = %s, e=%d) -%s"%(sfcst.strftime(fmt3),ens,t0d))
        ga("define aa = lterp(aa,mask)")

        drawpic(ppdir,pngname,title)


        #====================
        ppdir = "%s/%s/ATmin"%(pdir,mdlname[m])
        if not os.path.exists(ppdir) : os.makedirs(ppdir)

        ga("clear"); ga("reset")
        title = "%s min-AT : %s+(%d-%d)"%(mdlname[m],edt.strftime(fmt),t-12,t)
        pngname = "%sf%03d.png"%(edt.strftime(fmt),t)

        try :
          ga("set time %s %s"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
          ga("define tt = t.1(e=%d) -%s"%(ens,t0d))
          ga("define e = rh.2(e=%d)/100 * 6.105 * exp(17.27*tt/(237.7+tt))"%ens)
          ga("define atemp = 1.04*tt + 0.2*e -0.65*ws.2(e=%d) -2.7"%ens)
          ga("define aa = min(atemp,time=%s,time=%s)"%(sfcst.strftime(fmt3),fcst.strftime(fmt3)))
          ga("define aa = lterp(aa,mask)")

          ga("set time %s"%fcst.strftime(fmt3))
          drawpic(ppdir,pngname,title)

        except :
          pass


#====================================================================
def drawpic(pngdir,pngname,title) :
  dims={"Taiwan":[(21.7,25.5,119.1,122.1),(0.7,8,0.7,10.3)],"Kimen":[(24.3,24.6,118.05,118.55),(1.2,2.7,6.5,7.7)],"Matsu":[(25.9,26.4,119.8,120.3),(1.2,2.7,8.0,9.6)]}

  for d in ["Taiwan","Kimen","Matsu"] :
    dim, parea = dims[d]
    if d == "Taiwan" :
      ga("set parea %f %f %f %f"%(tuple(parea)))
      ga("set lat %f %f"%(tuple(dim[:2])))
      ga("set lon %f %f"%(tuple(dim[2:])))

      ga("set mproj scaled"); ga("set grads off")
      #ga("set xlab off"); ga("set ylab off")
      ga("set mpdraw off"); ga("set gxout shade2")
      ga("set digsiz .11"); ga("set cthick 7")
      ga("set xlint 1"); ga("set xlopts 1 7 0.2"); ga("set ylint 1"); ga("set ylopts 1 7 0.2")

      color_table.colorT(ga)
      ga("define bb = maskout(aa,mask)")
      ga("d bb")
      ga("undefine bb")

      ga("set rgb 301 70 70 70")
      ga("set line 301 1 7")
#      ga("draw shp %s/2010_5City_lonlat"%GASHP)
      ga("draw shp %s/COUNTY_MOI_1060525"%workdir)
      ga("draw shp %s/Asia"%GASHP)

      ga("run cbarn.gs 0.65 1 8.1 3.7")
      ga("draw title %s"%title)

    else :
      ga("set parea %f %f %f %f"%(tuple(parea)))
      ga("set lat %f %f"%(tuple(dim[:2])))
      ga("set lon %f %f"%(tuple(dim[2:])))

      ga("set xlab off"); ga("set ylab off")

      color_table.colorT(ga)
#      ga("d aa")
      ga("define bb = maskout(aa,mask)")
      ga("d bb")
      ga("undefine bb")

      ga("set rgb 301 70 70 70")
      ga("set line 301 1 7")
      ga("draw shp %s/TOWN_MOI_1060831"%workdir)
#      ga("draw shp %s/Island"%GASHP)



  if pngdir != "" :
    try :
      png = "%s/%s"%(pngdir,pngname)
      print png
      #ga("printim %s x600 y750 white"%(png))
      ga("gxprint %s x600 y750 white"%(png))
      png_resize(png)

#      if os.path.exists(png) :
#        pngfs8 = png.split(".")[0] + "-fs8.png"
#        if os.path.exists(pngfs8) : os.system("rm -f %s"%pngfs8)
#        os.chdir(pngdir)
#        os.system("%s 256 %s"%(pngquant,pngname))
#        os.system("mv %s %s"%(pngfs8,pngname))
#        os.chdir(workdir)
    except :
      return()


#====================================================================
def getMask(ga):
#  ga("open %s/topo.ctl"%workdir)
#  ga("define mask=topo.2(t=1)-1.e-5")

  ga("open %s/Town.ctl"%workdir)
  ga("define mask=shp.2(t=1)")

#============================
def png_resize(png) :
  if os.path.exists(png) :
    pngfs8 = png.split(".")[0] + "-fs8.png"
    if os.path.exists(pngfs8) : os.system("rm -f %s"%pngfs8)
    os.system("%s 256 %s"%(pngquant,png))
    os.system("mv %s %s"%(pngfs8,png))

#====================================================================
if __name__ == "__main__" :
  main()

