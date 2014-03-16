#include <iostream>
#include <Riostream.h>
#include <TPaveText.h>
#include <TF1.h>
#include <cstdlib>
#include <cstdio>
#include <string>
#include <cmath>
#include <TMath.h>
#include <TGraph.h>
#include <TLegend.h>
#include <vector>
#include <TCanvas.h>
#include <TFile.h>
#include <map>
#include <TRandom3.h>
#include <complex>
#include <TString.h>
#include <TH1.h>
#include <TLatex.h>
#include <TString.h>
#include <TPad.h>
#include <TStyle.h>
#include <TGaxis.h>
#include <TGraphErrors.h>
#include <TTree.h>
#include <fstream>
#include <TChain.h>
#include <TROOT.h>
#include <TStopwatch.h>


using namespace std;

typedef unsigned short event_t;

string filename;

void MemoryAllocation(event_t* &event,event_t* &ped){
    event=new event_t[12];
    ped=new event_t[12];
}

void CleanMemory(event_t* &event,event_t* &ped){
    delete [] event;
    delete [] ped;
    event=NULL;
    ped=NULL;
}


int Get_rootfile(){
    event_t* event=NULL;
    event_t* ped=NULL;
    MemoryAllocation(event,ped);
    cout<<"Please input the file name w/o extension"<<endl;
    cin >> filename;
    string filename_open=filename+".txt";

    ifstream infileabs (filename_open.data(),ios::in);
	if(!infileabs.is_open()){
		cout<<"No inputfile to open!"<<endl;
        return -1;
	}
    string filename_root=filename+".root";
    TFile* f= new TFile(filename_root.data(),"RECREATE",filename_root.data(),9);
    TTree* pedestal = new TTree("ped",Form("pedestal taken from the file %s",filename.data()));
    pedestal->Branch("Ped",ped,"ch0/S:ch1/S:ch2/S:ch3/S:ch4/S:ch5/S:ch6/S:ch7/S:ch8/S:ch9/S:ch10/S:ch11/S");
    TTree* data = new TTree("data",Form("data taken from the file %s",filename.data()));
    data->Branch("Events",event,"ch0/S:ch1/S:ch2/S:ch3/S:ch4/S:ch5/S:ch6/S:ch7/S:ch8/S:ch9/S:ch10/S:ch11/S");
    string line;
    while(
        getline(infileabs,line) && line!="data\0"
            ){
	if (line.find("data") != string::npos) break;
        stringstream sstr(line);
        for(int i=0;i<12;i++) {sstr>>ped[i];/*cout<<ped[i]<<" ";*/}
        pedestal->Fill();
    };

    cout<<"line is"<<line<<endl; //DEBUG
    while(getline(infileabs,line)){
        stringstream sstr(line);
        for(int i=0;i<12;i++) {sstr>>event[i];/*cout<<event[i]<<" ";*/}
        data->Fill();

    }
    data->Print();
    pedestal->Print();
    infileabs.close();
    f->Write();
    f->Close();
    cout<<"here"<<endl;
    delete f;
    CleanMemory(event,ped);
    return 0;
}
