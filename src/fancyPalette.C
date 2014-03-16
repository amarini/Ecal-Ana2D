#include "TROOT.h"
#include "TStyle.h"
#include "TColor.h"
#include "TCanvas.h"
#include "TColor.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TH1D.h"
#include "TH2D.h"

#include <iostream>
using namespace std;

class rgb{
public:
	rgb(Int_t color){SetColor(color);}
	Float_t r;
	Float_t g;
	Float_t b;
	int SetColor(Int_t color)
		{gROOT->GetColor(color)->GetRGB(r,g,b);}
};

Int_t MyPalette[1000];

void ChangePalette(){
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
	rgb black(kBlack);
	rgb darkBlue(kBlue+2);
	rgb orange(kOrange);
	rgb yellow(kYellow);
	rgb red(kRed);
	rgb darkRed(kRed+2);
	rgb white(kWhite);
   	//gROOT->GetColor(kBlack)->GetRGB(r,g,b)
   Double_t r[]    = {white.r, yellow.r, orange.r,   red.r, darkRed.r,  black.r };
   Double_t g[]    = {white.g, yellow.g, orange.g,   red.g, darkRed.g,  black.g };
   Double_t b[]    = {white.b, yellow.b, orange.b,   red.b, darkRed.b,  black.b };
   Double_t stop[] = {0.,      0.30,      .50,       .75,      .95,      1.0};
   for(int i=0;i<6;i++)
	   cout<< "RGB will be setted to "<<r[i]<<":"<<g[i]<<":"<<b[i]<<endl;
   Int_t FI = TColor::CreateGradientColorTable(6, stop, r, g, b, 255);
      //for (int i=0;i<100;i++) MyPalette[i] = FI+i

//Later on to reuse the palette MyPalette it will be enough to do
  // gStyle->SetPalette(100, MyPalette);
   gStyle->SetNumberContours(99);
}

void DarkBodyRadiator(){
// set Dark Body Radiator palette
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
      TColor::InitializeColors();
      const Int_t nRGBs = 5;
      Double_t stops[nRGBs] = { 0.00, 0.45, 0.80, 0.90, 1.00};
      Double_t red[nRGBs]   = { 0.00, 0.50, 1.00, 1.00, 1.00};
      Double_t green[nRGBs] = { 0.00, 0.00, 0.55, 1.00, 1.00};
      Double_t blue[nRGBs]  = { 0.00, 0.00, 0.00, 0.00, 1.00};
      TColor::CreateGradientColorTable(nRGBs, stops, red, green, blue, 255);
      int paletteType = 5;
      gStyle->SetNumberContours(99);
      //gStyle->SetAxisColor(kGray+3,"XY");
      return;
}

#include "TRandom3.h"
void TestPalette(){
//	ChangePalette();
	DarkBodyRadiator();
	TH2D *h=new TH2D("h","h",200,-5,5,100,-5,5);
	h->FillRandom("gaus",500000);
	h->Sumw2();
	for(int i=1;i<h->GetNbinsX();i++)
	for(int j=1;j<h->GetNbinsY();j++)
		if(h->GetBinContent(i,j)<0.001){h->SetBinContent(i,j,0.0);h->SetBinError(i,j,1);}
	TCanvas *c=new TCanvas("c","c");
	c->Divide(2);
	c->cd(1);
	h->Draw("COL  Z");
	//h->GetZaxis()->SetRangeUser(0,h->GetMaximum());
	c->cd(2);
	h->Draw("CONT4 Z");

}
