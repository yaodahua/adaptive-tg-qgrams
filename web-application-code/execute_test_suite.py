import os
import pickle

from tqdm import tqdm
from config import APP_NAMES, CHROME_CONTAINER_NAME, DIMESHIFT_NAME
from executors.executor import Executor
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from parsing.instrument import Instrument
from utils.file_utils import get_coverage_targets_file

import argparse

args = argparse.ArgumentParser()
args.add_argument(
    "--app-name",
    help="Name of the app under test",
    type=str,
    choices=APP_NAMES,
    default=DIMESHIFT_NAME,
)
args.add_argument(
    "--test-suite-filepath", help="Test suite file", type=str, default=None
)
args, _ = args.parse_known_args()


if __name__ == "__main__":

    logger = GlobalLog(logger_prefix="execute_test_suite")

    app_name = args.app_name
    test_suite_filepath = args.test_suite_filepath

    assert os.path.exists(
        test_suite_filepath
    ), f"Test suite file {test_suite_filepath} does not exist"

    assert (
        app_name in test_suite_filepath
    ), f"App name {app_name} is not in the test suite file path"

    executor = Executor.load_executor(app_name=app_name)
    network_name = executor.start_containers()

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    if os.path.exists(coverage_targets_filepath):
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)
        compile_instr = False
    else:
        instrument_instance = Instrument(app_name=app_name)
        coverage_targets = instrument_instance.add_probes_and_get_coverage_targets()
        compile_instr = True

    uncovered_targets = [ct.clone() for ct in coverage_targets]
    covered_targets = []

    chrome_container_name = None

    test_suite = TestCaseGenerator.parse_final_test_suite(
        test_suite_filepath=test_suite_filepath
    )

    pbar = tqdm(total=len(test_suite), desc="Number of Tests Progress", unit="unit")

    try:

        for individual in test_suite:

            try:
                _ = executor.get_container_name(
                    network_name=network_name, container_type=CHROME_CONTAINER_NAME
                )
            except RuntimeError:
                assert (
                    chrome_container_name is not None
                ), "Chrome container name is None"
                executor.start_container_by_name(
                    network_name=network_name,
                    container_name=chrome_container_name,
                    add_container_to_network=True,
                )

            execution_output = executor.execute(
                individual=individual,
                network_name=network_name,
                compile_instr=compile_instr,
            )

            # stopping the chrome container is needed to avoid a memory leak during the execution
            chrome_container_name = executor.get_container_name(
                network_name=network_name, container_type=CHROME_CONTAINER_NAME
            )
            executor.stop_container_by_name(
                network_name=network_name,
                container_name=chrome_container_name,
                remove_container_from_network=True,
            )

            current_covered_targets = execution_output.get_covered_targets()

            pbar.update(1)

            for ct in current_covered_targets:
                if ct in coverage_targets and ct not in covered_targets:
                    ct_clone = ct.clone()
                    covered_targets.append(ct_clone)
                if ct in uncovered_targets:
                    uncovered_targets.remove(ct)

            logger.debug(f"Current covered targets: {len(current_covered_targets)}")
            logger.debug(f"Global covered targets: {len(covered_targets)}")
            logger.debug(f"Global uncovered targets: {len(uncovered_targets)}")
            logger.debug(
                f"Global coverage: {100 * len(covered_targets) / len(coverage_targets):.2f}%"
            )

            assert len(uncovered_targets) + len(covered_targets) == len(
                coverage_targets
            ), "Sum of covered and uncovered targets should be equal to the total number of targets"

    finally:
        pbar.close()
        executor.stop_containers(network_name=network_name)
