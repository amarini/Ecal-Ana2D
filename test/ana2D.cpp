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
#include <TH2.h>
#include <TLatex.h>
#include <TString.h>
#include <TPad.h>
#include <TStyle.h>
#include <TGaxis.h>
#include <TGraphErrors.h>
#include <TTree.h>
#include <fstream>
#include "Get_rootfile.cpp"
#include <TChain.h>
#include <TROOT.h>
#include <TStopwatch.h>

#include "fancyPalette.C"

using namespace std;

extern string filename;

void Get_Graph(TH1F* h301,int nch1,double &Sub_Ped,TCanvas* c1,TTree* ped){
    string ans;
    Double_t f1min=10.,f1max=150.;
    h301=new TH1F(Form("ch%d",nch1),Form("ch%d",nch1),1024,0.,1024.);
    ped->Draw(Form("ch%d>>ch%d",nch1,nch1));
    h301->GetXaxis()->SetTitle("Channel");
    h301->GetYaxis()->SetTitle("#");
    h301->GetXaxis()->SetTitleOffset(1.0);
    h301->GetYaxis()->SetTitleOffset(1.0);
    h301->GetXaxis()->SetRange(0,200);
    c1->Update();
    // Define the fit function
     TF1 *f1 = new TF1("fit1","gaus",f1min,f1max);
    f1->SetLineColor(2);
    h301->Fit("fit1","R");
    c1->Update();
    Sub_Ped=f1->GetParameter(1);

    cout<< "Fitted pedestal value (rounded) = " << Sub_Ped<<endl;
    cout<< "Pedestal fit OK? [Y/N]: ";
     cin >> ans;
     if  (ans!="Y")
    {do
      {
        delete f1;
        cout << "Give (dotted) start value for pedestal fit: ";
        cin >> f1min;
        printf ("pedmin: %4.0f \n",f1min);
        cout << "Give (dotted) end value for pedestal fit: ";
        cin >> f1max;
        printf ("pedmax: %4.0f \n",f1max);
        f1 = new TF1("fit1","gaus",f1min, f1max);
        f1->SetLineColor(2);
        h301->Fit("fit1","R"); // "R" restricts the range for the fit
        c1->Update();
        Sub_Ped=f1->GetParameter(1);
        cout<< "Fitted pedestal value (rounded) = " << Sub_Ped<<endl;
        cout<< "Pedestal fit OK? [Y/N] ";
        cin >> ans;
      } while (ans!="Y");
    }
}

TH2F* rebin(TTree* data,char* h205name,int nch1, int nch2, double Sub_Ped1,double Sub_Ped2,int nbbin=256){
    TH2F* h205=new TH2F("ped-sub rebin",h205name,nbbin,0,1024,nbbin,0,1024);
    data->Draw(Form("ch%d-%.12f:ch%d-%.12f>>ped-sub rebin",nch1,Sub_Ped1,nch2,Sub_Ped2));
    h205->GetYaxis()->SetTitle(Form("ch%d",nch1));
    h205->GetXaxis()->SetTitle(Form("ch%d",nch2));
    h205->GetXaxis()->SetTitleOffset(1.0);
    h205->GetYaxis()->SetTitleOffset(1.5);
    h205->GetYaxis()->CenterTitle();
    h205->GetXaxis()->CenterTitle();
    h205->SetFillColor(46);
    return h205;
}

int ana2D(){
    gROOT->SetStyle("Plain"); // possibilities: Default, Plain, Bold, Video, Pub
    gStyle->SetOptStat(1002201);
    gStyle->SetOptFit(1111);
    double Sub_Ped1,Sub_Ped2;
    int labelopen=0;
    string opfile; 
    if(Get_rootfile()==-1){
        opfile=filename+".root";
        cout<<opfile<<" is the filename"<<endl;
        printf("Attempting to look for tree file in the current folder >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n");
        TFile* f=new TFile(opfile.data());
        if(f->IsZombie()){
            cout<<"Can't find tree file!Quit!"<<endl;
            return -1;}
        else labelopen=1;
    }
    else {
        opfile=filename+".root";
        cout<<opfile<<" is the filename"<<endl;
    }
    TCanvas* c1=new TCanvas("c1","Fit",0,0,768,576);
    int nch1=0,nch2=0;
    string ans;
    do{
        cout<<"Input two channels you would like to plot"<<endl;
        cin>>nch1>>nch2;
        printf("ch %d and ch %d will be drawn\n",nch1,nch2);
        cout<<"Y/N?";
        cin>>ans;
    }while(ans!="Y");
    c1->Divide(2,2);
    c1->cd(1);
    TFile* f=new TFile(opfile.data());
    TTree* ped0=(TTree*)f->Get("ped");
    TH1F* h301=NULL;
    Get_Graph(h301,nch1,Sub_Ped1,c1,ped0);
    c1->cd(2);
    TH1F* h302=NULL;
    Get_Graph(h302,nch2,Sub_Ped2,c1,ped0);
    c1->cd(3);
    TTree* data=(TTree*)f->Get("data");
    char* h401name=Form("ch%d:ch%d Ped_Sub",nch1,nch2);
    TH2F* h401=new TH2F(h401name,h401name,1024,0,1024,1024,0,1024);
    data->Draw(Form("ch%d-%.12f:ch%d-%.12f>>%s",nch1,Sub_Ped1,nch2,Sub_Ped2,h401name));
    h401->GetYaxis()->SetTitle(Form("ch%d",nch1));
    h401->GetXaxis()->SetTitle(Form("ch%d",nch2));
    h401->GetXaxis()->SetTitleOffset(1.0);
    h401->GetYaxis()->SetTitleOffset(1.5);

    c1->cd(4);
    TH2F* h401p=(TH2F*)h401->Clone();
    h401p->SetStats(kFALSE);
    h401p->Draw("colz");
    c1->Update();

cout<<"Get More plots?[Y/N]";
    cin>>ans;
    TH2F* h205=NULL;
    if (ans=="Y"){ 
        TCanvas* c2=new TCanvas("c2","c2",600,600);
        gPad->SetTicks(1,1);
        gPad->SetLeftMargin(0.15);
        gPad->SetRightMargin(0.15);
        c2->cd();
        int nbins=64;
        cout<<"The number of bins(A. 32; B. 64; C. 128; D. No rebin, but get plots; Other->Default(64))?";
        char opt=0;
        while((opt=getchar())<65);
        printf("Your option is %c=",opt);
        switch (opt){
        case 'a':
        case 'A':nbins=32;
               break;
        case 'b':
        case 'B':nbins=64;
               break;
        case 'c':
        case 'C':nbins=128;
               break;
        case 'd':
        case 'D':nbins=1024;
        }
        cout<<nbins<<endl;
        h205=rebin(data,h401name,nch1,nch2,Sub_Ped1,Sub_Ped2,nbins);

    TCanvas* c4=new TCanvas("c4","c4",600,600);
    gPad->SetTicks(1,1);
    gPad->SetLeftMargin(0.15);
        gPad->SetRightMargin(0.15);
    c4->cd();
    TH2F* h205c=(TH2F*)h205->Clone("h205c");
    h205c->GetXaxis()->SetRangeUser(100,1000);
    h205c->GetYaxis()->SetRangeUser(100,1000);
    h205c->SetStats(0);
    h205c->SetTitle("");
    h205c->GetXaxis()->SetTitle("3HF-WLS");
    h205c->GetYaxis()->SetTitle("CeF_{3}");
    h205c->GetXaxis()->SetLabelSize(0.03);
    h205c->GetYaxis()->SetLabelSize(0.03);
    h205c->GetXaxis()->SetTitleOffset(1.5);
    h205c->GetYaxis()->SetTitleOffset(1.5);
    h205c->GetYaxis()->CenterTitle();
    h205c->GetXaxis()->CenterTitle();
    h205c->Draw("lego2 0");
    TH2F* h205cc=(TH2F*)h205->Clone("h205cc");
    TCanvas* c3=new TCanvas("c3","c3",600,600);
    gPad->SetTicks(1,1);
    gPad->SetLeftMargin(0.15);
        gPad->SetRightMargin(0.15);

	h205cc->GetXaxis()->SetRangeUser(100..,1000.);
    h205cc->GetYaxis()->SetRangeUser(100,1000);
    h205cc->SetStats(0);
    h205cc->SetTitle("");
    h205cc->GetXaxis()->SetTitle("3HF-WLS");
    h205cc->GetYaxis()->SetTitle("CeF_{3}");
    h205cc->GetYaxis()->SetTitleOffset(1.5);
 h205cc->GetYaxis()->CenterTitle();
 h205cc->GetXaxis()->CenterTitle();

	c3->cd();
	h205cc->Draw("colz");
    TCanvas* c5 = new TCanvas("c5","c5",600,600);
    gPad->SetTicks(1,1);
    gPad->SetLeftMargin(0.15);
        gPad->SetRightMargin(0.15);
    c5->cd();
    gStyle->SetPalette(53);
    //ChangePalette();
    h205cc->Draw("CONT4 Z");
    //h205cc->Draw("CONT1 same");
   // h205cc->Draw("COL Z");
    TCanvas* c6 = new TCanvas("c6","c6",600,600);
    c6->cd();
    TH1D* px=h205cc->ProjectionX();
    px->SetLineWidth(2);
    px->Draw("HIST");
    TCanvas* c7 = new TCanvas("c7","c7",600,600);
    c7->cd();
    TH1D* py=h205cc->ProjectionY();
    py->SetLineWidth(2);
    py->Draw("HIST");
   
   //
    c1->SaveAs( (filename+ "_c1.pdf").c_str());
    c2->SaveAs( (filename+ "_c2.pdf").c_str());
    c3->SaveAs( (filename+ "_c3.pdf").c_str());
    c4->SaveAs( (filename+ "_c4.pdf").c_str());
    c5->SaveAs( (filename+ "_c5.pdf").c_str());
    c6->SaveAs( (filename+ "_c6.pdf").c_str());
    c7->SaveAs( (filename+ "_c7.pdf").c_str());

    }
    
    TFile* f1 = new TFile("ana2D.root","UPDATE");
    f1->WriteObject(h401,"h401");
    if (h205!=NULL) {
        f1->WriteObject(h205,"h205");
    }
    f1->Close();
    //Save Pdf

    printf("success\n");

    return 0;
}
