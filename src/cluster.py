#!/usr/bin/env python

''' 
 * All rights Reserved, Designed By HIT-Bioinformatics   
 * @Title:  process.py
 * @Package: 
 * @Description: Control rCANID pipeline
 * @author: tjiang
 * @date: June 11 2018
 * @version V1.0.1     
'''

import argparse
import sys
import pysam
from parsing_ins_signal import *
import logging
from CommandRunner import *
from extract_reads import *

USAGE="""\
	Cluster breakpoints and extract signal & unmapped reads.
"""

def parseArgs(argv):
	parser = argparse.ArgumentParser(prog="process.py detection", description=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
	# parser.add_argument("AlignmentFile", type=str, help="the bam format file generated by ngmlr, within a '.bai' index file")
	parser.add_argument("input", metavar="[BAM]", type=str, help="Input sorted BAM.")
	# parser.add_argument("Reference", metavar="REFERENCE", type=str, help="the reference genome(fasta format)")
	parser.add_argument('temp_dir', type=str, help = "temporary directory to use for distributed jobs")
	# parser.add_argument("--temp", type=str, default=tempfile.gettempdir(), help="Where to save temporary files")
	parser.add_argument('output', type=str, help = "the prefix of novel sequence insertion pridections")
	# parser.add_argument('signals', type=str, help = "storing cluster info file")

	# parser.add_argument('-s', '--min_support', help = "Mininum number of reads that support a ME.[%(default)s]", default = 5, type = int)
	# parser.add_argument('-l', '--min_length', help = "Mininum length of ME to be reported.[%(default)s]", default = 50, type = int)
	# parser.add_argument('-d', '--min_distance', help = "Mininum distance of two ME clusters.[%(default)s]", default = 20, type = int)
	# # parser.add_argument('-hom', '--homozygous', help = "The mininum score of a genotyping reported as a homozygous.[%(default)s]", default = 0.8, type = float)
	# # parser.add_argument('-het','--heterozygous', help = "The mininum score of a genotyping reported as a heterozygous.[%(default)s]", default = 0.3, type = float)
	# # parser.add_argument('-q', '--min_mapq', help = "Mininum mapping quality.[20]", default = 20, type = int)
	# parser.add_argument('-t', '--threads', help = "Number of threads to use.[%(default)s]", default = 1, type = int)
	# parser.add_argument('-x', '--presets', help = "The sequencing type <pacbio,ont> of the reads.[%(default)s]", default = "pacbio", type = str)
	# # parser.add_argument("--temp", type=str, default=tempfile.gettempdir(), help="Where to save temporary files")
	# # parser.add_argument("--chunks", type=int, default=0, help="Create N scripts containing commands to each input of the fofn (%(default)s)")
	# # parser.add_argument("--debug", action="store_true")
	args = parser.parse_args(argv)

	return args

def extract_mapped_reads(temp_dir, bam_path, out_path):
	logging.info("Merging cluster info...")
	cmd = ("cd %s && cat _*.txt > mapped_cluster_info.txt && cd $OLDPWD" % (temp_dir))
	# cmd = ("ngmlr -r %s -q %s -o %s -t %d -x %s" % (ref, inFile, outFile, nproc, presets))
	r, o, e = exe(cmd)
	logging.info("Finished cluster info merging.")

	logging.info("Extracting mapped signal reads...")
	if temp_dir[-1] != '/':
		temp_dir += '/'
	if out_path[-1] != '/':
		out_path += "/"
	parse_cluster(temp_dir+"mapped_cluster_info.txt", bam_path, out_path, 'fa')
	logging.info("Finished mapped signal reads extraction.")

def extract_unmapped_reads(BAM, out_path):
	from string import maketrans
	revComp = maketrans("ATCGNatcgn","TAGCNtagcn")
	s = pysam.Samfile(BAM)
	file = open(out_path+"unmaped.fa", 'w')
	get = s
	for read in get:
		if read.flag != 4:
			continue
		if read.is_reverse:
        		# sys.stdout.write("@{0}\n{1}\n+\n{2}\n".format(read.qname, read.seq.translate(revComp)[::-1], read.qual[::-1]))
			file.write(">{0}\n{1}\n".format(read,qname, read.seq.translate(revComp)[::-1]))
		else:
        		# sys.stdout.write("@{0}\n{1}\n+\n{2}\n".format(read.qname, read.seq, read.qual))
			file.write(">{0}\n{1}\n".format(read.qname, read.seq))
	file.close()

def run(argv):
	import time
	args = parseArgs(argv)
	setupLogging(False)
	# print args
	starttime = time.time()

	if args.temp_dir[-1] == '/':
		load_sam(args.input, args.temp_dir)
	else:
		load_sam(args.input, args.temp_dir+'/')

	extract_mapped_reads(args.temp_dir, args.input, args.output)
	extract_unmapped_reads(args.input, args.output)

	logging.info("Finished in %0.2f seconds."%(time.time() - starttime))

if __name__ == '__main__':
	run(sys.argv[1:])