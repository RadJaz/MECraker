import mec
import argparse
import os
from pathlib import Path
import sys
from yaml import safe_load_all as load_yaml
from pprint import pformat


def main():
    if len(sys.argv) == 1 and os.path.exists("MECraker.yaml"):
        args = config("MECraker.yaml")
    elif len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        filename = sys.argv[1]
        args = config(filename)
    else:
        args = None
    command(args)


def command(args=None):
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", required=True)

    run = subparser.add_parser("run")
    run.add_argument("--mecids", nargs="+", required=True)
    run.add_argument(
        "--watch-path", type=dir_path, default=os.path.join(Path.home(), "Downloads")
    )
    run.add_argument("--csv-path", type=str, default="csvs")
    run.add_argument("--reports-path", type=str, default="reports")

    reference = subparser.add_parser("ref")
    reference.add_argument("--type", choices=["seqno", "fields"])
    reference.add_argument("--in-file", type=file_path, required=True)
    reference.add_argument("--out-file", type=str)
    args = parser.parse_args(args)
    if args.command == "run":
        mec.run(
            MECIDs=args.mecids,
            csv_path=args.csv_path,
            watch_path=args.watch_path,
            reports_path=args.reports_path,
        )
    elif args.command == "ref":
        if not args.out_file:
            args.out_file = args.type + ".pdf"
        if args.type == "seqno":
            mec.report.reference.seqno(in_file=args.in_file, out_file=args.out_file)
        elif args.type == "fields":
            mec.report.reference.fields(in_file=args.in_file, out_file=args.out_file)


def config(filename):
    print("reading config {}".format(filename))
    with open(filename) as f:
        configs = list(load_yaml(f.read()))
    if len(configs) == 1:
        config = configs[0]
    else:
        options = "Please pick a config:\n"
        i = 0
        for config in configs:
            i += 1
            if "id" in config:
                options += "\n{}:\n{}\n".format(i, "\t" + config["id"])
                del config["id"]
            else:
                options += "\n{}:\n{}\n".format(
                    i, "\t" + pformat(config).replace("\n", "\n\t")
                )
        print(options + "\n")
        prompt = "Select an option (1-{}):".format(i)
        while True:
            selection = input(prompt)
            try:
                selection = int(selection)
            except:
                pass
            if selection in range(1, i + 1):
                config = configs[selection - 1]
                break
            print("Invalid selection. Try again.")
    args = [config["command"]]
    del config["command"]
    for key, value in config.items():
        if value == None:
            continue
        if type(value) == list:
            args.append("--" + key)
            args += value
            continue
        args += ["--" + key, value]
    return args


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
