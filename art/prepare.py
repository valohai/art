import os
from subprocess import check_call

import yaml

import logging

log = logging.getLogger(__name__)


def run_prepare(cfg):
    for prepare_step in cfg.prepare:
        log.info("Running prepare step: %s", prepare_step)
        check_call(prepare_step, shell=True, cwd=cfg.work_dir)


def update_config_from_work_dir(cfg):
    repo_cfg_path = os.path.join(cfg.work_dir, "art.yaml")
    if os.path.isfile(repo_cfg_path):
        log.info("Updating config from %s" % repo_cfg_path)
        with open(repo_cfg_path, "r") as infp:
            repo_cfg_data = yaml.safe_load(infp)
        cfg.update_from(repo_cfg_data)
