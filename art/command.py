import argparse
import atexit
import logging
import os
import shutil
import tempfile

from art.config import ArtConfig, FileMapEntry
from art.excs import Problem
from art.git import git_clone
from art.manifest import Manifest
from art.prepare import fork_configs_from_work_dir, run_prepare
from art.wrap import create_wrapfile
from art.write import write


def get_argument_parser():
    ap = argparse.ArgumentParser()
    source_group = ap.add_argument_group("Source options")
    source_group.add_argument(
        "--git-source", metavar="URL", help="Git repository URL (passed to `git clone`)"
    )
    source_group.add_argument(
        "--git-ref", default="master", help="Git reference (default %(default)s)"
    )
    source_group.add_argument("--local-source", help="Local source path")
    source_group.add_argument(
        "--config-file",
        default="art.yaml",
        help="Configuration filename within the source (default %(default)s)",
    )

    dest_group = ap.add_argument_group("Destination options")

    dest_group.add_argument(
        "--dest", "-d", help="Destination base path, e.g. `./dist`, `s3://artifacts/foo"
    )
    dest_group.add_argument(
        "--suffix",
        "-s",
        dest="suffixes",
        action="append",
        help="Destination suffix (e.g. `release`)",
    )
    dest_group.add_argument(
        "--suffix-description",
        action="store_true",
        help="Attempt to derive a suffix from the `git describe` of the source",
    )
    ap.add_argument(
        "--debug",
        dest="log_level",
        const=logging.DEBUG,
        action="store_const",
        help="Be debuggingly verbose",
    )
    ap.add_argument(
        "--file",
        dest="files",
        action="append",
        help="Add a file glob for adding to the destination. You should probably use a configuration file instead.",
    )
    return ap


def run_command(argv=None):
    ap = get_argument_parser()
    args = ap.parse_args(argv)
    logging.basicConfig(level=(args.log_level or logging.INFO))

    config = ArtConfig()
    config.update_from({"dest": args.dest})
    if args.git_source:
        config.repo_url = args.git_source
        config.ref = args.git_ref
        config.work_dir = tempfile.mkdtemp(prefix="art-git-")
        git_clone(config)
        atexit.register(shutil.rmtree, config.work_dir)
    elif args.local_source:
        config.repo_url = config.work_dir = os.path.abspath(args.local_source)
    else:
        ap.error("Either a git source or a local source must be defined")

    for config in fork_configs_from_work_dir(config, filename=args.config_file):
        try:
            process_config_postfork(args, config)
        except Problem as p:
            ap.error("config %s: %s" % (config.name, p))


def process_config_postfork(args, config):
    if not config.dest:
        raise Problem(
            "No destination specified (on command line or in config in source)"
        )
    if config.dest.startswith("./"):
        config.dest = os.path.abspath(config.dest)
    for file in args.files or ():
        config.file_map.append(FileMapEntry(source=file))
    run_prepare(config)
    manifest = Manifest.generate(config)
    if not manifest["files"]:
        raise Problem("No files were copied (use config or --file?)")
    suffixes = []
    if args.suffix_description and manifest["rev"]["description"]:
        suffixes.append(manifest["rev"]["description"])
    suffixes.extend(args.suffixes or ())
    if not suffixes:
        raise Problem("No write destinations (use --suffix?)")
    wrap_temp = create_wrapfile(config, manifest)
    for suffix in suffixes:
        write(
            config,
            dest=config.dest,
            path_suffix=suffix,
            manifest=manifest,
            wrap_filename=wrap_temp,
        )
    if wrap_temp:
        os.unlink(wrap_temp)


if __name__ == "__main__":
    run_command()
