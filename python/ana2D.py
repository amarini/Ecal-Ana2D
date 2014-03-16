import os, sys, array
import math

from optparse import OptionParser
usage="usage: %prog [options] "
parser=OptionParser(usage=usage)
parser.add_option("-d","--dat" ,dest='dat',type='string',help="Input Configuration file.\n\t Default=%default",default="xxx")	
parser.add_option("-b","--batch" ,dest='batch',action='store_true',help="Batch Mode.\n\t Default=%default",default=False)	
parser.add_option("","--dir" ,dest='dir',type='string',help="PlotDirectory\n\t Default=%default",default="./")	
(options,args)=parser.parse_args()

import ROOT
if options.batch:
	ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptFit(1111)
ROOT.gROOT.SetStyle("Plain")

#name=abcd pedrange1=1,2. 
outDir="./"

def ReadDat(inputfile):
	f=open(inputfile,"r")
	R={}
	for line in f:
		l0=line.split('#')[0]
		if l0 == "": continue;
		l0=l0.replace('\n','')
		l0=l0.replace('\r','')
		#each parts is a command line for a plot
		parts=l0.split()
	
		#float,float	
		print "Parsing line:" + l0 
		tmpDict={}
		strings=["name","xtitle","ytitle"]
		twofloats=["xaxis","yaxis","zaxis","pedrange1","pedrange2"]
		oneint=["ch1","ch2","xrebin","yrebin","density"]
		onefloat=[]
		for word in parts:
			if word.split("=")[0] in strings:
				tmpDict[word.split("=")[0]]=word.split("=")[1]
			elif word.split("=")[0] in twofloats:
				tmpStr=word.split("=")[1]
				tmpDict[word.split("=")[0]]= (float(tmpStr.split(",")[0]),float(tmpStr.split(",")[1]) )
			elif  word.split("=")[0] in onefloat:
				tmpDict[word.split("=")[0]]=float(word.split("=")[1])
			elif  word.split("=")[0] in oneint:
				tmpDict[word.split("=")[0]]=int(word.split("=")[1])
		#set default
		if not "name" in tmpDict: tmpDict["name"]="xxx"
		if not "ch1" in tmpDict: tmpDict["ch1"]=1
		if not "ch2" in tmpDict: tmpDict["ch2"]=2
		if not "xaxis" in tmpDict: tmpDict["xaxis"]=(100,1000)
		if not "yaxis" in tmpDict: tmpDict["yaxis"]=(100,1000)
		# no default zaxis. If exists is used
		if not "xtitle" in tmpDict: tmpDict["xtitle"]="3HF-WLS"
		if not "ytitle" in tmpDict: tmpDict["ytitle"]="CeF_{3}"
		if not "xrebin" in tmpDict: tmpDict["xrebin"]=1
		if not "yrebin" in tmpDict: tmpDict["yrebin"]=1
		if not "pedrange1" in tmpDict: tmpDict["pedrange1"]=(0,50)
		if not "pedrange2" in tmpDict: tmpDict["pedrange2"]=(0,50)
		# no default density. If exists is used
		if tmpDict["name"] != "xxx": R[tmpDict["name"]] =tmpDict
	return R

def PrintDat( R ):
	for name in R:
		print "----- "+name+" -------"
		print R[name]

def PrintStatusBar( frac,npoints=30 ):
	      Status="\r["
	      for i in range(0,npoints):
		      if i <= npoints*frac : Status+="*"
		      else: Status +="-"
	      Status += "]"
	      Status += " %3.0f %%"%(frac*100)
	      sys.stdout.write(Status)
	      sys.stdout.flush()

def PedFit(t,c,ch,f1min,f1max):
	h=ROOT.TH1F("ch%d"%ch,"ch%d"%ch,1024,0,1024)
	t.Draw("ch%d>>ch%d"%(ch,ch))
	h.GetXaxis().SetTitle("Channel")
	h.GetYaxis().SetTitle("#")
	h.GetXaxis().SetTitleOffset(1.)
	h.GetYaxis().SetTitleOffset(1.)
	h.GetXaxis().SetRangeUser(f1min,f1max)
	f1=ROOT.TF1("fit1","gaus",f1min,f1max)
	f1.SetLineColor(ROOT.kRed)
	h.Fit("fit1","R")
	c.Update()
	ped=f1.GetParameter(1)
	print "Pedestal for ch"+str(ch)+" is "+str(ped)
	return (h,ped)

def Plot( conf ):
	fROOT=ROOT.TFile.Open(conf["name"]+".root")
	if fROOT==None:
		ROOT.gSystem.Load("Get_rootfile_C.so")
		ROOT.Get_rootfile(conf["name"])
		fROOT=ROOT.TFile.Open(conf["name"]+".root")
	c1=ROOT.TCanvas("c1","Fit",0,0,768,576)	
	c1.Divide(2,2)
	pedTree=fROOT.Get("ped")
	c1.cd(1)
	(h1,ped1)=PedFit(pedTree,c1, conf["ch1"] , conf["pedrange1"][0], conf["pedrange1"][1])
	c1.cd(2)
	(h2,ped2)=PedFit(pedTree,c1, conf["ch2"] , conf["pedrange2"][0], conf["pedrange2"][1])

	c1.cd(3)
	dataTree=fROOT.Get("data")
	hDataName="ch%d:ch%d Ped_Sub"%(conf["ch1"],conf["ch2"])
	hData=ROOT.TH2F(hDataName,hDataName,1024,0,1024,1024,0,1024)
	dataTree.Draw("ch%d-%f:ch%d-%f>>%s"%(conf["ch1"],ped1,conf["ch2"],ped2,hDataName))
	hData.GetYaxis().SetTitle(conf["ytitle"])
	hData.GetXaxis().SetTitle(conf["xtitle"])
	hData.GetYaxis().SetTitleOffset(1.0)
	hData.GetXaxis().SetTitleOffset(1.0)

	c1.cd(4)
	hData_col=hData.Clone( hDataName+"_colored")
	hData_col.SetStats(0)
	hData_col.Draw("colz")
	hData_col.GetXaxis().SetRangeUser(conf["xaxis"][0],conf["xaxis"][1])
	hData_col.GetYaxis().SetRangeUser(conf["yaxis"][0],conf["yaxis"][1])
	c1.Update()

	ToSave={}
	ToSave[conf["name"]+"_c1"]=c1
	#More Plots
	hData_rebin=hData_col.Clone(hDataName+"_rebin")

	hData_rebin.RebinX(conf["xrebin"])
	hData_rebin.RebinY(conf["yrebin"])
	hData_rebin.GetXaxis().SetLabelSize(0.03)
	hData_rebin.GetYaxis().SetLabelSize(0.03)
	hData_rebin.GetYaxis().SetTitleOffset(1.)
	hData_rebin.GetXaxis().SetTitleOffset(1.)
	hData_rebin.GetXaxis().CenterTitle()
	hData_rebin.GetYaxis().CenterTitle()
	maximum=0
	for xBin in range(hData_rebin.GetXaxis().FindBin(conf["xaxis"][0]),hData_rebin.GetXaxis().FindBin(conf["xaxis"][1]) ):
		for yBin in range(hData_rebin.GetYaxis().FindBin(conf["yaxis"][0]),hData_rebin.GetYaxis().FindBin(conf["yaxis"][1]) ):
			if hData_rebin.GetBinContent(xBin,yBin) > maximum:
				maximum=hData_rebin.GetBinContent(xBin,yBin)

	hData_rebin.SetMaximum(maximum)
	if "zaxis" in conf:
		hData_rebin.GetZaxis().SetRangeUser(conf["zaxis"][0],conf["zaxis"][1])
		if conf["zaxis"][1] < maximum: print "Maximum is too low: set to "+str(conf["zaxis"][1]) + " while is " + str(maximum)


	hData_rebin.GetXaxis().SetRangeUser(conf["xaxis"][0],conf["xaxis"][1])
	hData_rebin.GetYaxis().SetRangeUser(conf["yaxis"][0],conf["yaxis"][1])

	#Draw lego plot
	c4=ROOT.TCanvas("c4","c4",600,600)
	hData_rebin.Draw("lego2 0")
	c3=ROOT.TCanvas("c3","c3",600,600)
	ROOT.gPad.SetTicks(1,1)
        ROOT.gPad.SetRightMargin(0.15);
        ROOT.gPad.SetLeftMargin(0.15);
	ToSave[conf["name"]+"_c4"]=c4

	#draw cont plot
	c5=ROOT.TCanvas("c5","c5",600,600)
    	#ROOT.gStyle.SetPalette(53);
	ROOT.gSystem.Load("fancyPalette_C.so")
	ROOT.DarkBodyRadiator();
	#ROOT.ChangePalette();
	hData_rebin.Draw("CONT4 Z");
	ToSave[conf["name"]+"_c5"]=c5

	#Draw Projection
	c6=ROOT.TCanvas("c6","c6",600,600)
	px=hData_rebin.ProjectionX();
	px.SetFillColor(ROOT.kRed-7)
	px.SetFillStyle(3001)
	px.SetLineWidth(2)
	px.Draw("HIST")
	ToSave[conf["name"]+"_c6"]=c6

	c7=ROOT.TCanvas("c7","c7",600,600)
	py=hData_rebin.ProjectionY();
	py.SetFillColor(ROOT.kBlue-7)
	py.SetFillStyle(3001)
	py.SetLineWidth(2)
	py.Draw("HIST")
	ToSave[conf["name"]+"_c7"]=c7

	if "density" in conf and conf["density"]:
	   c8=ROOT.TCanvas("c8","c8",600,600)
	   ROOT.gSystem.Load("kernelDensity_C.so")
	   xaxis=ROOT.std.pair(float,float)()
	   yaxis=ROOT.std.pair(float,float)()
	   xaxis.first= conf["xaxis"][0]
	   yaxis.first= conf["yaxis"][0]
	   xaxis.second= conf["xaxis"][1]
	   yaxis.second= conf["yaxis"][1]
	   maxZ=hData_rebin.GetMaximum()
	   hData_density=ROOT.kernelDensity(hData_rebin,maxZ*4,xaxis,yaxis)
	   hData_density.Draw("CONT4 Z")
	   ToSave[conf["name"]+"_density"]=c8
	
	for outName in ToSave:
		ToSave[outName].SaveAs(outDir+outName+".pdf")
		ToSave[outName].SaveAs(outDir+outName+".png")


if __name__ == "__main__":

	outDir=options.dir
	if outDir[-1] != '/' : outDir+="/"

	globalConfig=ReadDat(options.dat)	
	PrintDat(globalConfig)
	for name in globalConfig:
		Plot( globalConfig[name]) 
