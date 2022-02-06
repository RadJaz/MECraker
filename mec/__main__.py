import mec
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", required=True)

    run = subparser.add_parser("run")
    run.add_argument("--mecids", type=str, default=mec.KCcouncil)
    run.add_argument(
        "--watch-path", type=dir_path, default=os.path.join(Path.home(), "Downloads")
    )
    run.add_argument("--csv-path", type=str, default="csvs")

    reference = subparser.add_parser("ref")
    reference.add_argument("type", choices=["seqno", "fields"])
    reference.add_argument("--in-file", type=file_path, required=True)
    reference.add_argument("--out-file", type=str)

    args = parser.parse_args()

    if args.command == "run":
        mec.run(MECIDs=args.mecids, csv_path=args.csv_path, watch_path=args.watch_path)
    elif args.command == "ref":
        if not args.out_file:
            args.out_file = args.type + ".pdf"
        if args.type == "seqno":
            mec.report.reference.seqno(in_file=args.in_file, out_file=args.out_file)
        elif args.type == "fields":
            mec.report.reference.fields(in_file=args.in_file, out_file=args.out_file)


def dir_path(s):
    if os.path.isdir(s):
        return s
    else:
        raise NotADirectoryError(s)


def file_path(s):
    if os.path.isfile(s):
        return s
    else:
        raise FileNotFoundError(s)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\naborting!")
