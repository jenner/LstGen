# coding: utf-8
import sys
import os
import argparse

from lxml import etree
from io import StringIO

from . import PapParser

def main():
    parser = argparse.ArgumentParser(description='Erzeugt validen Code für die Lohnsteuerberechung aus PAP XML')
    parser.add_argument('pap_path', metavar='PAP-PATH', help='Pfad zur PAP XML')
    parser.add_argument('lang', metavar='LANG', help='Programmiersprache (PHP, Python oder Java)')
    parser.add_argument('--outfile',
        dest='outfile',
        metavar='OUTFILE',
        help='Ausgabedatei, default: STDOUT'
    )
    parser.add_argument('--class-name',
        dest='class_name',
        metavar='CLASS_NAME',
        help="Name der generierten Klasse, standardmässig wird der Name der PAP Elements verwendet",
    )
    parser.add_argument('--indent',
        dest='indent',
        default='    ',
        help='Zeichenkette mit der eingerückt wird, default: 4 Leerzeichen'
    )
    parser.add_argument('--java-package-name',
        dest='java_package',
        metavar='JAVA_PACKAGE',
        help="Package-Name (falls LANG=java), standardmässig wird 'default' verwendet",
    )
    parser.add_argument('--php-ns',
        dest='php_ns',
        metavar='PHP_NAMESPACE',
        help="Namespace-Name (falls LANG=php)",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.pap_path):
        sys.stderr.write("Kann Datei nicht öffnen: '{}'\n".format(args.pap_path))
        sys.exit(1)

    if args.lang.lower() not in ('php', 'python', 'java'):
        sys.stderr.write("Unbekannte Sprache: {}".format(lang))
        sys.exit(1)

    lang = args.lang.lower()
    with open(args.pap_path) as fp:
        parser = PapParser(etree.parse(fp))
        parser.parse()
        is_stdout = False
        if not args.outfile:
            is_stdout = True
            outfp = StringIO()
        else:
            outfp = open(args.outfile, 'w+')
        with outfp:
            if lang == 'php':
                from . writers.php import PhpWriter
                writer = PhpWriter(parser,
                    outfp,
                    class_name=args.class_name,
                    ns_name=args.php_ns,
                    indent=args.indent,
                )
            elif lang == 'python':
                from . writers.python import PythonWriter
                writer = PythonWriter(parser,
                    outfp,
                    class_name=args.class_name,
                    indent=args.indent
                )
            elif lang == 'java':
                from . writers.java import JavaWriter
                writer = JavaWriter(parser,
                    outfp,
                    class_name=args.class_name,
                    package_name=args.java_package,
                    indent=args.indent
                )
            writer.generate()
            if is_stdout:
                print(outfp.getvalue())
