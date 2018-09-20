import glob
import os
import re

from art.config import ArtConfig


def gather_files(cfg: ArtConfig, base_dir):
    base_dir = os.path.abspath(base_dir)
    for fme in cfg.file_map:
        for file in glob.glob(os.path.join(base_dir, fme.source)):
            src_file = file
            dest_file = os.path.relpath(file, base_dir)
            if fme.strip:
                dest_file = os.path.join(*os.path.split(dest_file)[fme.strip :])
            if fme.rename:
                for from_r, to_r in fme.rename:
                    dest_file = re.sub(from_r, to_r, dest_file)
            yield (src_file, dest_file)


def get_files_for_manifest(config):
    files = {}
    for local_path, remote_path in gather_files(config, config.work_dir):
        stat = os.stat(local_path)
        files[remote_path] = {
            "path": os.path.relpath(local_path, config.work_dir),
            "size": stat.st_size,
            "ctime": stat.st_ctime,
            "mtime": stat.st_mtime,
        }
    return files
