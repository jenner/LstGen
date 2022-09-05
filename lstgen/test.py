import math
from taxfiles import Lohnsteuer2022Big
import sys, getopt

def main(argv):
    brutto = 0
    try:
        opts, args = getopt.getopt(argv,"hb",["brutto="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-b", "--brutto"):
            brutto = int(arg)

    print('test')
    lst2014 = Lohnsteuer2022Big(
        RE4=brutto,
        KVZ=1.3,
        LZZ=2,
        PVZ=1,
        STKL=3,
    )

    lst2014.MAIN()
    print_lst(lst2014)

def print_lst(lst):
    steuer = math.floor(float(lst.getLstlzz()) + float(lst.getStv()) + float(lst.getSts())) / 100.0
    soli = math.floor(float(lst.getSolzlzz()) + float(lst.getSolzs()) + float(lst.getSolzv())) / 100
    stges = steuer + soli
    print("steuer: {steuer}\nsoli: {soli}\nstges: {stges}".format(
        steuer=steuer,
        soli=soli,
        stges=stges
    ))

if __name__ == "__main__":
    main(sys.argv[1:])