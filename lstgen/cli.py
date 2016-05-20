# coding: utf-8
import sys
import os
import argparse

from lxml import etree
from io import StringIO

from . import PapParser
from . import pap

LANGUAGES = ('php', 'python', 'java')

def main():
    parser = argparse.ArgumentParser(description='Erzeugt validen Code für die Lohnsteuerberechung aus PAP XML')
    parser.add_argument('-l', '--lang',
        dest='lang',
        choices=LANGUAGES,
        metavar='LANG',
        help='Programmiersprache (PHP, Python oder Java)')
    parser.add_argument('-p', '--pap-version',
        dest='pap_version',
        choices=pap.PAP_RESOURCES.keys(),
        metavar='PAP',
        help='PAP Version (z.B. "2016"), falls kein PAP XML Pfad angegeben wurde, siehe auch Option --pap-versions'
    )
    parser.add_argument('-x', '--pap-xml',
        dest='pap_xml_path',
        metavar='XML_PATH',
        help='Pfad zur PAP XML, falls keine PAP Version ausgewählt wurde.'
    )
    parser.add_argument('--pap-versions',
        dest='show_pap_versions',
        action='store_true',
        default=False,
        help='Gibt die Liste der verfügbaren PAP Version aus.'
    )
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

    if args.show_pap_versions:
        print("Verfügbare PAP Versionen:")
        for version in pap.PAP_RESOURCES.keys():
            print(version)
        sys.exit(0)

    if (not args.pap_version and not args.pap_xml_path) or (args.pap_version and args.pap_xml_path):
        sys.stderr.write("Bitte entweder eine PAP Version (-p) oder Pfad zu einer PAP XML Datei angeben (-x)\n")
        sys.exit(1)

    xml_content = None
    if args.pap_xml_path:
        if not os.path.isfile(args.pap_xml_path):
            sys.stderr.write("Kann Datei nicht öffnen: '{}'\n".format(args.pap_xml_path))
            sys.exit(1)
        else:
            xml_content = open(args.pap_xml_path, 'r').read()

    if args.pap_version:
        try:
            xml_content = pap.get_pap_xml(args.pap_version)
        except ValueError as err:
            sys.stderr.write(err)
            sys.stderr.write("\n")
            sys.exit(1)

    lang = args.lang.lower()
    parser = PapParser(etree.fromstring(xml_content))
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
