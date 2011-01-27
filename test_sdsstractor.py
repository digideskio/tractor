
import sys
from math import pi

import numpy as np
import pylab as plt

from astrometry.util.sip import Tan

from sdsstractor import *
#from compiled_profiles import *
#from galaxy_profiles import *

class FitsWcs(object):
	def __init__(self, wcs):
		self.wcs = wcs

	def positionToPixel(self, src, pos):
		x,y = self.wcs.radec2pixelxy(pos.ra, pos.dec)
		return x,y

	def pixelToPosition(self, src, xy):
		(x,y) = xy
		r,d = self.wcs.pixelxy2radec(x, y)
		return RaDecPos(r,d)

	def cdAtPixel(self, x, y):
		cd = self.wcs.cd
		return np.array([[cd[0], cd[1]], [cd[2],cd[3]]])


def main():
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option('-v', '--verbose', dest='verbose', action='count', default=0,
					  help='Make more verbose')
	opt,args = parser.parse_args()
	print 'Opt.verbose = ', opt.verbose
	if opt.verbose == 0:
		lvl = logging.INFO
	else: # opt.verbose == 1:
		lvl = logging.DEBUG
	logging.basicConfig(level=lvl, format='%(message)s', stream=sys.stdout)

	(images, simplexys, rois, zrange, nziv, footradecs
	 ) = prepareTractor(False, False)

	print 'Creating tractor...'
	tractor = SDSSTractor(images, debugnew=False, debugchange=True)

	'''
	step 19, change-011

	Changing source [131] PointSource at RA,Dec (120.5813, 9.3017) with SdssFlux: 2512.0 with scalar 373541.300971

	Pixel position in image 1: 162.38751309 22.0818652585

	* NGaussianPSF: sigmas [ 0.911, 2.687, 9.871, 7.172, 18.284 ], weights [ 1.005, 0.083, -0.032, -0.007, 0.138 ]
	* NGaussianPSF: sigmas [ 1.014, 1.507, 3.778, 4.812 ], weights [ 1.002, 0.037, 0.050, 0.065 ]
	'''
	pos = RaDecPos(120.5813, 9.3017)

	'''
	to   [ExpGalaxy(pos=RaDecPos(120.5813, 9.3017), flux=SdssFlux(2260.2), re=1.0, ab=0.50, phi=0.0)]
	-->
   ExpGalaxy at RA,Dec (120.5813, 9.3017) with SdssFlux: 3452.9, re=0.6, ab=0.88, phi=-0.1

  to   [DevGalaxy(pos=RaDecPos(120.5813, 9.3017), flux=SdssFlux(2260.2), re=1.0, ab=0.50, phi=0.0)]
   DevGalaxy at RA,Dec (120.5813, 9.3018) with SdssFlux: 5292.4, re=1.0, ab=1.24, phi=-0.0
	'''

	flux =  SdssFlux(3452.9 / SdssPhotoCal.scale)
	src = ExpGalaxy(pos, flux, 0.6, 0.88, -0.1)
	tractor.catalog.append(src)

	imgi = 1

	img = images[imgi]
	patch = src.getModelPatch(img)
	imargs1 = dict(interpolation='nearest', origin='lower')
	plt.clf()
	plt.imshow(patch.getImage(), **imargs1)
	plt.colorbar()
	plt.title('model')
	plt.savefig('eg-1.png')

	derivs = src.getParamDerivatives(img)
	for i,deriv in enumerate(derivs):
		plt.clf()
		plt.imshow(deriv.getImage(), **imargs1)
		plt.colorbar()
		plt.title('derivative ' + deriv.getName())
		plt.savefig('eg-deriv%i-0a.png' % i)

	chi = tractor.getChiImage(imgi)
	sl = patch.getSlice(img)

	plt.clf()
	plt.imshow(img.getImage()[sl], **imargs1)
	plt.colorbar()
	plt.title('image')
	plt.savefig('eg-image.png')

	plt.clf()
	plt.imshow(chi[sl], **imargs1)
	plt.colorbar()
	plt.title('chi')
	plt.savefig('eg-chi.png')
	
	for i,deriv in enumerate(derivs):
		plt.clf()
		(H,W) = chi.shape
		deriv.clipTo(W,H)
		sl = deriv.getSlice(chi)
		print 'slice', sl
		print 'deriv:', deriv
		print 'chi sliced:', chi[sl].shape
		print 'deriv:', deriv.getImage().shape
		plt.imshow(chi[sl] * deriv.getImage(), **imargs1)
		plt.colorbar()
		plt.title('chi * derivative ' + deriv.getName())
		plt.savefig('eg-chideriv%i-0a.png' % i)


	if False:
		src = PointSource(pos, SdssFlux(2512.0 / SdssPhotoCal.scale))
		tractor.catalog.append(src)
		x,y = images[1].getWcs().positionToPixel(src, pos)
		print 'Pixel position in image 1:', x,y
		tractor.changeSourceTypes(srcs=[src])


if __name__ == '__main__':

	main()
	sys.exit(0)

	angles = np.linspace(0, 2.*pi, 360)
	x,y = np.cos(angles), np.sin(angles)

	re = 3600./2. # arcsec
	ab = 0.5
	phi = 30. # deg

	abfactor = ab
	re_deg = re / 3600.
	phi = np.deg2rad(phi)

	# units of degrees
	G = np.array([[ re_deg * np.cos(phi), re_deg * np.sin(phi) ],
				  [ re_deg * abfactor * -np.sin(phi), re_deg * abfactor * np.cos(phi) ]])

	R = np.array([[ np.cos(phi),  np.sin(phi) ],
				  [-np.sin(phi),  np.cos(phi) ]])
	S = re_deg * np.array([[ 1., 0 ],
						   [ 0, abfactor ]])

	cp = np.cos(phi)
	sp = np.sin(phi)
	GG = re_deg * np.array([[ cp, sp * abfactor],
							[-sp, cp * abfactor]])

	print 'R', R
	print 'S', S

	RS = np.dot(R, S)

	print 'RS', RS

	print 'G', G
	#G = RS
	G = GG
	rd = np.dot(G, np.vstack((x,y)))
	print 'rd', rd.shape

	r = rd[0,:]
	d = rd[1,:]
	plt.clf()
	plt.plot(r, d, 'b-')
	plt.axis('equal')
	plt.savefig('g.png')


	width = (2./7.2) # in deg
	W,H = 500,500
	scale = width / float(W)
	cd = np.array([[-scale, 0],[0,-scale]])

	cdi = linalg.inv(cd)

	pg = np.dot(cdi, G)

	pxy = np.dot(pg, np.vstack((x,y)))
	px = pxy[0,:]
	py = pxy[1,:]
	plt.clf()
	plt.plot(px, py, 'b-')
	plt.axis('equal')
	plt.savefig('g2.png')
	

	T = np.dot(linalg.inv(G), cd)

	XX,YY = np.meshgrid(np.arange(-1000,1200, 200),
						np.arange( -600, 800, 200))
	XX = XX.ravel()
	YY = YY.ravel()
	XY = vstack((XX,YY))
	Tij = np.dot(T, XY)

	print 'Tij', Tij.shape
	for i in range(len(XX)):
		plt.text(XX[i], YY[i], '(%.1f,%.1f)' % (Tij[0,i], Tij[1,i]),
				 fontsize=8, ha='center', va='center')
	plt.savefig('g3.png')


	profile = CompiledProfile(modelname='exp', profile_func=profile_exp, re=100, nrad=4)

	#re_deg = 0.005 # 9 pix
	re_deg = 0.002 # 
	repix = re_deg / scale
	print 'repix', repix

	cp = np.cos(phi)
	sp = np.sin(phi)
	G = re_deg * np.array([[ cp, sp * abfactor],
						   [-sp, cp * abfactor]])
	T = np.dot(linalg.inv(G), cd)

	X = profile.sample_transform(T, repix, ab, W/2, H/2, W, H, 1,
								 debugstep=1)

	(xlo,xhi,ylo,yhi, cre,cn, cpixw, cpixh, re_factor, ab_factor,
	 Tij, ii, jj) = X
	print 'box size', cpixw, cpixh
	print 're_factor', re_factor
	print 'ab_factor', ab_factor

	plt.clf()
	plt.plot(Tij[0,:], Tij[1,:], 'b.')
	plt.title('Tij')
	plt.savefig('g4.png')

	plt.clf()
	plt.plot(ii, jj, 'b.')
	plt.savefig('g5.png')

	plt.clf()
	print 'boxes:', len(xlo)
	plt.plot(np.vstack((xlo,xhi,xhi,xlo,xlo)),
			 np.vstack((ylo,ylo,yhi,yhi,ylo)), 'b-')
	plt.savefig('g6.png')


	#sys.exit(0)

	ra,dec = 1.,45.
	width = (2./7.2) 	# in deg
	W,H = 500,500

	wcs = Tan()
	wcs.crval[0] = ra
	wcs.crval[1] = dec
	wcs.crpix[0] = W/2.
	wcs.crpix[1] = H/2.
	scale = width / float(W)
	wcs.cd[0] = -scale
	wcs.cd[1] = 0
	wcs.cd[2] = 0
	wcs.cd[3] = -scale
	wcs.imagew = W
	wcs.imageh = H

	wcs = FitsWcs(wcs)

	pos = RaDecPos(ra, dec)
	flux = SdssFlux(1e4)

	# arcsec
	repix = 25.
	re = 3600. * scale * repix
	ab = 0.5
	phi = 30.0
	
	eg = ExpGalaxy(pos, flux, re, ab, phi)

	image = np.zeros((H,W))
	invvar = np.zeros_like(image) + 1.
	photocal = SdssPhotoCal(SdssPhotoCal.scale)
	psf = NGaussianPSF([1.5], [1.0])
	sky = 0.
	img = Image(data=image, invvar=invvar, psf=psf, wcs=wcs, sky=sky,
				photocal=photocal)

	patch = eg.getModelPatch(img)

	imargs1 = dict(interpolation='nearest', origin='lower')

	plt.clf()
	plt.imshow(patch.getImage(), **imargs1)
	plt.colorbar()
	plt.savefig('eg-1.png')
	
