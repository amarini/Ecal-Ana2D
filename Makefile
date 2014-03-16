SrcSuf        = cc
HeadSuf       = h
ObjSuf        = o
DepSuf        = d
DllSuf        = so

.SUFFIXES: .$(SrcSuf) .$(ObjSuf) .$(DllSuf)

##
## Flags and external dependecies
## 
LDFLAGS       = -O
SOFLAGS       = -fPIC -shared
LD            = g++
CXX           = g++
ROOFIT_BASE=$(ROOFITSYS)


LDFLAGS+=-L$(ROOFIT_BASE)/lib $(ROOTLIBS) -lz -lRooUnfold
#LDFLAGS+=-lRooFitCore -lRooFit 
#LDFLAGS+= -lTMVA
CXXFLAGS+=-I$(ROOFIT_BASE)/include
CXXFLAGS+= `root-config --cflags`
CXXFLAGS+=-I$(shell pwd) -g
CXXFLAGS+= -O -fPIC
ROOTLIBS=`root-config --libs`
LDFLAGS+=$(ROOTLIBS)

SHELL=bash

BASEDIR = $(shell pwd)


BINDIR = $(BASEDIR)/bin
SRCDIR = $(BASEDIR)/src
HEADDIR = $(BASEDIR)/interface

$(shell mkdir -p $(BINDIR) )

#Packages=GlobalContainer Unfolding
## Sort needed for building libraries: LAST <- FIRST
.PHONY: all
all:fancyPalette_C.so kernelDensity_C.so  Get_rootfile_C.so

%_C.so: src/%.C
	echo -e ".L $^++ \n .q" | root  -l -b -
	mv src/$@ ./


