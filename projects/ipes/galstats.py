from __future__ import print_function
import os
import sys
from math import ceil
from glob import glob
import matplotlib
matplotlib.use('Agg')
from astrometry.util.pyfits_utils import *
from astrometry.util.plotutils import *
from astrometry.util.file import *
from astrometry.util.starutil_numpy import *
from astrometry.sdss import *
import pylab as plt
import numpy as np

from tractor.sdss import *
from tractor import *

def plots1():

	"""
	select fracdev_r,exprad_r,expab_r,expmag_r,expphi_r,run,camcol,field into mydb.exp3818
	from Galaxy where run=3818
	and clean=1 and probpsf=0
	and (flags & (dbo.fPhotoFlags('BINNED1'))) = (dbo.fPhotoFlags('BINNED1'))
	and (flags & (dbo.fPhotoFlags('INTERP') | dbo.fPhotoFlags('BLENDED') |
    dbo.fPhotoFlags('BINNED2') | dbo.fPhotoFlags('MOVED') | dbo.fPhotoFlags('DEBLENDED_AT_EDGE') |
    dbo.fPhotoFlags('MAYBE_CR') | dbo.fPhotoFlags('MAYBE_EGHOST'))) = 0
    and fracdev_r < 0.5
	=> exp3818_dstn.fit

	select fracdev_r,exprad_r,expab_r,expmag_r,expphi_r,run,camcol,field,ra,dec into mydb.exp3818
	from Galaxy where
	run=3818
	and camcol=2
	and clean=1 and probpsf=0
	and (flags & (dbo.fPhotoFlags('BINNED1'))) = (dbo.fPhotoFlags('BINNED1'))
	and (flags & (dbo.fPhotoFlags('INTERP') | dbo.fPhotoFlags('BLENDED') |
    dbo.fPhotoFlags('BINNED2') | dbo.fPhotoFlags('MOVED') | dbo.fPhotoFlags('DEBLENDED_AT_EDGE') |
    dbo.fPhotoFlags('MAYBE_CR') | dbo.fPhotoFlags('MAYBE_EGHOST'))) = 0
	and fracdev_r < 0.5
	and exprad_r between 0.4 and 0.55
	and expmag_r between 21 and 22
	=> exp3818b.fits

	select fracdev_i,exprad_i,expab_i,expmag_i,expphi_i,run,camcol,field,ra,dec into mydb.exp3818i
	from Galaxy where run=3818 and camcol=2
    and clean=1 and probpsf=0
	and (flags & (dbo.fPhotoFlags('BINNED1'))) = (dbo.fPhotoFlags('BINNED1'))
	and (flags & (dbo.fPhotoFlags('INTERP') | dbo.fPhotoFlags('BLENDED') |
	dbo.fPhotoFlags('BINNED2') | dbo.fPhotoFlags('MOVED') | dbo.fPhotoFlags('DEBLENDED_AT_EDGE') |
	dbo.fPhotoFlags('MAYBE_CR') | dbo.fPhotoFlags('MAYBE_EGHOST'))) = 0
	and fracdev_i < 0.5
	=> exp3818i.fits

	
	"""
	
	T=fits_table('exp3818_dstn.fit')

	plt.clf()
	H,xe,ye = np.histogram2d(np.log10(T.exprad_r), T.expmag_r, 200, range=((np.log10(0.1),np.log10(10)),(15,22)))
	plt.imshow(H.T, extent=(xe[0],xe[-1],ye[0],ye[-1]), aspect='auto', origin='lower', interpolation='nearest')
	plt.colorbar()
	plt.savefig('radi-mag1.png')
	
	return




	plt.clf()
	n,b,p = plt.hist(np.log10(T.exprad_r), 100, range=(np.log10(0.1), np.log10(10.)))
	plt.xlabel('log r_e')
	plt.ylabel('number of galaxies')
	plt.title('Run 3818: total %i' % sum(n))
	plt.savefig('rad1.png')

	plt.clf()
	plt.hist(T.exprad_r, 100, range=(0.4, 0.55))
	plt.xlim(0.4, 0.55)
	plt.savefig('rad2.png')

	plt.clf()
	H,xe,ye = np.histogram2d(T.exprad_r, T.expmag_r, 200, range=((0.4,0.55),(20,22)))
	plt.imshow(H.T, extent=(xe[0],xe[-1],ye[0],ye[-1]), aspect='auto', origin='lower', interpolation='nearest')
	plt.colorbar()
	plt.savefig('rad-mag.png')

	T2 = T[(T.expmag_r > 21) * (T.expmag_r < 22)]
	print(len(T2), 'in mag 21-22 range')
	T2 = T2[(T2.exprad_r >= 0.4) * (T2.exprad_r <= 0.55)]
	print(len(T2), 'in radius 0.4-0.55 range')

	#for cc in np.unique(T2.camcol):
	#	n = sum(T2.camcol == cc)
	#	print n, 'in camcol', cc

	T2 = T2[T2.camcol == 2]
	print(len(T2), 'in camcol 2')
	print('Fields:', min(T2.field), max(T2.field))
	T2.about()
	plt.clf()
	H,xe,ye = np.histogram2d(T2.exprad_r, T2.expmag_r, 200, range=((0.4,0.55),(21,22)))
	plt.imshow(H.T, extent=(xe[0],xe[-1],ye[0],ye[-1]), aspect='auto', origin='lower', interpolation='nearest')
	plt.colorbar()
	plt.savefig('rad-mag2.png')

	plt.clf()
	n,b,p = plt.hist(T2.exprad_r, 100, range=(0.4, 0.55))
	print(sum(n), 'counts plotted')
	plt.xlim(0.4, 0.55)
	plt.title('Run 3818, Camcol 2: total %i' % sum(n))
	plt.xlabel('exp r_e (arcsec)')
	plt.ylabel('number of galaxies')
	plt.savefig('rad3.png')

	plt.clf()
	plt.hist(T2.exprad_r, 300, range=(0.4, 0.55))
	plt.xlim(0.4, 0.55)
	plt.savefig('rad4.png')

	T2 = T2[(T2.field >= 100) * (T2.field < 200)]
	print(len(T2), 'in fields [100, 200)')

	plt.clf()
	n,b,p = plt.hist(T2.exprad_r, 100, range=(0.4, 0.55))
	plt.xlim(0.4, 0.55)
	plt.title('Run 3818, Camcol 2, Fields 100-200: total %i' % sum(n))
	plt.xlabel('exp r_e (arcsec)')
	plt.ylabel('number of galaxies')
	plt.savefig('rad5.png')

def plots2(rlo=1.3, rhi=1.5, fn='exp3818i_dstn.fit',
		   maxmag=20):
	T = fits_table(fn)
	print('Read', len(T))
	T.cut(T.fracdev_i == 0)
	print('Cut to', len(T), 'pure-exp')

	plt.clf()
	H,xe,ye = np.histogram2d(T.exprad_i, T.expmag_i, 200, range=((0.1,10),(15,22)))
	plt.imshow(H.T, extent=(xe[0],xe[-1],ye[0],ye[-1]), aspect='auto', origin='lower', interpolation='nearest')
	plt.colorbar()
	plt.savefig('rad-mag1.png')

	plt.clf()
	n,b,p = plt.hist(np.log10(T.exprad_i), 100, range=(np.log10(0.1), np.log10(10.)))
	plt.xlabel('log r_e')
	plt.ylabel('number of galaxies')
	plt.title('Run 3818, i-band, total %i' % sum(n))
	plt.savefig('radi1.png')

	plt.clf()
	n,b,p = plt.hist(T.exprad_i, 100, range=(rlo, rhi))
	plt.xlabel('r_e (arcsec)')
	plt.ylabel('number of galaxies')
	plt.title('Run 3818, i-band, total %i' % sum(n))
	plt.xlim(rlo, rhi)
	plt.savefig('radi2.png')

	T2 = T[(T.exprad_i >= rlo) * (T.exprad_i <= rhi)]
	print(len(T2), 'in radius range')
	T2 = T2[T2.expmag_i < maxmag]
	print(len(T2), 'in mag range')

	T2.band = np.array(['i']*len(T2))

	T2.writeto('exp3818c.fits')

	plt.clf()
	n,b,p = plt.hist(T2.exprad_i, 100, range=(rlo, rhi))
	plt.xlabel('r_e (arcsec)')
	plt.ylabel('number of galaxies')
	plt.title('Run 3818, i-band, mag < %g, total %i' % (maxmag,sum(n)))
	plt.xlim(rlo, rhi)
	plt.savefig('radi3.png')

	plt.clf()
	H,xe,ye = np.histogram2d(T2.exprad_i, T2.expmag_i, 200, range=((rlo,rhi),(15,maxmag)))
	plt.imshow(H.T, extent=(xe[0],xe[-1],ye[0],ye[-1]), aspect='auto', origin='lower', interpolation='nearest')
	plt.colorbar()
	plt.savefig('radi-mag2.png')


	"""
	select fracdev_i,exprad_i,expab_i,expmag_i,expphi_i,run,camcol,field,ra,dec into mydb.exp3818i_dr7
	from Galaxy where run=3818
    and probpsf=0
	and (flags & (dbo.fPhotoFlags('BINNED1'))) = (dbo.fPhotoFlags('BINNED1'))
	and (flags & (dbo.fPhotoFlags('INTERP') | dbo.fPhotoFlags('BLENDED') |
	dbo.fPhotoFlags('BINNED2') | dbo.fPhotoFlags('MOVED') | dbo.fPhotoFlags('DEBLENDED_AT_EDGE') |
	dbo.fPhotoFlags('MAYBE_CR') | dbo.fPhotoFlags('MAYBE_EGHOST'))) = 0
	and fracdev_i < 0.1
	## In DR7 context of SDSS3 CAS
	=> exp3818i_dr7.fits
	"""

def stage00():
	#T = fits_table('exp3818b.fits')
	T = fits_table('exp3818c.fits')
	print(len(T), 'galaxies')

	sdss = DR7()
	dn = 'paper0-data'
	if not os.path.exists(dn):
		os.mkdir(dn)
	sdss.setBasedir(dn)

	#band = 'r'

	# radius in pixels of ROI; max r_e = 0.55 arcsec, 8 r_e
	sz = int(ceil(0.55 * 8 / 0.396))
	#sz = 1.5 * 8 / 0.396
	tractors = []
	for i,(run,camcol,field,ra,dec) in enumerate(zip(T.run, T.camcol, T.field, T.ra, T.dec)):
		if hasattr(T, 'band'):
			band = T.band[i]
		else:
			band = 'r'
		print()
		print('Galaxy', (i+1), 'of', len(T))
		im,info = get_tractor_image(run, camcol, field, band, sdssobj=sdss, useMags=True,
									roiradecsize=(ra,dec,sz))
		sky,skysig = info['sky'],info['skysig']
		pa = dict(origin='lower', interpolation='nearest', vmin=sky-3*skysig, vmax=sky+10*skysig)
		plt.clf()
		plt.imshow(im.data, **pa)
		plt.savefig('gs-%03i-data.png' % i)

		roi = info['roi']
		srcs = get_tractor_sources(run, camcol, field, band, bands=[band], sdss=sdss, roi=roi)
		tractor = Tractor([im], srcs)
		synth = tractor.getModelImage(im)
		plt.clf()
		plt.imshow(synth, **pa)
		plt.savefig('gs-%03i-initial.png' % i)
		tractors.append(tractor)
	return dict(tractor=tractors, T=T)

def stage01(tractor=None, T=None):
	# typo
	tractors = tractor
	print('Tractors:', len(tractors))
	print('targets:', len(T))
	allsrcs = []
	srcs = []
	keepi = []
	for i,t in enumerate(tractors):
		cat = t.getCatalog()
		allsrcs.extend(cat)
		cat = [src for src in cat if type(src) is ExpGalaxy]
		if len(cat) == 0:
			continue
		if len(cat) > 1:
			print(len(cat), 'exps:')
			for src in cat:
				print('  ', src)
			dists = [arcsec_between(T.ra[i], T.dec[i], src.pos.ra, src.pos.dec)
					 for src in cat]
			print('Distances from target:', dists)
			I = np.argmin(dists)
			print('Keeping:', cat[I])
			cat = [cat[I]]
			
		srcs.extend(cat)
		keepi.append(i)
	keepi = np.array(keepi)
	T = T[keepi]
	print('all sources:', len(allsrcs))
	types = [type(src) for src in allsrcs]
	print('Source types:', np.unique(types))

	print('keeping', len(srcs), 'exp galaxies')

	rads = [src.shape.re for src in srcs]
	plt.clf()
	plt.hist(rads, 200)
	plt.xlabel('tsObj r_e')
	plt.savefig('re1.png')

	plt.clf()
	plt.hist(T.exprad_i, 200)
	plt.xlabel('CAS r_e')
	plt.savefig('re2.png')

	plt.clf()
	plt.xlabel('CAS r_e')
	plt.ylabel('tsObj r_e')
	plt.plot(T.exprad_i, rads, 'r.')
	plt.savefig('re3.png')

	dn = 'paper0-data'
	if not os.path.exists(dn):
		os.mkdir(dn)
	sdss = DR7(basedir=dn)

	dn = 'paper0-data-dr8'
	if not os.path.exists(dn):
		os.mkdir(dn)
	dr8 = DR8(basedir=dn)

	t = T[0]
	print(t)
	t.about()
	s8 = get_tractor_sources_dr8(t.run, t.camcol, t.field, t.band, sdss=dr8)
	i8 = get_tractor_image_dr8(t.run, t.camcol, t.field, t.band, sdss=dr8)


	# fns = glob('paper0-data/tsObj-003818-*.fit')
	# fns.sort()
	# fns = fns[:100]

	trads = []
	frads = []

	alltrads = []
	allfrads = []
	allfrads8 = []
	allprads8 = []

	for t in T[:100]:
		fn = sdss.getPath('tsObj', t.run, t.camcol, t.field, t.band)
		print(fn)
		ts = fits_table(fn)
		ts.index = np.arange(len(ts))
		tsid = ts.id
		print('  ', len(ts))
		B = 3
		#ts.cut(ts.fracdev[:,B] == 0)
		ts.cut(ts.fracpsf[:,B] == 0)
		ts.cut(ts.prob_psf[:,B] == 0)
		print('  exp -> ', len(ts))
		m = ts.counts_exp[:,B]
		# it's actually a mag, not counts
		ts.cut(m < 20.2)
		print('  mag -> ', len(ts))
		r = ts.r_exp[:,B]
		allI = ts.index
		alltrads.append(r)
		ts.cut((r >= 0.4) * (r <= 0.55))
		print('  rad -> ', len(ts))
		r = ts.r_exp[:,B]
		r = np.array(r)
		r.sort()
		print(r)
		trads.append(r)

		sdss.retrieve('fpObjc', t.run, t.camcol, t.field, t.band)
		fn = sdss.getPath('fpObjc', t.run, t.camcol, t.field, t.band)
		print(fn)
		fp = fits_table(fn)
		print('  ', len(fp))
		#fp.about()
		fpid = fp.id
		assert(all(fpid == tsid))
		fp1 = fp[ts.index]
		tsid = ts.id
		fpid = fp1.id
		assert(all(fpid == tsid))
		frads.append(fp1.r_exp[:,B])
		allfrads.append(fp[allI].r_exp[:,B])


		fn = dr8.retrieve('fpObjc', t.run, t.camcol, t.field, t.band)
		print(fn)
		fp = fits_table(fn)
		print('fpObjc:', fp)
		if fp is None:
			print('Warning:', fn, 'is None: maybe has 0 rows?')
			continue
		print('  ', len(fp))
		#fpid = fp.id
		#assert(all(fpid == tsid))
		#fp1 = fp[ts.index]
		#tsid = ts.id
		#fpid = fp1.id
		#assert(all(fpid == tsid))
		#frads.append(fp1.r_exp[:,B])

		fp.cut(fp.fracpsf[:,B] == 0)
		fp.cut(fp.prob_psf[:,B] == 0)
		print('  exp -> ', len(fp))
		c= fp.counts_exp[:,B]
		fp.cut(c > 10)
		print('  mag -> ', len(fp))
		r = fp.r_exp[:,B]
		allfrads8.append(r)

		fn = dr8.retrieve('photoObj', t.run, t.camcol, t.field)#, t.band)
		print(fn)
		fp = fits_table(fn)
		print('photoObj', fp)
		if fp is None:
			print('Warning:', fn, 'is None: maybe has 0 rows?')
			continue
		print('  ', len(fp))
		fp.cut(fp.fracdev[:,B] == 0)
		fp.cut(fp.prob_psf[:,B] == 0)
		print('  exp -> ', len(fp))
		c = fp.expmag[:,B]
		fp.cut(c < 20.2)
		print('  mag -> ', len(fp))
		r = fp.theta_exp[:,B]
		allprads8.append(r)





	trads = np.hstack(trads)
	plt.clf()
	plt.hist(trads, 200)
	plt.xlabel('tsObj direct r_e')
	plt.savefig('re4.png')
	
	frads = np.hstack(frads)
	plt.clf()
	plt.hist(frads, 200)
	plt.xlabel('fpObjc direct r_e')
	plt.savefig('re5.png')

	plt.clf()
	plt.plot(frads, trads, 'r.')
	plt.xlabel('fpObjc r_e')
	plt.ylabel('tsObj r_e')
	plt.savefig('re6.png')

	alltrads = np.hstack(alltrads)
	plt.clf()
	plt.hist(alltrads, 200)
	plt.xlabel('tsObj r_e')
	plt.savefig('re7.png')
	
	allfrads = np.hstack(allfrads)
	plt.clf()
	plt.hist(allfrads, 200)
	plt.xlabel('fpObjc r_e')
	plt.savefig('re8.png')

	plt.clf()
	plt.plot(allfrads, alltrads, 'r.')
	plt.xlabel('fpObjc r_e')
	plt.ylabel('tsObj r_e')
	plt.savefig('re9.png')

	allfrads8 = np.hstack(allfrads8)
	plt.clf()
	plt.hist(allfrads8, 200)
	plt.xlabel('fpObjc r_e')
	plt.title('DR8')
	plt.savefig('re10.png')

	plt.clf()
	#I = (allfrads8 >= (0.4 / 0.396)) * (allfrads8 <= (0.55 / 0.396))
	plt.hist(allfrads8, 200, range=(0.4 / 0.396, 0.55 / 0.396))
	plt.xlabel('fpObjc r_e')
	plt.title('DR8')
	plt.savefig('re11.png')

	allprads8 = np.hstack(allprads8)
	plt.clf()
	plt.hist(allprads8, 200)
	plt.xlabel('photoObj r_e')
	plt.title('DR8')
	plt.savefig('re12.png')

	plt.clf()
	plt.hist(allprads8, 200, range=(0.4, 0.55))
	plt.xlabel('photoObj r_e')
	plt.title('DR8')
	plt.savefig('re13.png')




def runstage(stage, force=[], threads=1):
	print('Runstage', stage)
	pfn = 'gs-%02i.pickle' % stage
	if os.path.exists(pfn):
		if stage in force:
			print('Ignoring pickle', pfn, 'and forcing stage', stage)
		else:
			print('Reading pickle', pfn)
			R = unpickle_from_file(pfn)
			return R
	if stage > 0:
		# Get prereqs
		P = runstage(stage-1)
	else:
		P = {}
	print('Running stage', stage)
	F = eval('stage%02i' % stage)

	R = F(**P)

	print('Saving pickle', pfn)
	pickle_to_file(R, pfn)
	print('Saved', pfn)
	return R

def main():
	import optparse
	parser = optparse.OptionParser()
	#parser.add_option('--threads', dest='threads', default=16, type=int, help='Use this many concurrent processors')
	parser.add_option('-v', '--verbose', dest='verbose', action='count', default=0,
					  help='Make more verbose')
	parser.add_option('-f', '--force-stage', dest='force', action='append', default=[], type=int,
					  help="Force re-running the given stage(s) -- don't read from pickle.")
	parser.add_option('-s', '--stage', dest='stage', default=4, type=int,
					  help="Run up to the given stage")
	opt,args = parser.parse_args()

	if opt.verbose == 0:
		lvl = logging.INFO
	else:
		lvl = logging.DEBUG
	logging.basicConfig(level=lvl, format='%(message)s', stream=sys.stdout)

	runstage(opt.stage, opt.force)#, opt.threads)


def big():
	T = fits_table('exp1_dstn.fit')

	plt.clf()
	#plt.hist(np.log10(T.exprad_i), 100)
	plt.hist(T.exprad_i, 100, range=(1, 3))
	plt.savefig('erad1.png')

	plt.clf()
	plt.hist(T.exprad_i, 100, range=(1.7, 1.8))
	plt.savefig('erad2.png')

	Ti = T[((T.exprad_i > 1.7) * (T.exprad_i < 1.8))]
	print(len(Ti), 'in cut on exprad_i')
	print('Runs:', np.unique(Ti.run))
	for r,d in zip(Ti.ra, Ti.dec):
		print(r,d)

	plt.clf()
	plt.hist(T.exprad_i, 100, range=(2.1, 2.3))
	plt.savefig('erad3.png')

	Ti = T[((T.exprad_i > 2.1) * (T.exprad_i < 2.3))]
	print(len(Ti), 'in cut on exprad_i')
	print('Runs:', np.unique(Ti.run))
	for r,d in zip(Ti.ra, Ti.dec):
		print('http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra=%g&dec=%g&scale=0.1&width=512&height=512&opt=&query=' % (r,d))

	Ti = T[T.exprad_i > 3.]
	plt.clf()
	plt.hist(Ti.exprad_i, 100, range=(3., 5.))
	plt.savefig('erad4.png')

	T = fits_table('exp3_dstn.fit')

	plt.clf()
	plt.hist(T.exprad_i, 100, range=(3., 5.))
	plt.savefig('erad5.png')

	Ti = T[(T.exprad_i > 3.2) * (T.exprad_i < 3.5)]

	print(len(Ti), 'in cut on exprad_i')
	print('Runs:', np.unique(Ti.run))
	I = np.argsort(-Ti.expmag_i)
	Tj = Ti[I]
	for r,d,mag in zip(Tj.ra, Tj.dec, Tj.expmag_i):
		print('mag', mag)
		print('http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra=%g&dec=%g&scale=0.1&width=512&height=512&opt=&query=' % (r,d))


	Ti = T[(T.exprad_i > 4.1) * (T.exprad_i < 4.4)]

	print(len(Ti), 'in cut on exprad_i')
	print('Runs:', np.unique(Ti.run))
	I = np.argsort(-Ti.expmag_i)
	Tj = Ti[I]
	for r,d,mag in zip(Tj.ra, Tj.dec, Tj.expmag_i):
		print('mag', mag)
		print('http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra=%g&dec=%g&scale=0.1&width=512&height=512&opt=&query=' % (r,d))



	#T = fits_table('exp4_dstn.fit')
	T = fits_table('exp5b_dstn.fit')

	plt.clf()
	#plt.hist(T.exprad_i, 100, range=(3., 5.))
	plt.hist(T.exprad_i, 100, range=(3., 8.))
	plt.savefig('erad6.png')

	rlo,rhi = 4.1, 4.4
	Ti = T[(T.exprad_i > rlo) * (T.exprad_i < rhi)]

	plt.clf()
	plt.hist(T.exprad_i, 100, range=(rlo, rhi))
	plt.xlabel('exprad_i (arcsec)')
	plt.ylabel('Number of galaxies')
	plt.title('exp galaxies')
	plt.xlim(rlo, rhi)
	plt.savefig('erad7.png')

	Ti = Ti[Ti.expmag_i < 19]
	print('Runs:', np.unique(Ti.run))
	I = np.argsort(-Ti.expmag_i)
	Tj = Ti[I]
	urls = []
	for r,d,mag in zip(Tj.ra, Tj.dec, Tj.expmag_i):
		print('  mag', mag, end=' ')
		url = 'http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra=%g&dec=%g&scale=0.198&width=128&height=128&opt=&query=' % (r,d)
		print('  ', url)
		urls.append(url)

	html = '<html><body>' + '\n'.join(['<img src="%s" />' % url for url in urls]) + '</body></html>'
	write_file(html, '/home/dstn/public_html/temp/gals5b.html')
	
	plt.clf()
	plt.plot(Ti.expab_i, Ti.expphi_i, 'r.')
	plt.xlabel('ab')
	plt.ylabel('phi')
	plt.savefig('erad8.png')

	plt.clf()
	plt.hist(Ti.expab_i, 100)
	plt.xlabel('ab')
	plt.savefig('erad9.png')

	plt.clf()
	plt.plot(Ti.expmag_i, Ti.expab_i, 'r.')
	plt.xlabel('mag')
	plt.ylabel('ab')
	plt.savefig('erad10.png')
	

	T = fits_table('dev5b_dstn.fit')

	plt.clf()
	plt.hist(T.devrad_i, 100, range=(3., 8.))
	plt.savefig('drad6.png')

	rlo,rhi = 5., 5.2
	Ti = T[(T.devrad_i > rlo) * (T.devrad_i < rhi)]

	plt.clf()
	plt.hist(T.devrad_i, 100, range=(rlo, rhi))
	plt.xlabel('devrad_i (arcsec)')
	plt.ylabel('Number of galaxies')
	plt.title('dev galaxies')
	plt.xlim(rlo, rhi)
	plt.savefig('drad7.png')

	Ti = Ti[Ti.devmag_i < 18]
	print('Runs:', np.unique(Ti.run))
	I = np.argsort(-Ti.devmag_i)
	Tj = Ti[I]
	urls = []
	for r,d,mag in zip(Tj.ra, Tj.dec, Tj.devmag_i):
		print('  mag', mag, end=' ')
		url = 'http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra=%g&dec=%g&scale=0.198&width=128&height=128&opt=&query=' % (r,d)
		print('  ', url)
		urls.append(url)

	html = '<html><body>' + '\n'.join(['<img src="%s" />' % url for url in urls]) + '</body></html>'
	write_file(html, '/home/dstn/public_html/temp/dev5b.html')


	T = fits_table('mye4.fits')

	T2 = fits_table('exp5b_dstn.fit')
	T2.cut(T2.expmag_i < 19)

	plt.clf()
	rlo,rhi = 3.2, 6
	n,b,p = plt.hist(T2.exprad_i, 100, histtype='step', color='m', range=(rlo,rhi))
	n2,b2,p2 = plt.hist(T.exprad_i, bins=b, histtype='step', color='r')
	n3,b3,p3 = plt.hist(T.my_exprad_i, bins=b, histtype='step', color='b')
	plt.legend((p[0],p2[0],p3[0]), ('All Photo', 'Photo, exprad in [4.1, 4.4]', 'Tractor-refit [4.1, 4.4]'))
	plt.xlim(rlo, rhi)
	plt.xlabel('exprad_i (arcsec)')
	plt.ylabel('number of galaxies')
	plt.savefig('my1.png')

	plt.clf()
	rlo,rhi = 3.6, 6
	n,b,p = plt.hist(T2.exprad_i, 100, histtype='step', color='m', range=(rlo,rhi))
	n2,b2,p2 = plt.hist(T.exprad_i, bins=b, histtype='step', color='r')
	n3,b3,p3 = plt.hist(T.my_exprad_i, bins=b, histtype='step', color='b')
	plt.legend((p[0],p2[0],p3[0]), ('All Photo', 'Photo, exprad in [4.1, 4.4]', 'Tractor-refit [4.1, 4.4]'))
	plt.xlim(rlo, rhi)
	plt.xlabel('exprad_i (arcsec)')
	plt.ylabel('number of galaxies')
	plt.savefig('my2.png')



if __name__ == '__main__':
	#plots1()
	#plots2(0.4, 0.55, fn='exp3818i_dr7.fits', maxmag=20.5)
	#mrb_plots()
	#main()

	#big()

	T = fits_table('dev5b_dstn.fit')

	ps = PlotSequence('stats')

	loghist(np.log10(T.devrad_i), T.devmag_i, 100)
	plt.xlabel('deV radius (arcsec)')
	xt = [5, 10, 20, 30]
	plt.xticks([np.log10(t) for t in xt], ['%i' % t for t in xt])
	plt.ylabel('deV mag')
	plt.ylim(20, 15)
	ps.savefig()

	loghist(T.devab_i, T.devmag_i, 100)
	plt.xlabel('deV a/b ratio')
	plt.ylabel('deV mag')
	plt.ylim(20, 15)
	ps.savefig()

	loghist(T.devphi_i, T.devmag_i, 100)
	plt.xlabel('deV position angle (deg)')
	plt.ylabel('deV mag')
	plt.ylim(20, 15)
	ps.savefig()

	T = fits_table('cs82data/W4p1m1_i.V2.7A.swarp.cut.deVexp.fit', hdunum=2)

	maglim = 25
	I = np.flatnonzero(T.chi2_psf > T.chi2_model)
	print(len(I), 'galaxies')
	T.cut(I)
	faint = (T.mag_disk > maglim) * (T.mag_spheroid > maglim)
	T.cut(np.logical_not(faint))

	Texp = T[T.mag_disk <= maglim]
	Tdev = T[T.mag_spheroid <= maglim]

	plt.clf()
	ha=dict(histtype='step', range=(16,25), bins=100, log=True)
	nil,nil,p1 = plt.hist(Tdev.mag_spheroid, color='r', **ha)
	nil,nil,p2 = plt.hist(Texp.mag_disk, color='b', **ha)
	plt.xlabel('Mag')
	plt.legend((p1[0],p2[0]), ('spheroid', 'disk'), loc='upper left')
	plt.xlim(16,25)
	ps.savefig()

	plt.clf()
	ha=dict(histtype='step', range=(-7, -2), bins=100)
	nil,nil,p1 = plt.hist(np.log10(Tdev.spheroid_reff_world), color='r', **ha)
	nil,nil,p2 = plt.hist(np.log10(Texp.disk_scale_world), color='b', **ha)
	plt.xlabel('log_10 Scale')
	plt.legend((p1[0],p2[0]), ('spheroid', 'disk'))
	ps.savefig()

	plt.clf()
	ha=dict(histtype='step', range=(0, 1), bins=100)
	nil,nil,p1 = plt.hist(Tdev.spheroid_aspect_world, color='r', **ha)
	nil,nil,p2 = plt.hist(Texp.disk_aspect_world, color='b', **ha)
	plt.xlabel('Aspect ratio')
	plt.legend((p1[0],p2[0]), ('spheroid', 'disk'))
	ps.savefig()

	plt.clf()
	ha=dict(histtype='step', range=(-90, 90), bins=180)
	nil,nil,p1 = plt.hist(Tdev.spheroid_theta_world, color='r', **ha)
	nil,nil,p2 = plt.hist(Texp.disk_theta_world, color='b', **ha)
	plt.xlabel('Position angle (deg)')
	plt.legend((p1[0],p2[0]), ('spheroid', 'disk'))
	ps.savefig()

	loghist(np.append(Tdev.spheroid_theta_world,
					  Texp.disk_theta_world),
			np.append(Tdev.mag_spheroid,
					  Texp.mag_disk), 100, range=((-90,90),(16,25)))
	plt.xlabel('theta (deg)')
	plt.ylabel('mag')
	ps.savefig()

	loghist(Tdev.spheroid_theta_world,
			Tdev.spheroid_aspect_world,
			100, range=((-90,90),(0,1)))
	plt.xlabel('theta (deg)')
	plt.ylabel('aspect ratio')
	plt.title('spheroid')
	ps.savefig()

	loghist(Texp.disk_theta_world,
			Texp.disk_aspect_world,
			100, range=((-90,90),(0,1)))
	plt.xlabel('theta (deg)')
	plt.ylabel('aspect ratio')
	plt.title('disk')
	ps.savefig()



	sys.exit(0)


def mrb_plots():
	dn = 'paper0-data'
	if not os.path.exists(dn):
		os.mkdir(dn)
	sdss = DR7(basedir=dn)

	run,camcol,field = 3818,2,100
	band='r'
	B = 2
	rlo,rhi = (0.1, 1.5)
	sdss.retrieve('fpObjc', run, camcol, field, band)
	fn = sdss.getPath('fpObjc', run, camcol, field, band)
	fp = fits_table(fn)
	plt.clf()
	plt.hist(fp.r_exp.ravel(), 200, range=(rlo, rhi))
	plt.xlim(rlo,rhi)
	plt.ylim(0, 50)
	plt.xlabel('r_exp (pixels)')
	plt.title('DR7 fpObjc')
	plt.savefig('re20.png')

	sdss.retrieve('tsObj', run, camcol, field, band)
	fn = sdss.getPath('tsObj', run, camcol, field, band)
	fp = fits_table(fn)
	alo,ahi = (rlo*0.396, rhi*0.396)
	plt.clf()
	plt.hist(fp.r_exp.ravel(), 200, range=(alo,ahi))
	plt.xlabel('r_exp (arcsec)')
	plt.xlim(alo,ahi)
	plt.ylim(0, 50)
	plt.title('DR7 tsObj')
	plt.savefig('re21.png')

	T = fits_table('MyTable_10_dstn.fit')
	rad = np.hstack([T.get('exprad_%s'%b) for b in 'ugriz'])
	plt.clf()
	plt.hist(rad, 200, range=(alo,ahi))
	plt.xlabel('exprad (arcsec)')
	plt.xlim(alo,ahi)
	plt.ylim(0, 50)
	plt.title('DR7 CAS')
	plt.savefig('re22.png')
	

