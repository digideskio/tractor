from __future__ import print_function
if __name__ == '__main__':
	import matplotlib
	matplotlib.use('Agg')

import os
import numpy as np
import pyfits

from astrometry.util.util import Tan

from tractor.sdss import *
from tractor.galaxy import *

def addexpgal(x, y, flux, re, ab, theta, wcs, tractor):
	rd1 = wcs.pixelToPosition(x, y)
	g1 = ExpGalaxy(rd1, Flux(flux), re, ab, theta)
	tractor.catalog.append(g1)

def addstar(x, y, flux, wcs, tractor):
	rd1 = wcs.pixelToPosition(x, y)
	s1 = PointSource(rd1, Flux(flux))
	tractor.catalog.append(s1)

def gettractor():
	W,H = 200,200
	image = np.zeros((H,W))
	invvar = np.zeros_like(image) + 1.

	ra,dec = 0,0
	# arcsec/pix
	pixscale = 1.
	wcs1 = Tan(ra, dec, W/2, H/2,
			   -pixscale/3600., 0, 0, -pixscale/3600., W, H)
	wcs = FitsWcs(wcs1)
	photocal = NullPhotoCal()
	psf = NCircularGaussianPSF([1.], [1.])
	sky = ConstantSky(0.)
	
	img = Image(data=image, invvar=invvar, psf=psf,
				wcs=wcs, sky=sky, photocal=photocal)
	tractor = SDSSTractor([img])
	return tractor,wcs

def writeimg(tractor, visit):
	dirnm = 't%04i' % visit
	if not os.path.exists(dirnm):
		print('Creating director', dirnm)
		os.mkdir(dirnm)

	mods = tractor.getModelImages()
	mod = mods[0]

	img = tractor.getImage(0)
	noise = np.random.normal(size=img.shape) * (1./img.getInvError())
	wcs1 = img.getWcs().wcs
	(H,W) = img.shape

	args = dict(interpolation='nearest', origin='lower')
	plt.clf()
	plt.imshow(mod, **args)
	plt.gray()
	plt.colorbar()
	fn = os.path.join(dirnm, 'mod.png')
	plt.savefig(fn)
	print('wrote', fn)

	plt.clf()
	plt.imshow(mod + noise, **args)
	plt.gray()
	plt.colorbar()
	fn = os.path.join(dirnm, 'mod2.png')
	plt.savefig(fn)
	print('wrote', fn)

	wcs1.write_to('wcs.fits')
	hdr = pyfits.open('wcs.fits')[0].header

	mask = np.zeros((H,W), np.int16)
	var = 1./img.getInvError()**2

	if False:
		pyfits.writeto('t_img.fits', mod, header=hdr, clobber=True)
		pyfits.writeto('t_msk.fits', mask, clobber=True)
		pyfits.writeto('t_var.fits', var, clobber=True)

	hdus = pyfits.HDUList([pyfits.PrimaryHDU(header=hdr),
						   pyfits.ImageHDU((mod + noise).astype(np.float32), header=hdr),
						   pyfits.ImageHDU(mask),
						   pyfits.ImageHDU(var.astype(np.float32))])
	fn = os.path.join(dirnm, 't.fits')
	hdus.writeto(fn, clobber=True)
	print('wrote', fn)

	fn = os.path.join(dirnm, 'srcs.fits')
	srcs = tractor.getCatalog()
	sx,sy = [],[]
	wcs = img.getWcs()
	for src in srcs:
		x,y = wcs.positionToPixel(src.getPosition(), src)
		sx.append(x)
		sy.append(y)
	tab = pyfits.new_table([
		pyfits.Column(name='X', format='E', array=np.array(sx)),
		pyfits.Column(name='Y', format='E', array=np.array(sy)),])
	tab.writeto(fn, clobber=True)
	print('Wrote', fn)

# two galaxies, bright & fairly well separated
def test0():
	tractor,wcs = gettractor()
	addexpgal( 85., 100., 1e5, 20., 0.5,  0., wcs, tractor)
	addexpgal(115., 100., 1e5, 20., 0.5, 90., wcs, tractor)
	writeimg(tractor, 0)

# closer together
def test1():
	tractor,wcs = gettractor()
	addexpgal( 90., 100., 1e5, 20., 0.5,  0., wcs, tractor)
	addexpgal(110., 100., 1e5, 20., 0.5, 90., wcs, tractor)
	writeimg(tractor, 1)

# fainter
def test2():
	tractor,wcs = gettractor()
	addexpgal( 90., 100., 1e4, 20., 0.5,  0., wcs, tractor)
	addexpgal(110., 100., 1e4, 20., 0.5, 90., wcs, tractor)
	writeimg(tractor, 2)

# galaxy + 2 point sources
def test3():
	tractor,wcs = gettractor()
	addexpgal( 90., 100., 1e5, 20., 0.5,  0., wcs, tractor)
	addstar(90., 120., 1e3, wcs, tractor)
	addstar(100.5,  100.25, 1e3, wcs, tractor)
	addstar(100.0,  110.25, 1e3, wcs, tractor)
	addstar(100.75,  80.25, 1e3, wcs, tractor)
	writeimg(tractor, 3)


def test10():
	tractor,wcs = gettractor()
	S = 40.
	X = np.arange(S/2., 200, S)
	Y = np.arange(S/2., 200, S)
	for i,x in enumerate(X):
		for j,y in enumerate(Y):
			ab = (i+0.5)/len(X)
			theta = (j+0.5)/len(Y) * 90.
			print('ab', ab, 'theta', theta)
			addexpgal(x, y, 1e5, 20., ab,  theta, wcs, tractor)
	writeimg(tractor, 10)

def test11():
	tractor,wcs = gettractor()
	S = 40.
	X = np.arange(S/2., 200, S)
	Y = np.arange(S/2., 200, S)
	for i,x in enumerate(X):
		for j,y in enumerate(Y):
			ab = (i+0.5)/len(X) * 0.33
			theta = (j+0.5)/len(Y) * 90.
			print('ab', ab, 'theta', theta)
			addexpgal(x, y, 1e6 * np.sqrt(ab), 20., ab,  theta, wcs, tractor)
	writeimg(tractor, 11)

def test2x():
	ab = 0.4
	tstep = 18.
	for i in range(10):
		theta = tstep * i
		tractor,wcs = gettractor()
		addexpgal(100., 100., 1e6 * np.sqrt(ab), 20., ab,  theta, wcs, tractor)
		writeimg(tractor, 20 + i)



if __name__ == '__main__':
	#test0()
	#test1()
	test2()
	test3()
	#test2x()
	#test10()
	test11()
	
			
