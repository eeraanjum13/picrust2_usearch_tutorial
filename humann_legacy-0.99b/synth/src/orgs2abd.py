#!/usr/bin/env python

import re
import sys

c_strKO	= "ko"

if len( sys.argv ) < 4:
	raise Exception( "Usage: orgs2abd.py <stagger> <pathwayc> <pathways.list>+ < <organisms.txt>" )
strStagger, strOrg, strPathways, astrPathways = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
fOrgResult = int(strOrg) != 0
fStagger = int(strStagger) != 0

hashOrgs = {}
hashHits = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	strOrg, strAbd = strLine.split( "\t" )
	hashOrgs[strOrg] = float(strAbd)
	hashHits[strOrg] = False

setstrPathways = set()
for strLine in open( strPathways ):
	astrLine = strLine.strip( ).split( "\t" )
	setstrPathways.add( astrLine[0] )

hashPathways = {}
for strPathways in astrPathways:
	pMatch = re.search( '^(?:.*\/)?([a-z]{3}?)_\S+\.list$', strPathways )
	if not pMatch:
		sys.stderr.write( "Illegal genome: %s\n" % strPathways )
		continue
	strOrg = pMatch.group( 1 )
	if strOrg not in hashOrgs:
		sys.stderr.write( "Extra genome: %s\n" % strPathways )
		continue
	hashHits[strOrg] = True
	setPathways = hashPathways.setdefault( strOrg, set() )
	for strLine in open( strPathways ):
		strGene, strToken = strLine.strip( ).split( "\t" )
		strToken, strID = strToken.split( ":" )
		mtch = re.search( '^[a-z]{3}(\d+)$', strID )
		if mtch:
			strID = c_strKO + mtch.group( 1 )
		if strID in setstrPathways:
			setPathways.add( strID )

for strOrg, fOrg in hashHits.items( ):
	if not fOrg:
		sys.stderr.write( "Missing genome: %s\n" % strOrg )

hashhashAbds = {}
for strOrg, setPathways in hashPathways.items( ):
	dAbd = hashOrgs[strOrg] if fStagger else 1
	for strPathway in setPathways:
		dCur = hashhashAbds.setdefault( strOrg if fOrgResult else None, {} ).get( strPathway, 0 )
		hashhashAbds[strOrg if fOrgResult else None][strPathway] = dCur + dAbd

sys.stdout.write( "PID	" )
if fOrgResult:
	sys.stdout.write( "Organism	" )
print( "Abundance" )
for strOrg, hashAbds in hashhashAbds.items( ):
	for strPathway, dAbd in hashAbds.items( ):
		sys.stdout.write( "%s	" % strPathway )
		if fOrgResult:
			sys.stdout.write( "%s	" % strOrg )
		print( "%g" % dAbd )
	