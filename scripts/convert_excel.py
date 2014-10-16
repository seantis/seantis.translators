# -*- coding: utf-8 -*-
from __future__ import print_function

import click
import sys
import tablib
import textwrap


@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path(exists=False))
def convert(input, output):
    """ Converts the existing translators excel to be compatible with the
    seantis.people excel import.

    """
    print_error = lambda msg: click.secho(textwrap.dedent(msg), fg='red')

    with open(input, 'rb') as excel:
        ds = tablib.import_set(excel)

    if not all(ds.headers):
        print_error(u"""
            The headers could not be detected. This means that you are trying
            to convert the original xls(x) by the client, which doesn't work
            with this script because it never meant to leave the Windows world.

            To fix, open the excel file in Excel, select all, copy all, create
            a new excel file and paste it all there.

            Store the new excel file as xlsx and call the script with the
            path to that file again.
        """)
        sys.exit(1)

    if not output.endswith('.csv'):
        print_error(u"The export file is required to end with .csv")
        sys.exit(1)

    # we don't need those columns anymore
    for header in (u"AVANTI", u"Verzeichnis Übersetzende", u"Mutation"):
        del ds[header]

    # split zipcode and town
    zipcodes = [s.split(' ')[0].strip() for s in ds[u"Plz Ort"]]
    towns = [s.split(' ')[1].strip() for s in ds[u"Plz Ort"]]

    del ds["Plz Ort"]
    ds.append_col(zipcodes, u"PLZ")
    ds.append_col(towns, u"Ort")

    # rename certain headers
    header_map = {
        u"Bank Kto ltd auf": u"Bank Konto lautet auf",
        u"eMail": u"E-Mail",
        u"Telefon P": u"Telefon Privat",
        u"Telefon G": u"Telefon Geschäft",
        u"Andere": u"Andere Zertifikate",
        u"Geb Datum": u"Geburtsdatum"
    }

    for old_name, new_name in header_map.items():
        ds.append_col(ds[old_name], new_name)
        del ds[old_name]

    # certificates are done differently
    certificates = []
    for zhaw, ogzh in zip(ds[u"ZHAW Zertifikat"], ds[u"OGZH Zertifikat"]):
        if zhaw == 1 and ogzh == 1:
            certificates.append(u"ZHAW, OGZH")
        if zhaw == 1 and ogzh == 0:
            certificates.append(u"ZHAW")
        if zhaw == 0 and ogzh == 1:
            certificates.append(u"OGZH")
        if zhaw == 0 and ogzh == 0:
            certificates.append(u"")

    del ds[u"ZHAW Zertifikat"]
    del ds[u"OGZH Zertifikat"]

    ds.append_col(certificates, u"Zertifikate")

    # cleanup a few things
    new_ds = tablib.Dataset()
    new_ds.headers = ds.headers

    for r, row in enumerate(ds):
        new_row = [c for c in row]

        for c, col in enumerate(row):

            if col is None:
                new_row[c] = ''

            if isinstance(col, basestring):
                if col == '-':
                    new_row[c] = ''

                if '@' in col and '#mailto:' in col:
                    new_row[c] = col[:col.find('#mailto')]

            if isinstance(col, int):
                if col <= 1:
                    new_row[c] = int == 1 and True or False
                else:
                    new_row[c] = str(col)

        new_ds.append(new_row)

    ds = new_ds

    # write the result
    with open(output, 'w') as csv:
        csv.write(ds.csv)


if __name__ == '__main__':
    convert()
