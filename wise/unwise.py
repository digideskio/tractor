from __future__ import print_function
import os
import numpy as np
import fitsio

from astrometry.util.util import Tan
from astrometry.util.starutil_numpy import degrees_between
from astrometry.util.miscutils import polygons_intersect
from astrometry.util.fits import fits_table
from tractor import *

def unwise_tile_wcs(ra, dec, W=2048, H=2048, pixscale=2.75):
    '''
    Returns a Tan WCS object at the given RA,Dec center, axis aligned, with the
    given pixel W,H and pixel scale in arcsec/pixel.
    '''
    cowcs = Tan(ra, dec, (W+1)/2., (H+1)/2.,
                -pixscale/3600., 0., 0., pixscale/3600., W, H)
    return cowcs

def unwise_tiles_touching_wcs(wcs, polygons=True):
    '''
    Returns a FITS table (with RA,Dec,coadd_id) of unWISE tiles
    '''
    atlasfn = os.path.join(os.path.dirname(__file__), 'allsky-atlas.fits')
    T = fits_table(atlasfn)
    trad = wcs.radius()
    wrad = np.sqrt(2.)/2. * 2048 * 2.75/3600.
    rad = trad + wrad
    r,d = wcs.radec_center()
    I, = np.nonzero(np.abs(T.dec - d) < rad)
    I = I[degrees_between(T.ra[I], T.dec[I], r, d) < rad]

    if not polygons:
        return T[I]
    # now check actual polygon intersection
    tw,th = wcs.imagew, wcs.imageh
    targetpoly = [(0.5,0.5),(tw+0.5,0.5),(tw+0.5,th+0.5),(0.5,th+0.5)]
    cd = wcs.get_cd()
    tdet = cd[0]*cd[3] - cd[1]*cd[2]
    if tdet > 0:
        targetpoly = list(reversed(targetpoly))
    targetpoly = np.array(targetpoly)
    keep = []
    for i in I:
        wwcs = unwise_tile_wcs(T.ra[i], T.dec[i])
        cd = wwcs.get_cd()
        wdet = cd[0]*cd[3] - cd[1]*cd[2]
        H,W = wwcs.shape
        poly = []
        for x,y in [(0.5,0.5),(W+0.5,0.5),(W+0.5,H+0.5),(0.5,H+0.5)]:
            rr,dd = wwcs.pixelxy2radec(x,y)
            ok,xx,yy = wcs.radec2pixelxy(rr,dd)
            poly.append((xx,yy))
        if wdet > 0:
            poly = list(reversed(poly))
        poly = np.array(poly)
        if polygons_intersect(targetpoly, poly):
            keep.append(i)
    I = np.array(keep)
    return T[I]
    

def get_unwise_tile_dir(basedir, coadd_id):
    return os.path.join(basedir, coadd_id[:3], coadd_id)

def get_unwise_tractor_image(basedir, tile, band, bandname=None, masked=True,
                             **kwargs):
    '''
    masked: read "-m" images, or "-u"?

    bandname: PhotoCal band name to use: default: "w%i" % band
    '''

    if bandname is None:
        bandname = 'w%i' % band

    mu = 'm' if masked else 'u'

    # Allow multiple colon-separated unwise-coadd directories.
    basedirs = basedir.split(':')
    foundFiles = False
    for basedir in basedirs:
        thisdir = get_unwise_tile_dir(basedir, tile)
        base = os.path.join(thisdir, 'unwise-%s-w%i-' % (tile, band))

        imfn = base + 'img-%s.fits'       % mu
        ivfn = base + 'invvar-%s.fits.gz' % mu
        # ppfn = base + 'std-%s.fits.gz'    % mu
        nifn = base + 'n-%s.fits.gz'      % mu
        nufn = base + 'n-u.fits.gz'

        if not os.path.exists(imfn):
            print('Does not exist:', imfn)
            continue
        print('Reading', imfn)
        wcs = Tan(imfn)
        twcs = ConstantFitsWcs(wcs)

        F = fitsio.FITS(imfn)
        img = F[0]
        hdr = img.read_header()
        H,W = img.get_info()['dims']
        H,W = int(H), int(W)

        roi = interpret_roi(twcs, (H,W), **kwargs)
        if roi is None:
            # No overlap with ROI
            return None
        # interpret_roi returns None or a tuple; drop the second element in the tuple.
        roi,nil = roi
        (x0,x1,y0,y1) = roi

        wcs = wcs.get_subimage(x0, y0, x1-x0, y1-y0)
        twcs = ConstantFitsWcs(wcs)
        roislice = (slice(y0,y1), slice(x0,x1))
        img = img[roislice]

        if not os.path.exists(ivfn) and os.path.exists(ivfn.replace('.fits.gz', '.fits')):
            ivfn = ivfn.replace('.fits.gz','.fits')
        if not os.path.exists(nifn) and os.path.exists(nifn.replace('.fits.gz', '.fits')):
            nifn = nifn.replace('.fits.gz','.fits')
        if not os.path.exists(nufn) and os.path.exists(nufn.replace('.fits.gz', '.fits')):
            nufn = nufn.replace('.fits.gz','.fits')

        if not (os.path.exists(ivfn) and os.path.exists(nifn) and os.path.exists(nufn)):
            print('Files do not exist:', ivfn, nifn, nufn)
            continue

        foundFiles = True
        break

    if not foundFiles:
        raise IOError('unWISE files not found in ' + str(basedirs) + ' for tile ' + tile)

    print('Reading', ivfn)
    invvar = fitsio.FITS(ivfn)[0][roislice]

    if band == 4:
        # due to upsampling, effective invvar is smaller (the pixels
        # are correlated)
        invvar *= 0.25
    
    #print 'Reading', ppfn
    #pp = fitsio.FITS(ppfn)[0][roislice]
    print('Reading', nifn)
    nims = fitsio.FITS(nifn)[0][roislice]

    if nufn == nifn:
        nuims = nims
    else:
        print('Reading', nufn)
        nuims = fitsio.FITS(nufn)[0][roislice]

    #print 'Median # ims:', np.median(nims)
    good = (nims > 0)
    invvar[np.logical_not(good)] = 0.
    sig1 = 1./np.sqrt(np.median(invvar[good]))

    # Load the average PSF model (generated by wise_psf.py)
    psffn = os.path.join(os.path.dirname(__file__), 'wise-psf-avg.fits')
    print('Reading', psffn)
    P = fits_table(psffn, hdu=band)
    psf = GaussianMixturePSF(P.amp, P.mean, P.var)

    sky = 0.
    tsky = ConstantSky(sky)

    # if opt.errfrac > 0:
    #     nz = (iv > 0)
    #     iv2 = np.zeros_like(invvar)
    #     iv2[nz] = 1./(1./invvar[nz] + (img[nz] * opt.errfrac)**2)
    #     print 'Increasing error estimate by', opt.errfrac, 'of image flux'
    #     invvar = iv2

    tim = Image(data=img, invvar=invvar, psf=psf, wcs=twcs,
                sky=tsky, photocal=LinearPhotoCal(1., band=bandname),
                name='unWISE %s W%i' % (tile, band))
    tim.sig1 = sig1
    tim.roi = roi
    tim.nims = nims
    tim.nuims = nuims
    tim.hdr = hdr

    if 'MJDMIN' in hdr and 'MJDMAX' in hdr:
        from tractor.tractortime import TAITime
        tim.mjdmin = hdr['MJDMIN']
        tim.mjdmax = hdr['MJDMAX']
        tim.time = TAITime(None, mjd=(tim.mjdmin + tim.mjdmax)/2.)

    return tim

