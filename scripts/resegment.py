"""
Find undetected introductions in the protocols. After finding an intro,
tag the next paragraph as an utterance.
"""
from pyparlaclarin.refine import format_texts
from pyriksdagen.db import filter_db, load_patterns
from pyriksdagen.refine import (
    detect_mps,
    find_introductions,
    update_ids,
    update_hashes,
)
from pyriksdagen.utils import infer_metadata
from lxml import etree
import pandas as pd
import os, progressbar, argparse


def main(args):
    start_year = args.start
    end_year = args.end
    root = ""  # "../"
    pc_folder = root + "corpus/"
    folders = os.listdir(pc_folder)

    mp_db = pd.read_csv(root + "corpus/members_of_parliament.csv")
    minister_db = pd.read_csv(root + "corpus/ministers.csv", parse_dates=True)

    parser = etree.XMLParser(remove_blank_text=True)
    for outfolder in progressbar.progressbar(folders):
        if os.path.isdir(pc_folder + outfolder):
            outfolder = outfolder + "/"
            protocol_ids = os.listdir(pc_folder + outfolder)
            protocol_ids = [
                protocol_id.replace(".xml", "")
                for protocol_id in protocol_ids
                if protocol_id.split(".")[-1] == "xml"
            ]

            first_protocol_id = protocol_ids[0]
            metadata = infer_metadata(first_protocol_id)
            year = metadata["year"]
            if year >= start_year and year <= end_year:
                for protocol_id in protocol_ids:
                    metadata = infer_metadata(protocol_id)
                    filename = pc_folder + outfolder + protocol_id + ".xml"
                    root = etree.parse(filename, parser).getroot()

                    # print(year, type(year))
                    years = [
                        int(elem.attrib.get("when").split("-")[0])
                        for elem in root.findall(
                            ".//{http://www.tei-c.org/ns/1.0}docDate"
                        )
                    ]

                    if not year in years:
                        year = years[0]

                    #if str(year) not in protocol_id:
                    #    print(protocol_id, year)
                    year_mp_db = filter_db(mp_db, year=year)
                    names = year_mp_db["name"]
                    ids = year_mp_db["id"]
                    names_ids = list(zip(names, ids))

                    pattern_db = load_patterns()
                    pattern_db = pattern_db[
                        (pattern_db["start"] <= year) & (pattern_db["end"] >= year)
                    ]
                    root = find_introductions(root, pattern_db, names_ids, minister_db=minister_db)
                    root = update_ids(root, protocol_id)
                    root = format_texts(root)
                    root = update_hashes(root, protocol_id)
                    b = etree.tostring(
                        root, pretty_print=True, encoding="utf-8", xml_declaration=True
                    )

                    f = open(filename, "wb")
                    f.write(b)
                    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1920)
    parser.add_argument("--end", type=int, default=2021)
    args = parser.parse_args()
    main(args)
