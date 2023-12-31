#!/usr/bin/env python

import pathway
import sys

c_fCoverage	= True
c_fMedup	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathab.py <keggc> [modulep] [medup=" + str(c_fMedup) + "] [coverage=" + str(c_fCoverage) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
strModuleP = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
fMedup = c_fMedup if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )
fCoverage = c_fCoverage if ( len( sys.argv ) <= 4 ) else ( int(sys.argv[4]) != 0 )

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashModules = {}
if strModuleP:
	for pPathway in pathway.open( open( strModuleP ) ):
		hashModules[pPathway.id( )] = pPathway

hashKOs = {}
hashhashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		fOrg = len( astrLine ) > 3
		continue
	if fOrg:
		dScore = float( astrLine[3] )
		strKOOrg = "".join( ( astrLine[0],astrLine[1] ) )
		hashKOs[strKOOrg] = max( dScore, hashKOs.get( strKOOrg, 0 ) )
		strOrg = astrLine[1]
	else:
		dScore = float( astrLine[2] )
		hashKOs[astrLine[0]] = max( dScore, hashKOs.get( astrLine[0], 0 ) )
	hashhashScores.setdefault( astrLine[1] if fOrg else None, {} ).setdefault( 
		astrLine[2] if fOrg else astrLine[1], {} )[astrLine[0]] = dScore
adScores = sorted( hashKOs.values( ) )
if len( adScores ) > 2:
	d25, d50, d75 = (adScores[int(round( 0.25 * ( i + 1 ) * len( adScores ) ))] for i in range( 3 ))
else:
	d25, d50, d75 = [adScores[0] if adScores else 0] * 3
sys.stdout.write( "PID	" )
if fOrg:
	sys.stdout.write( "Organism	" )
print( "Abundance" )
for strOrg, hashScores in hashhashScores.items( ):
	for strKEGG, hashKOs in hashScores.items( ):
		if len( strKEGG ) == 0:
			continue
		for strKO in hashKEGGs.get( strKEGG, [] ):
			hashKOs.setdefault( strKO, 0 )
		adAbs = sorted( hashKOs.values( ) )
		pPathway = hashModules.get( strKEGG )
		if pPathway:
			dAb = pPathway.abundance( hashKOs, d50 if fCoverage else None )
		else:
			if fMedup:
				adAbs = adAbs[( len( adAbs ) / 2 ):]
			dAb = sum( adAbs ) / len( adAbs )
		if fOrg:
			print( "\t".join( (strKEGG, strOrg, str(dAb)) ) )
		else:
			print( "\t".join( (strKEGG, str(dAb)) ) )