#
#	report about normalisation
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

fields = ['imgname', 'seeing', 'nbralistars', 'geomaprms', 'medcoeff', 'nbrcoeffstars', 'maxcoeffstars', 'sigcoeff', 'spancoeff']



db = KirbyBase()
reporttxt = ""

usedsetnames = set(map(lambda x : x[0], db.select(imgdb, ['recno'], ['*'], ['setname'])))

for setname in usedsetnames:
	
	reporttxt += "\n\n      ########### %10s    ########\n\n"%setname
	setreport = db.select(imgdb, ['flagali','setname'], ['== 1', setname], fields, sortFields=['nbrcoeffstars', 'spancoeff'], returnType='report')
	reporttxt += setreport


reporttxtfile = open(os.path.join(workdir, "report_prenorm.txt"), "w")
reporttxtfile.write(reporttxt)
reporttxtfile.close()

