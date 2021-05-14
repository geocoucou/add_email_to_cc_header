#!/usr/local/bin/python3
import sys, getopt
import re
from chardet.universaldetector import UniversalDetector
import codecs

# find . -not -path '*/\.*' -type f -exec ./add_email_to_cc_header.py -i {} -e laurent@vincelette.net -v \;

def getHeaders(lines):
    for i, line in enumerate(lines):
        #print (line)
        if line == '':
            return lines[:i]
    return False

def getCCStartAtLine(lines):
    for i, line in enumerate(lines):
        match = re.match("^[Cc]{2}:.*", line)
        if match:
            return i
    return -1

def getCCEndAtLine(lines, ccStartAtLine):
    for i, line in enumerate(lines):
        if i > ccStartAtLine:
            match = re.match("^[\w-]+:.*", line)
            if match:
                return i - 1
    return ccStartAtLine

def getInsertCCAt(lines):
    for i, line in enumerate(lines):
        match = re.match("^[TtOo]{2}:.*", line)
        if match:
            return getCCEndAtLine(lines, i) + 1
    return -1

def isEmailInCC(lines, email):
    for i, line in enumerate(lines):
        match = re.match(email, line)
        if (line.find(email)!= -1):
            return True
    return False

def getEncodingFromFile(inputfile):
    detector = UniversalDetector()
    for line in open(inputfile, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result['encoding']

def vPrint(line, verbose):
    if verbose:
        print (line)

def main():
    inputfile = ''
    email = ''
    verbose = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:e:v",["help", "ifile=", "email="])
    except getopt.GetoptError:
        print ('add_email_to_cc_header.py -i <inputfile> -e <email>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ('extract_ad_from_detection.py -i <inputfile> -e <email>')
            sys.exit()
        elif opt == "-v":
            verbose = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-e", "--email"):
            email = arg
            
      
    vPrint ('Looking for CC: in file "' + inputfile + '"', verbose)


    encoding = getEncodingFromFile(inputfile)
    vPrint ("find encoding: " + encoding, verbose)

    with codecs.open(inputfile, encoding=encoding) as f:
        lines = f.read().splitlines()
    
    headers = getHeaders(lines)
    if not headers :
        vPrint ("headers not found.", verbose)
        sys.exit()

    ccStartAtLine = getCCStartAtLine(headers)
    if (ccStartAtLine >= 0):
        ccEndAtLine = getCCEndAtLine(headers, ccStartAtLine)
        vPrint ("find Cc: at line " + str(ccStartAtLine+1) + ' up to line '+ str(ccEndAtLine+1), verbose)
        if (not isEmailInCC(headers[ccStartAtLine:ccEndAtLine+1], email)):
            vPrint ("email "+ email +" not found in Cc:, proceed to insertion at line "+ str(ccEndAtLine+2), verbose)
            with codecs.open(inputfile, "w", encoding=encoding) as f:
                for i, line in enumerate(lines):
                    if (i < ccEndAtLine):
                        f.write(line + '\n')
                    if (i == ccEndAtLine):
                        f.write(line + ',\n')
                        f.write(' '+ email+ '\n')
                    if (i > ccEndAtLine):
                        f.write(line+ '\n')
            vPrint ("file updated", verbose)
        else:
            vPrint ("email already in Cc: skipping", verbose)
    else:
        insertCCAt = getInsertCCAt(headers)
        vPrint("Cc: not found proceed to new Cc: insertion at line "+ str(insertCCAt+1), verbose)
        with codecs.open(inputfile, "w", encoding=encoding) as f:
            for i, line in enumerate(lines):
                    if (i < insertCCAt):
                        f.write(line + '\n')
                    if (i == insertCCAt):
                        f.write('Cc: '+ email+ '\n')
                        f.write(line + ',\n')
                    if (i > insertCCAt):
                        f.write(line+ '\n')
            
        # codecs.close(inputfile)
                



  

if __name__ == "__main__":
    main()




