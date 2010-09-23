#
#	generates pngs related to the deconvolution
#

execfile("../config.py")
import shutil
import f2n
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
from star import *

pngkey = deckey + "_png"
pngdir = os.path.join(workdir, pngkey)

if os.path.isdir(pngdir):
	print "Deleting existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
	
	reflinkdestpath = os.path.join(workdir, deckey + "_ref.png")
	if os.path.exists(reflinkdestpath):
		os.remove(reflinkdestpath)
	
os.mkdir(pngdir)

# Read input positions of point sources, to draw a legend.
ptsrcs = readmancatasstars(ptsrccat)
print "Number of point sources :", len(ptsrcs)



db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])

for i, image in enumerate(images):
	
	print "- " * 40
	code = image[deckeyfilenum]
	print i+1, "/", len(images), ":", image['imgname'], code
	
	# We want to look for cosmics. Not that obvious, as we have left all the cosmic detections into the objdirs...
	# We do this in a robust way, i.e. only if we find the required files...
	objkey = "obj_" + decobjname
	cosmicslistpath = os.path.join(workdir, objkey, image['imgname'], "cosmicslist.pkl")
	if os.path.exists(cosmicslistpath):
		cosmicslist = readpickle(cosmicslistpath, verbose=False)
	else:
		cosmicslist = []
		
	# To get the number of cosmics is easier ...
	objcosmicskey = objkey + "_cosmics" # objkey is redefined up there...
	ncosmics = image[objcosmicskey]
	
	pngpath = os.path.join(pngdir, image['imgname'] + ".png")
	
	
	f2ng = f2n.fromfits(os.path.join(decdir, "g" +code+".fits"), verbose=False)
	f2ng.setzscale(-20, "auto")
	f2ng.makepilimage(scale = "log", negative = False)
	f2ng.upsample(4)
	f2ng.drawstarslist(cosmicslist)
	f2ng.writeinfo(["Input"])
	
	#f2ng.writeinfo(["","g001.fits"])
	
	f2ndec = f2n.fromfits(os.path.join(decdir, "dec" +code+".fits"), verbose=False)
	f2ndec.setzscale(-20, "auto")
	f2ndec.makepilimage(scale = "log", negative = False)
	f2ndec.upsample(2)
	f2ndec.writeinfo(["Deconvolution"])
	
	f2nresi = f2n.fromfits(os.path.join(decdir, "resi" +code+".fits"), verbose=False)
	f2nresi.setzscale(-10, 10)
	f2nresi.makepilimage(scale = "lin", negative = False)
	f2nresi.upsample(2)
	f2nresi.writeinfo(["Residual"])
	
	f2nresi_sm = f2n.fromfits(os.path.join(decdir, "resi_sm" +code+".fits"), verbose=False)
	f2nresi_sm.setzscale(-10, 10)
	f2nresi_sm.makepilimage(scale = "lin", negative = False)
	f2nresi_sm.upsample(2)
	f2nresi_sm.writeinfo(["SM Residual"])
	
	f2nback = f2n.fromfits(os.path.join(decdir, "back" +code+".fits"), verbose=False)
	f2nback.setzscale(-20, "ex")
	f2nback.makepilimage(scale = "lin", negative = False)
	f2nback.upsample(2)
	f2nback.writeinfo(["Background"])
	
	
	f2ns = f2n.fromfits(os.path.join(decdir, "s" +code+".fits"), verbose=False)
	f2ns.setzscale(1e-8, "ex")
	f2ns.makepilimage(scale = "log", negative = False)
	f2ns.upsample(2)
	f2ns.writeinfo(["PSF"])
	
	
	#legend = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	#legend.setzscale(0.0, 1.0)
	#legend.makepilimage(scale = "lin", negative = False)
	
	legend = f2n.f2nimage(shape = (64,64), fill = 0.0, verbose=False)
	legend.setzscale(0.0, 1.0)
	legend.makepilimage(scale = "lin", negative = False)
	legend.upsample(4)
	for ptsrc in ptsrcs:
		legend.drawcircle(ptsrc.x, ptsrc.y, r=0.5, colour=(255), label = ptsrc.name)
	legend.writeinfo(["Legend"])
	
	
	
	txtendpiece = f2n.f2nimage(shape = (256,256), fill = 0.0, verbose=False)
	txtendpiece.setzscale(0.0, 1.0)
	txtendpiece.makepilimage(scale = "lin", negative = False)
	
	
	date = image['datet']
	seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	nbralistars = "Nb alistars : %i" % image['nbralistars']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f [deg]" % image['az']
	stddev = "Sky stddev : %4.2f [ADU]" % image['stddev']
	dkfn = "Deconv file : %s" % code
	ncosmics = "Cosmics : %i" % ncosmics
	selectedpsf = "Selected PSF : %s" % image[deckeypsfused]
	normcoeff = "Norm. coeff : %.3f" % image[deckeynormused]
	
	# we write long image names on two lines ...
	if len(image['imgname']) > 25:
		infolist = [image['imgname'][0:25], image['imgname'][25:]]
	else:
		infolist = [image['imgname']]
	infolist.extend([date, seeing, ell, nbralistars, stddev, airmass, az, dkfn, ncosmics, selectedpsf, normcoeff])
	
	txtendpiece.writeinfo(infolist)
	

	f2n.compose([[f2ng, f2ndec, f2nback, txtendpiece], [f2ns, f2nresi, f2nresi_sm, legend]], pngpath)	
	
	orderlink = os.path.join(pngdir, "%s.png" % code)
	os.symlink(pngpath, orderlink)
	
	
	# Before going on with the next image, we build a special link for the ref image (i.e. the first one, in this case) :
	
	if image["imgname"] == refimgname:
		print "This was the reference image."
		sourcepath = pngpath
		destpath = os.path.join(workdir, deckey + "_ref.png")
		copyorlink(sourcepath, destpath, uselinks)
		print "For this special image I made a link into the workdir :"
		print destpath
		print "I would now continue for all the other images."
		
		# We do something similar with the background image as fits :
		copyorlink(os.path.join(decdir, "back0001.fits"), os.path.join(workdir, deckey + "_back.fits"), uselinks)
		
		proquest(askquestions)
	
	
print "- " * 40


notify(computer, withsound, "Done.")

print "I've made deconvolution pngs for", deckey
print "Note : for these pngs, the filenames of the links"
print "refer to decfilenums, not to a chronological order ! "

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)


