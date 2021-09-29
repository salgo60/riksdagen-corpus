"""
Prepare sample for segmentation annotation. Assumes you have generated a
sample with scripts/sample_pages.csv, and that you have a folder annotatordata
where the output files are placed.
"""
import pandas as pd
import os
import argparse
from lxml import etree
from pyparlaclarin.read import paragraph_iterator

def main(args):
    sample = pd.read_csv(args.infile)
    parser = etree.XMLParser(remove_blank_text=True)
    for _, row in sample.iterrows():
        protocol_id = row["package_id"]
        subfolder = protocol_id.split("-")[1] + "/"
        path = "corpus/" + subfolder + protocol_id + ".xml"
        root = etree.parse(path, parser).getroot()
        page = row["pagenumber"]
        
        newroot = etree.Element("page")
        for p in paragraph_iterator(root, page=page):
            for p in p.split("\n\n"):
                p = "\n" + " ".join(p.split()) + "\n"
                if p.strip()!= "":
                    u = etree.SubElement(newroot, "unknown")
                    u.text = p

        print(newroot)

        path = "annotatordata/" + protocol_id + "p" + str(page) + ".xml"
        b = etree.tostring(newroot, pretty_print=True, encoding="utf-8")
        f = open(path, "wb")
        f.write(b)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--infile", type=str, help="Sample location", default="sample.csv")
    args = parser.parse_args()
    main(args)
