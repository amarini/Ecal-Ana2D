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
		strings=["name","xtitle","ytitle","merge"]
		twofloats=["xaxis","yaxis","zaxis","pedrange1","pedrange2"]
		oneint=["ch1","ch2","xrebin","yrebin","density","maxentries"]
		onefloat=["statrescale"]
		for word in parts:
			if word.split("=")[0] in strings:
				tmpDict[word.split("=")[0]]=word.split("=")[1].replace('~',' ')
			elif word.split("=")[0] in twofloats:
				tmpStr=word.split("=")[1]
				tmpDict[word.split("=")[0]]= (float(tmpStr.split(",")[0]),float(tmpStr.split(",")[1]) )
			elif  word.split("=")[0] in onefloat:
				tmpDict[word.split("=")[0]]=float(word.split("=")[1])
			elif  word.split("=")[0] in oneint:
				tmpDict[word.split("=")[0]]=int(word.split("=")[1])
		#set default
		if not "name" in tmpDict: tmpDict["name"]="xxx"
		if not "merge" in tmpDict: tmpDict["merge"]=None
		if not "maxentries" in tmpDict: tmpDict["maxentries"]=-1
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
		if not "statrescale" in tmpDict: tmpDict["statrescale"]=1
		if tmpDict["statrescale"] > 1 or tmpDict["statrescale"] <0:
			print "Error: Rescale of Stat not in [0-1]. I will assume 1"
			tmpDict["statrescale"]=1
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
	''' Run a pedestal fit:
		t -> tree
		c -> canvas/pad to save the results in
		ch -> channell to run the fit
		f1min,f1max -> min and max of the function
	'''
	h=ROOT.TH1F("ch%d"%ch,"Pedestal ch%d"%ch,1024,0,1024)
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

def FitGaus(h):
	f1min=h.GetBinLowEdge(1)
	f1max=h.GetBinLowEdge(h.GetNbinsX()+1)
	f1=ROOT.TF1("fit1","gaus",f1min,f1max)
	f1.SetParameter(0,h.Integral())
	f1.SetParameter(1,h.GetMean())
	f1.SetParameter(2,h.GetRMS())

	h.Fit("fit1","NQ")

	mu=f1.GetParameter(1)
	sigma=f1.GetParameter(2)

	print "step1 '"+h.GetName()+"' mu=",mu,"sigma=",sigma,"norm=",f1.GetParameter(0)
	print "step1 R==",f1min,f1max
	f1min=max(mu-sigma,f1min)
	f1max=min(mu+sigma,f1max)

	if(mu<0):
		maxH=0
		iMax=0
		for i in range(1,h.GetNbinsX()+1):
			if maxH<h.GetBinContent(i): 
				maxH=h.GetBinContent(i)
				iMax=i
		print "SWITCH TO MU<0 mode"
		f1min=h.GetBinLowEdge(iMax-5)
		f1max=h.GetBinLowEdge(iMax+4)
	
	
	f1.SetRange(f1min,f1max)
	h.Fit("fit1","RQ")
	mu=f1.GetParameter(1)
	sigma=f1.GetParameter(2)

	return (mu,sigma)

def DrawLines(conf):
	low=0.
	high=1000.

	x1=ROOT.TGraph()
	x1.SetName("line_x1")
	x2=ROOT.TGraph()
	x2.SetName("line_x2")
	y1=ROOT.TGraph()
	y1.SetName("line_y1")
	y2=ROOT.TGraph()
	y2.SetName("line_y2")
	
	if "xaxis" in conf:
		x1.SetPoint(0,conf["xaxis"][0],low)
		x1.SetPoint(1,conf["xaxis"][0],high)
		x2.SetPoint(0,conf["xaxis"][1],low)
		x2.SetPoint(1,conf["xaxis"][1],high)
	if "yaxis" in conf:
		y1.SetPoint(0,low,conf["yaxis"][0])
		y1.SetPoint(1,high,conf["yaxis"][0])
		y2.SetPoint(0,low,conf["yaxis"][1])
		y2.SetPoint(1,high,conf["yaxis"][1])

	# set color
	x1.SetLineColor(ROOT.kGreen+2)
	x2.SetLineColor(ROOT.kGreen+2)
	y1.SetLineColor(ROOT.kGreen+2)
	y2.SetLineColor(ROOT.kGreen+2)
	#width
	x1.SetLineWidth(2)
	x2.SetLineWidth(2)
	y1.SetLineWidth(2)
	y2.SetLineWidth(2)
	#stlye
	x1.SetLineStyle(1)
	x2.SetLineStyle(1)
	y1.SetLineStyle(1)
	y2.SetLineStyle(1)
	#Draw
	x1.Draw("L SAME")
	x2.Draw("L SAME")
	y1.Draw("L SAME")
	y2.Draw("L SAME")
	print "Drawing lines on the current pad:",ROOT.gPad.GetName()
	return [x1,x2,y1,y2]

def PlotRebin( hData_col,conf):
	''' Plot a rebinned histograms 
		hData_col -> data histograms
		conf -> configurator
	'''
	hDataName=hData_col.GetName()
	hData_rebin=hData_col.Clone(hDataName+"_rebin")

	hData_rebin.RebinX(conf["xrebin"])
	hData_rebin.RebinY(conf["yrebin"])
	hData_rebin.GetXaxis().SetLabelSize(0.03)
	hData_rebin.GetYaxis().SetLabelSize(0.03)
	hData_rebin.GetYaxis().SetTitleOffset(1.)
	hData_rebin.GetXaxis().SetTitleOffset(1.)
	hData_rebin.GetXaxis().CenterTitle()
	hData_rebin.GetYaxis().CenterTitle()
	#find the maximum in the plot
	maximum=0
	for xBin in range(hData_rebin.GetXaxis().FindBin(conf["xaxis"][0]),hData_rebin.GetXaxis().FindBin(conf["xaxis"][1]) ):
		for yBin in range(hData_rebin.GetYaxis().FindBin(conf["yaxis"][0]),hData_rebin.GetYaxis().FindBin(conf["yaxis"][1]) ):
			if hData_rebin.GetBinContent(xBin,yBin) > maximum:
				maximum=hData_rebin.GetBinContent(xBin,yBin)

	hData_rebin.SetMaximum(maximum)
	if "zaxis" in conf:
		hData_rebin.GetZaxis().SetRangeUser(conf["zaxis"][0],conf["zaxis"][1])
		if conf["zaxis"][1] < maximum: print "WARNING: Maximum is too low: set to "+str(conf["zaxis"][1]) + " while it should be " + str(maximum)

	hData_rebin.GetXaxis().SetRangeUser(conf["xaxis"][0],conf["xaxis"][1])
	hData_rebin.GetYaxis().SetRangeUser(conf["yaxis"][0],conf["yaxis"][1])

	return hData_rebin

def CleanHisto(hData_rebin):
	''' draw the scatter plot. This macros cleans the 0 content to an epsilon.for drawing purpose'''
	hData_clean=hData_rebin.Clone(hData_rebin.GetName()+"_clean")
	for xBin in range(1,hData_clean.GetNbinsX() + 1): 
	  for yBin in range(1,hData_clean.GetNbinsY() + 1): 
		  if hData_clean.GetBinContent(xBin,yBin) <= 0 : ### also the = 0
			  hData_clean.SetBinContent(xBin,yBin,0.001)
			  hData_clean.SetBinError(xBin,yBin,1)
	return hData_clean

import Get_rootfile as External

def Plot( conf ):
	''' Make all the plots from a configuration file 
	'''
	fROOT=ROOT.TFile.Open(conf["name"]+".root")
	#if fROOT==None:
	#	ROOT.gSystem.Load("Get_rootfile_C.so")
	#	ROOT.Get_rootfile(conf["name"])
	#	fROOT=ROOT.TFile.Open(conf["name"]+".root")
	if fROOT==None:
		External.Get_rootfile(conf["name"])
		fROOT=ROOT.TFile.Open(conf["name"]+".root")
	
	### make the basic plots
	c1=ROOT.TCanvas("c1","Fit",0,0,768,576)	
	c1.Divide(2,2)
	#pedTree=fROOT.Get("ped")
	pedTree=ROOT.TChain("ped")
	pedTree.Add(conf["name"]+".root")
	if "merge" in conf and conf["merge"] != None:
		for f in conf["merge"].split(','):
			print "Adding file",f+".root","to the pedestal for",conf["name"]
			f2=ROOT.TFile.Open(f+".root")
			if f2==None:External.Get_rootfile(f)
			else: f2.Close()
			pedTree.Add(f+".root")
	c1.cd(1)
	(h1,ped1)=PedFit(pedTree,c1, conf["ch1"] , conf["pedrange1"][0], conf["pedrange1"][1])
	c1.cd(2)
	(h2,ped2)=PedFit(pedTree,c1, conf["ch2"] , conf["pedrange2"][0], conf["pedrange2"][1])

	c1.cd(3)
	#dataTree=fROOT.Get("data")
	dataTree=ROOT.TChain("data")
	dataTree.Add(conf["name"]+".root")
	if "merge" in conf and conf["merge"] != None:
		for f in conf["merge"].split(','):
			print "Adding file",f+".root","to the datatree for",conf["name"]
			dataTree.Add(f+".root")
	hDataName="ch%d:ch%d Ped. Sub."%(conf["ch1"],conf["ch2"])
	hData=ROOT.TH2F(hDataName,hDataName,1024,0,1024,1024,0,1024)
	maxentries=conf["maxentries"] if conf["maxentries"] >0 else 1000000000
	if conf["maxentries"]<=0 and conf["statrescale"] <1 :
		print "Using stat rescale: "
		maxentries= int (dataTree.GetEntries() * conf["statrescale"] )
	if conf["maxentries"] > 0 and conf["statrescale"]<1:
		print "WARNING: Cannot declare both entries and stat rescale. Ignoring the stat recale."
	dataTree.Draw("ch%d-%f:ch%d-%f>>%s"%(conf["ch1"],ped1,conf["ch2"],ped2,hDataName),"","",maxentries)
	hData.GetYaxis().SetTitle(conf["ytitle"])
	hData.GetXaxis().SetTitle(conf["xtitle"])
	hData.GetYaxis().SetTitleOffset(1.0)
	hData.GetXaxis().SetTitleOffset(1.0)
	lines=DrawLines(conf)

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
	hData_rebin=PlotRebin(hData_col,conf)

	#Draw lego plot
	c4=ROOT.TCanvas("c4","c4",600,600)
	hData_rebin.Draw("lego2 0")
	ToSave[conf["name"]+"_c4"]=c4
	##

	#draw cont plot
	c5=ROOT.TCanvas("c5","c5",600,600)
	# Palette 53
	#    if ncolors = 51 and colors=0, a Deep Sea palette is used.
	#   if ncolors = 52 and colors=0, a Grey Scale palette is used.
	#   if ncolors = 53 and colors=0, a Dark Body Radiator palette is used.
	#   if ncolors = 54 and colors=0, a two-color hue palette palette is used.(dark blue through neutral gray to bright yellow)
	#   if ncolors = 55 and colors=0, a Rain Bow palette is used.
	#   if ncolors = 56 and colors=0, an inverted Dark Body Radiator palette is used.
    	#ROOT.gStyle.SetPalette(56);


	ROOT.gSystem.Load("fancyPalette_C.so")
	#ROOT.DarkBodyRadiator();
	ROOT.MonoCromatic();

	#ROOT.ChangePalette();
	hData_clean=CleanHisto(hData_rebin)

	hData_clean.Draw("COL Z");
	ToSave[conf["name"]+"_c5"]=c5

	#Draw Projection
	l=ROOT.TLatex()
	l.SetNDC()
	l.SetTextSize(0.03)
	l.SetTextAlign(33)

	c6=ROOT.TCanvas("c6","c6",600,600)
	px=hData_rebin.ProjectionX();
	px.SetTitle("Projection X (%.1f<=Y<=%.1f)"%( hData_rebin.GetXaxis().GetBinLowEdge( hData_rebin.GetXaxis().GetFirst() ) , 
						hData_rebin.GetXaxis().GetBinLowEdge( hData_rebin.GetXaxis().GetLast() + 1)
		))
	px.SetFillColor(ROOT.kRed-7)
	px.SetFillStyle(3001)
	px.SetLineWidth(2)
	px.Draw("HIST")
	(m,s)=FitGaus(px)
	l.DrawLatex(.89,.89, "#splitline{#mu=%.1f}{#sigma=%.1f}"%(m,s)) 
	ToSave[conf["name"]+"_c6"]=c6

	c7=ROOT.TCanvas("c7","c7",600,600)
	py=hData_rebin.ProjectionY();
	py.SetTitle("Projection Y (%.1f<=X<=%.1f)"%( hData_rebin.GetYaxis().GetBinLowEdge( hData_rebin.GetYaxis().GetFirst() ) , 
						hData_rebin.GetYaxis().GetBinLowEdge( hData_rebin.GetYaxis().GetLast() + 1)
		))
	py.SetFillColor(ROOT.kBlue-7)
	py.SetFillStyle(3001)
	py.SetLineWidth(2)
	py.Draw("HIST")
	(m,s)=FitGaus(py)
	l.DrawLatex(.89,.89, "#splitline{#mu=%.1f}{#sigma=%.1f}"%(m,s)) 
	ToSave[conf["name"]+"_c7"]=c7

	if "density" in conf and conf["density"]:
	   c8=ROOT.TCanvas("c8","c8",600,600)
	   # this must be compiled, otherwise too slow
	   ROOT.gSystem.Load("kernelDensity_C.so")
	   xaxis=ROOT.std.pair(float,float)()
	   yaxis=ROOT.std.pair(float,float)()
	   xaxis.first= conf["xaxis"][0]
	   yaxis.first= conf["yaxis"][0]
	   xaxis.second= conf["xaxis"][1]
	   yaxis.second= conf["yaxis"][1]
	   maxZ=(hData_rebin.GetMaximum() + 1) *8
	   #hData_density=ROOT.kernelDensity(hData_rebin,maxZ*4,xaxis,yaxis)
	   hData_softRebin=hData_col.Clone( hData_col.GetName()+"_softrebin")
	   hData_softRebin.RebinX(max(conf["xrebin"],1))
	   hData_softRebin.RebinY(max(conf["yrebin"],1))
	   hData_softRebin.GetXaxis().SetRangeUser(conf["xaxis"][0],conf["xaxis"][1])
	   hData_softRebin.GetYaxis().SetRangeUser(conf["yaxis"][0],conf["yaxis"][1])
	   hData_density=ROOT.kernelDensity(hData_softRebin,maxZ,xaxis,yaxis)
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
