"""
Backup the json file data that is stored at SciServer
"""

import sys
import os
import json
import logging
from datetime import datetime
import otter

log = logging.getLogger(__file__)

def main():

    import argparse
    p = argparse.ArgumentParser()
    p.add_argument(
        "--arango-url",
        "-u",
        default=os.environ.get("ARANGO_URL_BACKUPS", "https://localhost:8529")
    )
    p.add_argument(
        "--outpath",
        "-o",
        default=os.path.join(
            os.getcwd(),
            "backups",
            f"backup-{datetime.today().strftime('%Y-%m-%d')}"
        )
    )
    p.add_argument(
        "--password",
        default=os.environ.get("ARANGO_USER_PASSWORD", "")
    )
    p.add_argument(
        "--username",
        default="user-guest"
    )
    args = p.parse_args()

    # set some special cases for calling from the bash script
    if args.arango_url == "_NULL":
        args.arango_url = os.environ.get("ARANGO_URL_BACKUPS", "https://localhost:8529")
    if args.outpath == "_NULL":
        args.outpath = os.path.join(
            os.getcwd(),
            "backups",
            f"backup-{datetime.today().strftime('%Y-%m-%d')}"
        )
    if args.password == "_NULL":
        args.password = os.environ.get("ARANGO_USER_PASSWORD", "")
    if args.username == "_NULL":
        args.username = "user-guest"

    # connect to the sciserver database
    db = otter.Otter(
        url = args.arango_url,
        password = args.password,
        username = args.username
    )

    log.info("Connected to the SciServer database")
    
    # make two directories
    transient_backup = os.path.join(args.outpath, "transient-collection")
    vetting_backup = os.path.join(args.outpath, "vetting-collection")
    
    if not os.path.exists(args.outpath):
        os.makedirs(args.outpath)

    if not os.path.exists(transient_backup):
        os.makedirs(transient_backup)

    if not os.path.exists(vetting_backup):
        os.makedirs(vetting_backup)

    log.info(f"Created the backup directories at {args.outpath}")
    
    # get all of the documents in the transient collection
    transient_data = db.query()
    for t in transient_data:
        tpath = os.path.join(
                    transient_backup,
                    f"{t.default_name.replace(' ', '-')}.json"
                )
        with open(tpath, "w+") as f:
            json.dump(
                dict(t),
                f,
                indent=4
            )

    log.info(f"Finished backing up the transient collection to {transient_backup}")
            
    # then get the entire vetting collection
    q = """
FOR t IN vetting
    RETURN t
"""
    
    vetting_data = db.AQLQuery(q, rawResults=True, batch_size=100_000_000)

    for v in vetting_data:
        vpath = os.path.join(
            vetting_backup,
            f"{v['name']['default_name']}.json"
        )
        with open(vpath, "w+") as f:
            json.dump(
                v,
                f,
                indent=4
            )

    log.info(f"Finished backing up the vetting collection to {vetting_backup}")

if __name__ == "__main__":
    sys.exit(main())
