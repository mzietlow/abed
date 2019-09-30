import datetime
import os

from tabulate import tabulate

from .models import AbedTable
from ..conf import settings
from ..utils import info, mkdir, clean_str


def export_tables(tables):
    summary_tables = []
    for table in tables:
        summary_table = merge_description_table(table)
        write_table_txt(table, summary_table)
        write_table_ajax(table, is_summary=False)
        write_table_ajax(summary_table, is_summary=True)
        summary_tables.append(summary_table)
    return summary_tables


def merge_description_table(table):
    if (not settings.DATA_DESCRIPTION_CSV is None) and os.path.exists(
        settings.DATA_DESCRIPTION_CSV
    ):
        at = AbedTable()
        at.from_csv(settings.DATA_DESCRIPTION_CSV)
        summary_table = table.left_insert(at)
    else:
        summary_table = table.summary_table()
    return summary_table


def get_table_fname(table, ext, _type):
    if _type == "html":
        outdir = "%s%s%s" % (settings.OUTPUT_DIR, os.sep, "html")
    elif _type == "txt":
        outdir = "%s%s%s" % (settings.OUTPUT_DIR, os.sep, "txt")
    mkdir(outdir)
    if table.is_metric:
        fname = "%s%sABED_%s_%s_%s%s" % (
            outdir,
            os.sep,
            clean_str(table.target),
            clean_str(table.name),
            clean_str(table.type),
            ext,
        )
    else:
        fname = "%s%sABED_%s_%s%s" % (
            outdir,
            os.sep,
            clean_str(table.target),
            clean_str(table.type),
            ext,
        )
    return fname


def write_table_txt(table, summary_table):
    fname = get_table_fname(table, ".txt", "txt")
    now = datetime.datetime.now()
    with open(fname, "w") as fid:
        fid.write(
            "%% Result file generated by ABED at %s\n" % now.strftime("%c")
        )
        fid.write("%% Table for label: %s\n" % table.target)
        fid.write("%% Showing: %s\n" % table.type)
        if table.is_metric:
            fid.write("%% Metric: %s\n\n" % table.name)
        txttable = [[i] + r for i, r in table]
        fmt = ".%df" % settings.RESULT_PRECISION
        tabtxt = tabulate(txttable, headers=table.headers, floatfmt=fmt)
        fid.write(tabtxt)
        fid.write("\n\n")
        sumtable = [[i] + r for i, r in summary_table]
        tabtxt = tabulate(
            sumtable, headers=summary_table.headers, floatfmt=fmt
        )
        fid.write(tabtxt)
    info("Created output file: %s" % fname)


def write_table_ajax(table, is_summary=False):
    if is_summary:
        fname = get_table_fname(table, "_summary_ajax.txt", "html")
    else:
        fname = get_table_fname(table, "_ajax.txt", "html")
    with open(fname, "w") as fid:
        fid.write("{\n")
        fid.write('  "data": [\n')
        pairs = [(_id, row) for (_id, row) in table]
        for _id, row in pairs[:-1]:
            fid.write("    [\n")
            fid.write('      "%s",\n' % str(_id))
            for elem in row[:-1]:
                fid.write('      "%s",\n' % str(elem))
            fid.write('      "%s"\n' % str(row[-1]))
            fid.write("    ],\n")
        _id, row = pairs[-1]
        fid.write("    [\n")
        fid.write('      "%s",\n' % str(_id))
        for elem in row[:-1]:
            fid.write('      "%s",\n' % str(elem))
        fid.write('      "%s"\n' % str(row[-1]))
        fid.write("    ]\n")
        fid.write("  ]\n")
        fid.write("}\n")
    info("Created output file: %s" % fname)
