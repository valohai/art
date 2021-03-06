import copy
import logging
import os
from subprocess import check_call

import yaml

from art.consts import DEFAULT_CONFIG_FILENAME

log = logging.getLogger(__name__)


def run_prepare(cfg):
    for prepare_step in cfg.prepare:
        log.info("Running prepare step: %s", prepare_step)
        check_call(prepare_step, shell=True, cwd=cfg.work_dir)


def fork_configs_from_data(base_cfg, cfg_data):
    if not isinstance(cfg_data, dict):
        raise TypeError("Invalid configuration (must be a dict, got %r)" % cfg_data)
    configs_dict = cfg_data["configs"] if "configs" in cfg_data else {None: cfg_data}
    for name, cfg_data in configs_dict.items():
        subcfg = copy.deepcopy(base_cfg)
        subcfg.update_from(cfg_data)
        subcfg.name = name or "default"
        if name:
            subcfg.dest += "/%s" % name
        yield subcfg


def fork_configs_from_work_dir(base_cfg, filename=DEFAULT_CONFIG_FILENAME):
    repo_cfg_path = os.path.join(base_cfg.work_dir, filename)
    if os.path.isfile(repo_cfg_path):
        log.info("Updating config from %s" % repo_cfg_path)
        with open(repo_cfg_path, "r") as infp:
            repo_cfg_data = yaml.safe_load(infp)
        return fork_configs_from_data(base_cfg, repo_cfg_data)
    if filename != DEFAULT_CONFIG_FILENAME:
        raise ValueError("non-default config filename %s not found" % filename)
    log.info("No config updates from file (%s didn't exist in source)" % filename)
    return [copy.deepcopy(base_cfg)]
