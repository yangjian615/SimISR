#!/usr/bin/env python
"""
Created on Wed May  6 13:55:26 2015
analysisplots.py
This module is used to plot the output from various stages of the simulator to debug
problems.
@author: John Swoboda
"""
import os
import matplotlib.pyplot as plt
from matplotlib import rc
import scipy as sp
import scipy.fftpack as scfft
import scipy.interpolate as spinterp

import numpy as np
import seaborn as sns
import pdb

from RadarDataSim.IonoContainer import IonoContainer
from RadarDataSim.utilFunctions import readconfigfile,spect2acf


def plotbeamparameters(param='Ne',ffit=None,fin=None,acfname=None):
    sns.set_style("whitegrid")
    sns.set_context("notebook")
    rc('text', usetex=True)

    fitdisp= ffit is not None
    indisp = ffit is not None
    acfdisp = acfname is not None

    if not param.lower()=='ne':
        acfdisp = False

    if acfdisp:
        Ionoacf = IonoContainer.readh5(acfname)
        dataloc = Ionoacf.Sphere_Coords
    if indisp:
        Ionoin = IonoContainer.readh5(fin)
    if fitdisp:
        Ionofit = IonoContainer.readh5(ffit)
        dataloc = Ionoacf.Sphere_Coords

    angles = dataloc[:,1:]
    b = np.ascontiguousarray(angles).view(np.dtype((np.void, angles.dtype.itemsize * angles.shape[1])))
    _, idx, invidx = np.unique(b, return_index=True,return_inverse=True)

    Neind = sp.argwhere(param==Ionofit.Param_Names)[0,0]
    beamnums = [0,1]
    beamlist = angles[idx]
    for ibeam in beamnums:
        curbeam = beamlist[ibeam]
        indxkep = np.argwhere(invidx==ibeam)[:,0]
        Ne_data = np.abs(Ionoacf.Param_List[indxkep,0,0])*2.0
        Ne_fit = Ionofit.Param_List[indxkep,0,Neind]
        rng= dataloc[indxkep,0]
        curlocs = dataloc[indxkep]
        origNe = np.zeros_like(Ne_data)
        rngin = np.zeros_like(rng)
        for ilocn,iloc in enumerate(curlocs):
            temparam,_,tmpsph = Ionoin.getclosestsphere(iloc)[:3]
            origNe[ilocn]=temparam[0,-1,0]
            rngin[ilocn] = tmpsph[0]
        print sp.nanmean(Ne_data/origNe)
        fig = plt.figure()
        plt.plot(Ne_data,rng,'bo',label='Data')
        plt.gca().set_xscale('log')
        plt.hold(True)
        plt.plot(origNe,rngin,'g.',label='Input')
        plt.plot(Ne_fit,rngin,'r*',label='Fit')
        plt.xlabel('$N_e$')
        plt.ylabel('Range km')
        plt.title('Ne vs Range for beam {0} {1}'.format(*curbeam))
        plt.legend(loc=1)

        plt.savefig('comp{0}'.format(ibeam))
        plt.close(fig)

def plotaltparameters(param='Ne',ffit=None,fin=None,acfname=None):
    sns.set_style("whitegrid")
    sns.set_context("notebook")
    rc('text', usetex=True)

    fitdisp= ffit is not None
    indisp = ffit is not None
    acfdisp = acfname is not None

    if not param.lower()=='ne':
        acfdisp = False

    if acfdisp:
        Ionoacf = IonoContainer.readh5(acfname)
        dataloc = Ionoacf.Sphere_Coords
    if indisp:
        Ionoin = IonoContainer.readh5(fin)
    if fitdisp:
        Ionofit = IonoContainer.readh5(ffit)
        dataloc = Ionoacf.Sphere_Coords

    angles = dataloc[:,1:]
    b = np.ascontiguousarray(angles).view(np.dtype((np.void, angles.dtype.itemsize * angles.shape[1])))
    _, idx, invidx = np.unique(b, return_index=True,return_inverse=True)

    Neind = sp.argwhere(param==Ionofit.Param_Names)[0,0]
    beamnums = [0,1]
    beamlist = angles[idx]
    for ibeam in beamnums:
        curbeam = beamlist[ibeam]
        indxkep = np.argwhere(invidx==ibeam)[:,0]
        Ne_data = np.abs(Ionoacf.Param_List[indxkep,0,0])*2.0
        Ne_fit = Ionofit.Param_List[indxkep,0,Neind]
        rng= dataloc[indxkep,0]
        curlocs = dataloc[indxkep]
        origNe = np.zeros_like(Ne_data)
        rngin = np.zeros_like(rng)
        for ilocn,iloc in enumerate(curlocs):
            temparam,_,tmpsph = Ionoin.getclosestsphere(iloc)[:3]
            origNe[ilocn]=temparam[0,-1,0]
            rngin[ilocn] = tmpsph[0]
        print sp.nanmean(Ne_data/origNe)
        fig = plt.figure()
        plt.plot(Ne_data,rng,'bo',label='Data')
        plt.gca().set_xscale('log')
        plt.hold(True)
        plt.plot(origNe,rngin,'g.',label='Input')
        plt.plot(Ne_fit,rngin,'r*',label='Fit')
        plt.xlabel('$N_e$')
        plt.ylabel('Range km')
        plt.title('Ne vs Range for beam {0} {1}'.format(*curbeam))
        plt.legend(loc=1)

        plt.savefig('comp{0}'.format(ibeam))
        plt.close(fig)

def plotspecs(coords,times,configfile,maindir,cartcoordsys = True, indisp=True,acfdisp= True,filetemplate='spec'):
    """ This will create a set of images that compare the input ISR spectrum to the
    Output ISR spectrum from the simulator.
    Inputs
    coords - An Nx3 numpy array that holds the coordinates of the desired points.
    times - A numpy list of times in seconds.
    configfile - The name of the configuration file used.
    cartcoordsys - (default True)A bool, if true then the coordinates are given in cartisian if
    false then it is assumed that the coords are given in sphereical coordinates.
    specsfilename - (default None) The name of the file holding the input spectrum.
    acfname - (default None) The name of the file holding the estimated ACFs.
    filetemplate (default 'spec') This is the beginning string used to save the images."""
#    indisp = specsfilename is not None
#    acfdisp = acfname is not None

    acfname = os.path.join(maindir,'ACF','00lags.h5')
    specsfiledir = os.path.join(maindir,'Spectrums')
    (sensdict,simparams) = readconfigfile(configfile)
    simdtype = simparams['dtype']
    npts = simparams['numpoints']*3.0
    amb_dict = simparams['amb_dict']
    if sp.ndim(coords)==1:
        coords = coords[sp.newaxis,:]
    Nt = len(times)
    Nloc = coords.shape[0]
    sns.set_style("whitegrid")
    sns.set_context("notebook")

    if indisp:
        dirlist = os.listdir(specsfiledir)
        timelist = sp.array([int(i.split()[0]) for i in dirlist])
        for itn,itime in enumerate(times):
            filear = sp.argwhere(timelist>=itime)
            if len(filear)==0:
                filenum = len(timelist)-1
            else:
                filenum = filear[0][0]
            specsfilename = os.path.join(specsfiledir,dirlist[filenum])
            Ionoin = IonoContainer.readh5(specsfilename)
            if itn==0:
                specin = sp.zeros((Nloc,Nt,Ionoin.Param_List.shape[-1])).astype(Ionoin.Param_List.dtype)
            omeg = Ionoin.Param_Names
            npts = Ionoin.Param_List.shape[-1]

            for icn, ic in enumerate(coords):
                if cartcoordsys:
                    tempin = Ionoin.getclosest(ic,times)[0]
                else:
                    tempin = Ionoin.getclosestsphere(ic,times)[0]
#                if sp.ndim(tempin)==1:
#                    tempin = tempin[sp.newaxis,:]
                specin[icn,itn] = tempin/npts/npts

    if acfdisp:
        Ionoacf = IonoContainer.readh5(acfname)
        ACFin = sp.zeros((Nloc,Nt,Ionoacf.Param_List.shape[-1])).astype(Ionoacf.Param_List.dtype)
        ts = Ionoacf.Param_Names[1]-Ionoacf.Param_Names[0]
        omeg = sp.arange(-sp.ceil((npts+1)/2),sp.floor((npts+1)/2))/ts/npts
        for icn, ic in enumerate(coords):
            if cartcoordsys:
                tempin = Ionoacf.getclosest(ic,times)[0]
            else:
                tempin = Ionoacf.getclosestsphere(ic,times)[0]
            if sp.ndim(tempin)==1:
                tempin = tempin[sp.newaxis,:]
            ACFin[icn] = tempin
        specout = scfft.fftshift(scfft.fft(ACFin,n=npts,axis=-1),axes=-1)


    nfig = sp.ceil(Nt*Nloc/6.0)
    imcount = 0

    for i_fig in sp.arange(nfig):
        lines = [None]*3
        labels = [None]*3
        (figmplf, axmat) = plt.subplots(2, 3,figsize=(16, 12), facecolor='w')
        axvec = axmat.flatten()
        for iax,ax in enumerate(axvec):
            if imcount>=Nt*Nloc:
                break
            iloc = int(sp.floor(imcount/Nt))
            itime = int(imcount-(iloc*Nt))

            maxvec = []

            if indisp:
                # apply ambiguity funciton to spectrum
                curin = specin[iloc,itime]
                rcs = curin.real.sum()
                (tau,acf) = spect2acf(omeg,curin)

                # apply ambiguity function
                tauint = amb_dict['Delay']
                acfinterp = sp.zeros(len(tauint),dtype=simdtype)

                acfinterp.real =spinterp.interp1d(tau,acf.real,bounds_error=0)(tauint)
                acfinterp.imag =spinterp.interp1d(tau,acf.imag,bounds_error=0)(tauint)
                # Apply the lag ambiguity function to the data
                guess_acf = sp.zeros(amb_dict['Wlag'].shape[0],dtype=sp.complex128)
                for i in range(amb_dict['Wlag'].shape[0]):
                    guess_acf[i] = sp.sum(acfinterp*amb_dict['Wlag'][i])

            #    pdb.set_trace()
                guess_acf = guess_acf*rcs/guess_acf[0].real

                # fit to spectrums
                spec_interm = scfft.fftshift(scfft.fft(guess_acf,n=npts))
                maxvec.append(spec_interm.real.max())
                lines[0]= ax.plot(omeg*1e-3,spec_interm.real,label='Input',linewidth=5)[0]
                labels[0] = 'Input Spectrum With Ambiguity Applied'
                normset = spec_interm.real.max()/curin.real.max()
                lines[1]= ax.plot(omeg*1e-3,curin.real*normset,label='Input',linewidth=5)[0]
                labels[1] = 'Input Spectrum'
            if acfdisp:
                lines[2]=ax.plot(omeg*1e-3,specout[iloc,itime].real,label='Output',linewidth=5)[0]
                labels[2] = 'Estimated Spectrum'
                maxvec.append(specout[iloc,itime].real.max())
            ax.set_xlabel('f in kHz')
            ax.set_ylabel('Amp')
            ax.set_title('Location {0}, Time {1}'.format(coords[iloc],times[itime]))
            ax.set_ylim(0.0,max(maxvec)*1.1)

            imcount=imcount+1
        figmplf.suptitle('Spectrum Comparison', fontsize=20)
        if None in labels:
            labels.remove(None)
            lines.remove(None)
        plt.figlegend( lines, labels, loc = 'lower center', ncol=5, labelspacing=0. )
        fname= filetemplate+'_{0:0>3}.png'.format(i_fig)
        plt.savefig(fname)
        plt.close(figmplf)

