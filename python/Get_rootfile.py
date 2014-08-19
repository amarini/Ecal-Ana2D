#!env python

import ROOT

ROOT.gROOT.ProcessLine(' struct Entry { \
		unsigned short x[12] ;\
		}; \
		' )
#from ROOT import event,ped
from ROOT import Entry

DEBUG=1

def Get_rootfile(filename):
	if ".txt" in filename or ".root" in filename:
		raise "Exception filename should have no extension"
	txt=open(filename+".txt")
	
	if txt==None:
		raise "Exceptions file",filename,"does not exist"
	fROOT=ROOT.TFile(filename + ".root","RECREATE",filename+".root",9)
	fROOT.cd()

	ped=Entry()
	event=Entry()

	pedTree=ROOT.TTree("ped","pedestal taken from the file "+ filename)
	pedTree.Branch("Ped",ROOT.AddressOf(ped,"x"),"ch0/S:ch1/S:ch2/S:ch3/S:ch4/S:ch5/S:ch6/S:ch7/S:ch8/S:ch9/S:ch10/S:ch11/S")
	
	dataTree=ROOT.TTree("data","data taken from file "+ filename)
	dataTree.Branch("Events",ROOT.AddressOf(event,"x"),"ch0/S:ch1/S:ch2/S:ch3/S:ch4/S:ch5/S:ch6/S:ch7/S:ch8/S:ch9/S:ch10/S:ch11/S")

	pedSection=True
	dataSection=False
	for line in txt:
		if "data" in line:
			pedSection=False
			dataSection=True
			continue;
		parts=line.split()
		for i in range(0,12):
			ped.x[i]=float(parts[i])
			event.x[i]=float(parts[i])
		if dataSection:
			dataTree.Fill()
		if pedSection:
			pedTree.Fill()
	dataTree.Print()
	pedTree.Print()
	txt.close()
	fROOT.Write()
	fROOT.Close()
	print "here"

##############################################
