
#include "TH2D.h"
#include "TH2F.h"
#include "TMath.h"

#include <iostream>
#include <cstdio>
#include <string>
#include <map>
#include <vector>


using namespace std;

void PrintStatusBar( float frac,int npoints=30 ){
	      string Status="\r[";
	      for (int i=0;i<npoints;i++){
		      if (i <= npoints*frac ) Status+="*";
		      else Status +="-";
		      }
	      Status += "]";
	      Status += Form(" %3.0f %%",(frac*100) );
	      fprintf(stdout,Status.c_str());
	      fflush(stdout);
	      return ;
}

TH2* kernelDensity(TH2* hData_rebin,float minInRadius,pair<float,float> xaxis, pair<float,float> yaxis){
	   string hDataName=hData_rebin->GetName();
	   TH2* hData_density=(TH2*)hData_rebin->Clone( (hDataName+"_density").c_str() );
	   int TotBins=hData_rebin->GetNbinsX()*hData_rebin->GetNbinsY();
	   float maxDensity=0;
	   for (int curXbin=1 ; curXbin<= hData_density->GetNbinsX()+1; curXbin++ ){
	      if ( hData_density->GetXaxis()->GetBinCenter(curXbin)< xaxis.first )continue;
	      if ( hData_density->GetXaxis()->GetBinCenter(curXbin)> xaxis.second )continue;
	      for (int curYbin=1 ;curYbin<= hData_density->GetNbinsY(); curYbin++){
	         if ( hData_density->GetYaxis()->GetBinCenter(curYbin)< yaxis.first) continue;
	         if ( hData_density->GetYaxis()->GetBinCenter(curYbin)> yaxis.second) continue;
	         int Tot=(curXbin-1)*hData_rebin->GetNbinsY() + curYbin-1;
	         PrintStatusBar( float(Tot)/float(TotBins) );
		 cout<< " "<<Tot<<" "<<TotBins;
	         float nInRadius=0;
	         float radius=0; 
	         float rStep=TMath::Sqrt(hData_density->GetYaxis()->GetBinWidth(curYbin)*hData_density->GetXaxis()->GetBinWidth(curXbin));
	         while (nInRadius < minInRadius && radius<5*rStep){
	               radius += rStep;
	               //for xbin in range(curXbin-bRadiusX,curXbin+bRadiusX+1):
	               //   for ybin in range(curYbin-bRadiusY,curYbin+bRadiusY+1):
	               nInRadius=0;
	               for (int xbin=1 ; xbin <= hData_density->GetNbinsX() ; xbin++)
	                  for (int ybin=1 ; ybin <= hData_density->GetNbinsY(); ybin++){
	   		       float dx=hData_density->GetXaxis()->GetBinCenter(xbin) - hData_density->GetXaxis()->GetBinCenter(curXbin);
	   		       float dy=hData_density->GetYaxis()->GetBinCenter(ybin) - hData_density->GetYaxis()->GetBinCenter(curYbin);
	   		       if (dx*dx + dy*dy  <= radius *radius)
	   			       nInRadius += hData_rebin->GetBinContent(xbin,ybin);
			       } //end double for
			}//end while, look for radius

	         //cout <<" Radius is "<<radius<< " nInRadius is "<<nInRadius;

	         //current=nInRadius;
	         float current=0;
	         for ( int xbin=1; xbin <=hData_density->GetNbinsX(); xbin++){
	   	        float dx=hData_density->GetXaxis()->GetBinCenter(xbin) - hData_density->GetXaxis()->GetBinCenter(curXbin);
	   	        if (dx > 5*radius) continue;
	                for ( int ybin=1; ybin <= hData_density->GetNbinsY(); ybin++){
	   	               float dy=hData_density->GetYaxis()->GetBinCenter(ybin) - hData_density->GetYaxis()->GetBinCenter(curYbin);
	   	               if (dy > 5*radius) continue;
	         	       if (dx*dx+dy*dy > 5*radius) continue ;//avoid extremely distant points
		               if  (hData_rebin->GetBinContent(xbin,ybin)> 0)
	   	       	       		current += hData_rebin->GetBinContent(xbin,ybin) * TMath::Exp( - (dx*dx+dy*dy)/(radius*radius) );
			}//end ybin
		 }//end xbin
		 //current /= 2 *TMath::Pi() ; // integral of gaus

	         current /= (radius * radius);
		 current *= rStep*rStep; //restore #bins
		 //cout <<" current is "<<current;
	         hData_density->SetBinContent(curXbin,curYbin,current);
		 if (current > maxDensity) maxDensity=current;
	   } //end curYbin
	}//end curXbin
hData_density->SetMaximum(maxDensity); 
return  hData_density;
}
