#!/usr/bin/env python2.7
import os, datetime, sys, grads, numpy, math, color_table
import NWPpost_w as NWPpost
os.umask(0000)
h2s=60*60; ms2kts=1.943844; dd=0.1; skip=4; xres=600; yres=750
#periods=[168]
periods=[12,24,48,3,72,120,168,6] if not "-p" in sys.argv else [int(sys.argv[sys.argv.index("-p")+1])]
model="ECMWF" if not "-m" in sys.argv else sys.argv[sys.argv.index("-m")+1]
model_lag_hours= int(sys.argv(sys.argv.index("-lag")+1)) if "-lag" in sys.argv else 3 if model=="GFE" else 10 if model in ["FV3G","FV3N","TGFSN","TGFSG"] else 5
#updPrd=12 if model in ["ECMWF","FV3G","FV3N"] else  6
#updPrd=12 if model in ["FV3G","FV3N"] else  6
updPrd=6
now= datetime.datetime.strptime(sys.argv[sys.argv.index("-now")+1],"%Y%m%d%H") if "-now" in sys.argv else datetime.datetime.utcnow()-datetime.timedelta(hours=model_lag_hours)

script_path = os.path.realpath(__file__)
workDir = os.path.dirname(script_path)

outdir="/nas_qpf"
GrADS = "/opt/grads-2.1.0.oga.1/Classic/bin/grads -bp"
pngquant = "/opt/grads-2.0.1.oga.1/Contents/Linux/Versions/2.0.1.oga.1/x86_64/pngquant"



fmt="%Y%m%d_%H00"; fmt2="%Hz%d%b%Y"
def main():
  if "--stop" in sys.argv : print "Nothting needs to do, Quit."; sys.exit(250)

  os.chdir(workDir)
  init_time=datetime.datetime.strptime((now-datetime.timedelta(hours=now.hour%updPrd)).strftime(fmt),fmt); print model,init_time
  ga=grads.GaNum(Bin=GrADS,Echo=None,Window=False)
#  ga=grads.GaNum(Bin=GrADS,Window=False)
#  ga=grads.GaNum(Bin=GrADS)
  try:
    if "-BC" in sys.argv:
      nwp=NWPpost.NWPpost(ga,model,init_time,BC=True)
      u,v=nwp.getVARname()["wind-combined"]; print u,v
    else:
      nwp=NWPpost.NWPpost(ga,model,init_time)
      u,v=nwp.getVARname()["wind"]; print u,v
  except:
    if model[:4]=="WEPS":
      init_time=datetime.datetime.strptime((init_time-datetime.timedelta(hours=6)).strftime(fmt),fmt)
      nwp=NWPpost.NWPpost(ga,model,init_time)
      u,v=nwp.getVARname()["wind"]; print u,v
    elif model[:4]=="NCDR":
      init_time=datetime.datetime.strptime((init_time-datetime.timedelta(hours=6)).strftime(fmt),fmt)
      nwp=NWPpost.NWPpost(ga,model,init_time)
      u,v=nwp.getVARname()["wind"]; print u,v
    else:
      print "%s on %s not found!"%(model,init_time.strftime(fmt))
      return
  global u,v
 # ga("run /opt/grads-2.1.0.oga.1/Classic/scripts/font.gs 10")
  ga("set font 10 file /opt/grads-2.1.0.oga.1/Classic/data/font0.dat")
#  ga("set map auto")
  figure_set(ga)

  try:
    nwp.getQPF(1,5)
  except:
    nwp.getQPF(1,3)
  mask=getMask(ga,lterp_grid="qpf")
  taus=nwp.getTimes()
  for prd in periods:
    for t in taus[1:]:
      if "-w" in sys.argv: continue
#      if (t-init_time).total_seconds()/h2s>72 and model=="GFE": continue
      if not t.hour%prd in [0,12]: continue
      t0=t-datetime.timedelta(hours=prd)
      if not t0 in taus: continue
      print model, init_time, t0, t, prd
      try:
        qpf=nwp.getQPF(t0,t,getGrid=True)
      except:
        qpf=nwp.getQPF(t0,t,getGrid=True)
        continue
      figure_set(ga)
      color_table.colorQPF(ga)
      ga("d qpf")
      draw_shp(ga)
      drawMax(ga,qpf,mask)
      ga("draw title %s: %s + (%d-%dh)"%(model,init_time.strftime(fmt),(t0-init_time).total_seconds()/h2s,(t-init_time).total_seconds()/h2s))
      ga("run cbarn.gs 0.65 1 8.1 3.7")
      file="%s/%s/%s/QPF%d/%sf%03d.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),prd,init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
      if not os.path.exists("/".join(file.split("/")[:-1])): os.makedirs("/".join(file.split("/")[:-1]))
      ga("printim %s x%d y%d white"%(file,xres,yres))
      #raw_input()
      ga("c")


      png_resize(file)


    # wind speed
    if prd==3 and u!=None:
      for t in taus:
        if t.hour%prd !=0: continue
        figure_set(ga)
        ga("set time %s"%t.strftime(fmt2))
        color_table.colorW(ga)
        #ga("d %d*skip(re(%s,%f),20);%d*re(%s,%f);%d*re(mag(%s,%s),%f)"%(ms2kts,u,dd,ms2kts,v,dd,ms2kts,u,v,dd))
        ga("d %f*mag(%s,%s))"%(ms2kts,u,v)) #; print "d %f*mag(%s,%s))"%(ms2kts,u,v) 
        ga("draw title %s Wind: %s + %dh"%(model,init_time.strftime(fmt),(t-init_time).total_seconds()/h2s))
        ga("run cbarn_wind-1.gs 0.65 1 8.1 3.7")
        draw_shp(ga,Marine=True)
        if "-BC" in sys.argv:
          file="%s/%s/%s/speed/%sf%03dcb.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
        else:
          file="%s/%s/%s/speed/%sf%03d.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
        if not os.path.exists("/".join(file.split("/")[:-1])): os.makedirs("/".join(file.split("/")[:-1]))
        ga("printim %s x%d y%d white"%(file,xres,yres))
        #raw_input()

        png_resize(file)


        ga("c")
        if t.hour%12==0:
          figure_set(ga)
          t0=t-datetime.timedelta(hours=12)
          if t0 in taus:
            t1=taus[taus.index(t0)+1]; print t0, t
            color_table.colorW(ga)
#            print model,"d %f*max(mag(%s,%s),time=%s,time=%s))"%(ms2kts,u,v,t1.strftime(fmt2),t.strftime(fmt2))
            if model != "JMA":
              print "%s to %s"%(t1.strftime(fmt2),t.strftime(fmt2))
              if (model == "M04" or model == "M05"): ga("set dfile 3")
              if (model == "ECMWF" and "-BC" in sys.argv ): ga("set dfile 2")
              ga("d %f*max(mag(%s,%s),time=%s,time=%s))"%(ms2kts,u,v,t1.strftime(fmt2),t.strftime(fmt2)))
            else:
              ga("d %f*max(mag(%s,%s),time=%s,time=%s,2))"%(ms2kts,u,v,t1.strftime(fmt2),t.strftime(fmt2)))
            ga("draw title %s Wind`bMax`n: %s + (%d-%dh)"%(model,init_time.strftime(fmt),(t0-init_time).total_seconds()/h2s,(t-init_time).total_seconds()/h2s))
            ga("run cbarn_wind-1.gs 0.65 1 8.1 3.7")
            draw_shp(ga,Marine=True)
            if "-BC" in sys.argv:
              file="%s/%s/%s/speed12/%sf%03dcb.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
            #raw_input()
            else:
              file="%s/%s/%s/speed12/%sf%03d.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
            if not os.path.exists("/".join(file.split("/")[:-1])): os.makedirs("/".join(file.split("/")[:-1]))
            ga("printim %s x%d y%d white"%(file,xres,yres))


            png_resize(file)


            ga("c")
        wind_figure_set(ga)
        color_table.colorW(ga)
        ga("d %f*skip(re(%s,%f),%d);%f*re(%s,%f);%f*re(mag(%s,%s),%f)"%(ms2kts,u,dd,skip,ms2kts,v,dd,ms2kts,u,v,dd))
        if "-BC" in sys.argv:
          file="%s/%s/%s/wind/%sf%03dcb.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
        else:
          file="%s/%s/%s/wind/%sf%03d.png"%(outdir,init_time.strftime("%Y%m"),model.upper(),init_time.strftime(fmt),(t-init_time).total_seconds()/h2s); print file
        if not os.path.exists("/".join(file.split("/")[:-1])): os.makedirs("/".join(file.split("/")[:-1]))
#        ga("printim %s x%d y%d white -t 0"%(file,xres,yres))
#        ga("gxprint %s x%d y%d white -t 0"%(file,xres,yres))
        ga("gxprint %s x%d y%d -t 0"%(file,xres,yres))
        #raw_input()
        ga("c")

        png_resize(file)




#================
def getMask(ga,lterp_grid="qpf"):
  ga("open topo.ctl")
  if "-w" and "-BC" in sys.argv:
    if model[:4]=="WEPS":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
      ga("close 3")
    elif model[:4]=="NCDR":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
      ga("close 3")
    elif model=="M04" or model=="M05":
      ga("set dfile 5")
      ga("define ter=lterp(topo.5(t=1,e=1),%s)"%(lterp_grid))
#      ga("close 5")
    else:
      ga("set dfile 4")
      ga("define ter=lterp(topo.4(t=1,e=1),%s)"%(lterp_grid))
      ga("close 4")

  elif "-w" in sys.argv:
    if model[:4]=="WEPS":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
      ga("close 3")
    elif model[:4]=="NCDR":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
      ga("close 3")
    elif model=="M04" or model=="M05":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
      ga("close 3")
    else:
      ga("set dfile 2")
      ga("define ter=lterp(topo.2(t=1,e=1),%s)"%(lterp_grid))
      ga("close 2")

  else:
    if model[:4]=="WEPS":
      if u==None and v==None:
        ga("set dfile 2")
        ga("define ter=lterp(topo.2(t=1,e=1),%s)"%(lterp_grid))
        ga("close 2")
      else:
        ga("set dfile 3")
        ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
        ga("close 3")
    elif model[:4]=="NCDR":
      if u==None and v==None:
        ga("set dfile 2")
        ga("define ter=lterp(topo.2(t=1,e=1),%s)"%(lterp_grid))
        ga("close 2")
      else:
        ga("set dfile 3")
        ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
        ga("close 3")
    elif model=="M04" or model=="M05":
      ga("set dfile 3")
      ga("define ter=lterp(topo.3(t=1,e=1),%s)"%(lterp_grid))
#      ga("close 3")
    else:
      ga("set dfile 2")
      ga("define ter=lterp(topo.2(t=1,e=1),%s)"%(lterp_grid))
      ga("close 2")
#  for i in range(ga.rline()):
#    if ga.rword(i+1,1)=="Data":
#      dfile=int(ga.rline(i+1).split()[-1])
#      break
#  ga("set dfile %s"%dfile)
#  ga("define ter=lterp(topo.%s(t=1,e=1),%s)"%(dfile,lterp_grid))
#  ga("close %s"%dfile)
  return ga.exp("ter").data

#def figure_set(ga,dims=[118.,122.5,21.3,26.5]):
def figure_set(ga):
  dims=[118.,122.5,21.3,26.5]
  lon1,lon2,lat1,lat2=dims
  ga("set lat %f %f"%(lat1,lat2));  ga("set lon %f %f"%(lon1,lon2))
  ga("set frame on"); ga("set xlab on"); ga("set ylab on"); ga("set grid on")
  ga("set parea 0.7 8 0.7 10.3"); ga("set mproj scaled");ga("set grads off")
  ga("set mpdraw off"); ga("set gxout shade2"); 
  ga("set gxout barb"); ga("set digsiz .11"); ga("set cthick 7")
  ga("set xlint 1"); ga("set xlopts 1 7 0.2"); ga("set ylint 1"); ga("set ylopts 1 7 0.2")

def wind_figure_set(ga):
  ga("set parea 0.7 8 0.7 10.3"); ga("set mproj scaled");ga("set grads off")
  ga("set frame off"); ga("set xlab off"); ga("set ylab off"); ga("set grid off")
  ga("set mpdraw off")
  ga("set gxout barb"); ga("set digsiz .12"); ga("set cthick 12")
  ga("set xlint 1"); ga("set xlopts 1 7 0.2"); ga("set ylint 1"); ga("set ylopts 1 7 0.2")

def draw_shp(ga,b=False,Marine=False):
#  ga("set gxout shp")
  if Marine:
    ga("set line 14 1 5"); ga("draw shp Offshore"); ga("draw shp Inshore")
  ga("set rgb 101 255 255 150") if b else ga("set rgb 101 20 20 20")
  ga("set line 101 1 10"); ga("draw shp 2010_5City_lonlat 0 12"); ga("draw shp 2010_5City_lonlat 14 22"); ga("set line 1 1 5"); ga("draw shp Asia"); ga("draw shp Island")

def drawMax(ga,qpf,mask,qpf_name="qpf"):
  marksiz=0.30; marktype=8; dd=0.1; var="tpm"
  #print "define %s=maskout(%s,lterp(%s(t=1,e=1),%s)-1.e-3)"%(var,qpf,topo,qpf)
  if numpy.prod(qpf.shape) != numpy.prod(mask.shape):
    print "Warning! QPF dimensiotn != Mask dimension", qpf.shape, mask.shape
    return
  tpm=qpf.copy()
  tpm[mask<=0]=0.
  maxv=numpy.max(tpm)#; print maxv
  if(maxv>550): ga("run %s/hatch.gs %s 500 -thickness 7"%(workDir,qpf_name))
  if(maxv>800): ga("run %s/hatch.gs %s 750 -angle 135 -thickness 7"%(workDir,qpf_name))
  if(maxv>1050): ga("run %s/hatch.gs %s 1000 -color 2 -thickness 7"%(workDir,qpf_name))
  if(maxv>1550): ga("run %s/hatch.gs %s 1500 -angle 135 -color 2 -thickness 7"%(workDir,qpf_name))
  #print numpy.argmax(numpy.max(tpm,axis=1))
  x=tpm.grid.lon[numpy.argmax(numpy.max(tpm,axis=0))]
  y=tpm.grid.lat[numpy.argmax(numpy.max(tpm,axis=1))]
  ga("q w2xy %s %s"%(x,y))
  rec=ga.rline(1).split(); x=float(rec[2]); y=float(rec[5])
  ga("set line 1 1 10")
  ga("set strsiz %s %s"%(marksiz*1.2,marksiz*1.5))
  ga("set string 1 l 20")
  if maxv <0.1:
    pass
  elif 0.1<= maxv < 10:
    ga("draw mark %s %s %s %s"%(marktype,x,y,marksiz))
    ga("draw string %s %s %.1f"%(x+dd,y,maxv))
  else:
    ga("draw mark %s %s %s %s"%(marktype,x,y,marksiz))
    ga("draw string %s %s %.0f"%(x+dd,y,maxv))
  dd=(tpm.grid.lat[1]-tpm.grid.lat[0])*math.pi/180.*6371.e3 # in meter
  sumQ=(tpm.T*1.e-3*dd*dd*numpy.cos(tpm.grid.lat*math.pi/180.)).sum()
  ga("set strsiz 0.25"); ga("set string 1 r 5")
#  ga('draw string 8 0.18 total water: %.0f `3*`010`a6`n m`a3'%round(sumQ/1.e6))
  ga('draw string 8 0.18 total water: %.0f X 10`a6`n m`a3'%round(sumQ/1.e6))
#  ga('draw string 8 0.18 total water: %.0f'%round(sumQ/1.e6))


#============================
def png_resize(png) :
  if os.path.exists(png) :
    pngfs8 = png.split(".")[0] + "-fs8.png"
    if os.path.exists(pngfs8) : os.system("rm -f %s"%pngfs8)
    os.system("%s 256 %s"%(pngquant,png))
    os.system("mv %s %s"%(pngfs8,png))

#====================================================================
if __name__=="__main__":
  main()
