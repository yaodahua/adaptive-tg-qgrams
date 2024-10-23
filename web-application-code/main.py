import json
import os
from pathlib import Path
import pickle
import re
import time
import docker
import numpy as np
import requests
from config import (
    APP_NAMES,
    CHROME_CONTAINER_NAME,
    DIMESHIFT_NAME,
    DISTANCE_GENERATOR_NAME,
    DIVERSITY_STRATEGY_NAMES,
    GENERATOR_NAMES,
    QGRAMS_GENERATOR_NAME,
    RANDOM_GENERATOR_NAME,
    SEQUENCE_DIVERSITY_STRATEGY_NAME,
)
from executors.executor import Executor
from generators.test_case_generator import TestCaseGenerator
from global_log import GlobalLog
from individuals.individual import Individual
from parsing.instrument import Instrument
from utils.file_utils import get_coverage_targets_file
from utils.randomness_utils import RandomGenerator, set_random_seed
from tqdm import tqdm

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
    "--generator-name",
    help="Name of the generator",
    type=str,
    choices=GENERATOR_NAMES,
    default=RANDOM_GENERATOR_NAME,
)
args.add_argument("--budget", help="Budget in seconds", type=int, default=180)
args.add_argument(
    "--seed", help="Seed for random number generation", type=int, default=-1
)
args.add_argument("--progress", help="Activate progress bar", action="store_true")
args.add_argument(
    "--resume-filepath",
    help="Path to the json file containing the execution stats for resuming",
    type=str,
    default=None,
)
args.add_argument(
    "--max-length", help="Maximum length of the test case", type=int, default=30
)
args.add_argument(
    "--num-candidates",
    help=f"Number of candidates for generators {DISTANCE_GENERATOR_NAME} and {QGRAMS_GENERATOR_NAME}",
    type=int,
    default=5,
)
args.add_argument(
    "--q",
    help=f"Number of qgrams for generator {QGRAMS_GENERATOR_NAME}",
    type=int,
    default=2,
)
args.add_argument(
    "--diversity-strategy",
    help=f"Number of candidates for generators {DISTANCE_GENERATOR_NAME} and {QGRAMS_GENERATOR_NAME}",
    type=str,
    choices=DIVERSITY_STRATEGY_NAMES,
    default=SEQUENCE_DIVERSITY_STRATEGY_NAME,
)
args, _ = args.parse_known_args()


if __name__ == "__main__":

    logger = GlobalLog(logger_prefix="Main")

    app_name = args.app_name
    generator_name = args.generator_name
    budget = args.budget
    max_length = args.max_length
    num_candidates = args.num_candidates
    q = args.q
    progress = args.progress
    diversity_strategy = args.diversity_strategy
    resume_filepath = args.resume_filepath

    if resume_filepath is not None:
        assert os.path.exists(resume_filepath), "Resume filepath does not exist"
        assert resume_filepath.endswith(
            ".json"
        ), "Resume filepath should be a json file"

        prefix = resume_filepath.split(os.sep)[-1]
        parent_filepath = Path(resume_filepath).parent

        match_seed = re.search(r"(\d+).json", prefix)
        match_date = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", prefix)

        assert match_seed is not None, "Seed not found in the filename"
        assert match_date is not None, "Date not found in the filename"
        seed = int(match_seed.group(0).replace(".json", ""))
        previous_date = match_date.group(0)

        if args.seed != -1:
            logger.info(
                f"Command line seed is {args.seed} is ignored in favor of the seed in the filename {seed}"
            )

        with open(resume_filepath, "r") as f:
            data = json.load(f)
            exhausted_budget = data["exhausted_budget"]
            assert not exhausted_budget, "Budget is exhausted, no need to resume"
            previous_time_elapsed = data["time_elapsed"]

            assert (
                data["app_name"] == app_name
            ), "App name is different from previous execution"
            assert (
                data["budget"] == budget
            ), "Budget is different from previous execution"

            budget -= previous_time_elapsed
            previous_iterations = data["iterations"]
            assert (
                max_length == data["max_length"]
            ), "Max length is different from previous execution"
            assert (
                data["generator"] == generator_name
            ), "Generator name is different from previous execution"
            if (
                generator_name == DISTANCE_GENERATOR_NAME
                or generator_name == QGRAMS_GENERATOR_NAME
            ):
                assert (
                    data["num_candidates"] == num_candidates
                ), "Number of candidates is different from previous execution"

                assert (
                    data["diversity_strategy"] == diversity_strategy
                ), "Diversity strategy is different from previous execution"

                if generator_name == QGRAMS_GENERATOR_NAME:
                    assert (
                        data["q"] == q
                    ), "Number of qgrams is different from previous execution"

            logger.info(
                f"Resuming execution for {app_name} from file {resume_filepath} "
                f"for the remainig budget of {budget} seconds"
            )

            previous_generation_times = data["generation_times"]
            previous_execution_times = data["execution_times"]
            previous_coverage_over_time = data["coverage_over_time"]
            previous_individual_lengths = data["individual_lengths"]

        if generator_name != RANDOM_GENERATOR_NAME:
            with open(
                os.path.join(
                    parent_filepath, f"{previous_date}_{seed}_generator_state.pkl"
                ),
                "rb",
            ) as f:
                generator_state = pickle.load(f)
        else:
            generator_state = None

        with open(
            os.path.join(parent_filepath, f"{previous_date}_{seed}_random_state.pkl"),
            "rb",
        ) as f:
            random_state = pickle.load(f)

        with open(
            os.path.join(
                parent_filepath, f"{previous_date}_{seed}_covered_targets.pkl"
            ),
            "rb",
        ) as f:
            covered_targets = pickle.load(f)

        with open(
            os.path.join(
                parent_filepath, f"{previous_date}_{seed}_final_test_suite.pkl"
            ),
            "rb",
        ) as f:
            final_test_suite = pickle.load(f)

        set_random_seed(seed=seed, random_state=random_state)

    else:

        seed = args.seed

        if seed == -1:
            # generate seed randomly
            try:
                # in some machines, depending on the architecture, 2^32 might overflow
                seed = np.random.randint(2**32 - 1, dtype="int64").item()
            except ValueError as _:
                seed = np.random.randint(2**30 - 1, dtype="int64").item()

        set_random_seed(seed=seed)

    if (
        generator_name == DISTANCE_GENERATOR_NAME
        or generator_name == QGRAMS_GENERATOR_NAME
    ):
        assert num_candidates > 0, "Number of candidates should be positive"
    if generator_name == QGRAMS_GENERATOR_NAME:
        assert q > 0, "Number of qgrams should be positive"

    executor = Executor.load_executor(app_name=app_name)
    try:
        network_name = executor.start_containers()
    except RuntimeError as e:
        logger.error(f"Error starting containers: {e}")
        exit(1)

    coverage_targets_filepath = get_coverage_targets_file(app_name=app_name)

    if os.path.exists(coverage_targets_filepath):
        with open(coverage_targets_filepath, "rb") as f:
            coverage_targets = pickle.load(f)
    else:
        instrument_instance = Instrument(app_name=app_name)
        coverage_targets = instrument_instance.add_probes_and_get_coverage_targets()

    if resume_filepath is not None:
        uncovered_targets = [
            ct.clone() for ct in coverage_targets if ct not in covered_targets
        ]
    else:
        uncovered_targets = [ct.clone() for ct in coverage_targets]
        covered_targets = []

    if progress:
        pbar = tqdm(total=len(coverage_targets), desc="Coverage Progress", unit="unit")
        if resume_filepath is not None:
            pbar.update(len(covered_targets))

    generator = TestCaseGenerator.load_generator(
        diversity_strategy=diversity_strategy,
        generator_name=generator_name,
        num_candidates=num_candidates,
        app_name=app_name,
        q=q,
    )

    if resume_filepath is not None and generator_state is not None:
        generator.set_state(generator_state=generator_state)

    if resume_filepath is not None and final_test_suite is not None:
        generator.set_final_test_suite(final_test_suite=final_test_suite)

    start_time = time.perf_counter()
    result_json = {}
    iterations = 0
    coverage_over_time = []
    generation_times = []
    execution_times = []
    individual_lengths = []

    compile_instr = True

    chrome_container_name = None

    try:

        while (
            len(covered_targets) < len(coverage_targets)
            and time.perf_counter() - start_time < budget
        ):

            try:
                _ = executor.get_container_name(
                    network_name=network_name, container_type=CHROME_CONTAINER_NAME
                )
            except RuntimeError:
                assert (
                    chrome_container_name is not None
                ), "Chrome container name is None"

                max_counter = 10
                exception = True
                while exception and max_counter > 0:
                    try:
                        executor.start_container_by_name(
                            network_name=network_name,
                            container_name=chrome_container_name,
                            add_container_to_network=True,
                        )
                        exception = False
                    except (
                        docker.errors.NotFound,
                        requests.exceptions.ConnectionError,
                    ) as e:
                        logger.error(f"Error starting container: {e}")
                        max_counter -= 1
                        time.sleep(1)
                assert (
                    max_counter > 0
                ), f"Max counter for starting container {chrome_container_name} reached"

            start_time_generation = time.perf_counter()
            individual = generator.generate(
                uncovered_targets=uncovered_targets, max_length=max_length
            )
            end_time_generation = time.perf_counter()
            individual_lengths.append(len(individual.statements))

            max_counter = 10
            exception = True
            excecution_output = None
            while exception and max_counter > 0:

                try:
                    start_time_execution = time.perf_counter()
                    execution_output = executor.execute(
                        individual=individual,
                        network_name=network_name,
                        compile_instr=compile_instr,
                    )
                    exception = False
                except (
                    ValueError,
                    RuntimeError,
                    docker.errors.NotFound,
                    docker.errors.APIError,
                ) as err:
                    max_counter -= 1
                    time.sleep(1)
                    logger.error(
                        f"Error during execution: {err}. "
                        f"All containers: {executor.list_all_containers()} "
                        f"All networks: {executor.list_all_networks()}"
                    )

            end_time_execution = time.perf_counter()

            assert max_counter > 0, "Max counter for executing a test reached"
            assert execution_output is not None, "Execution output is None"
            current_covered_targets = execution_output.get_covered_targets()

            for ct in current_covered_targets:
                if ct in coverage_targets and ct not in covered_targets:
                    ct_clone = ct.clone()
                    ct_clone.iteration = iterations
                    covered_targets.append(ct_clone)
                    if progress:
                        pbar.update(1)
                if ct in uncovered_targets:
                    uncovered_targets.remove(ct)

            if progress:
                pbar.update(0)

            logger.debug(f"Current covered targets: {len(current_covered_targets)}")
            logger.debug(f"Global covered targets: {len(covered_targets)}")
            logger.debug(f"Global uncovered targets: {len(uncovered_targets)}")
            logger.debug(
                f"Global coverage: {100 * len(covered_targets) / len(coverage_targets):.2f}%"
            )
            logger.debug(f"Time elapsed: {time.perf_counter() - start_time:.2f}s")
            logger.debug(
                f"Time generation: {end_time_generation - start_time_generation:.2f}s"
            )
            logger.debug(
                f"Time execution: {end_time_execution - start_time_execution:.2f}s"
            )
            coverage_over_time.append(
                100 * len(covered_targets) / len(coverage_targets)
            )

            assert len(uncovered_targets) + len(covered_targets) == len(
                coverage_targets
            ), "Sum of covered and uncovered targets should be equal to the total number of targets"

            generation_times.append(end_time_generation - start_time_generation)
            execution_times.append(end_time_execution - start_time_execution)

            feasible_statements_strings = execution_output.get_feasible_prefix(
                app_name=app_name
            )
            feasible_individual = Individual.parse_statement_strings(
                statement_strings=feasible_statements_strings
            )
            generator.update_final_test_suite(
                individual=feasible_individual, covered_targets=current_covered_targets
            )

            # stopping the chrome container is needed to avoid a memory leak during the execution
            chrome_container_name = executor.get_container_name(
                network_name=network_name, container_type=CHROME_CONTAINER_NAME
            )
            exception = True
            max_counter = 10
            while exception and max_counter > 0:
                try:
                    executor.stop_container_by_name(
                        network_name=network_name,
                        container_name=chrome_container_name,
                        remove_container_from_network=True,
                    )
                    exception = False
                except docker.errors.APIError as e:
                    logger.error(f"Error stopping container: {e}")
                    max_counter -= 1
                    time.sleep(1)
            assert (
                max_counter > 0
            ), f"Max counter for stopping container {chrome_container_name} reached"

            # compiling the instrumented class is only needed once
            compile_instr = False
            iterations += 1

    finally:
        executor.stop_containers(network_name=network_name)
        if progress:
            pbar.close()

        time_elapsed = round(time.perf_counter() - start_time, 2)
        date = time.strftime("%Y-%m-%d_%H-%M-%S")
        exhausted_budget = time.perf_counter() - start_time > budget or len(
            covered_targets
        ) == len(coverage_targets)
        if resume_filepath is not None:
            date = previous_date
            time_elapsed += previous_time_elapsed
            iterations += previous_iterations
            # reset budget to the original value
            budget = args.budget
            generation_times = previous_generation_times + generation_times
            execution_times = previous_execution_times + execution_times
            coverage_over_time = previous_coverage_over_time + coverage_over_time
            individual_lengths = previous_individual_lengths + individual_lengths

        result_json["seed"] = seed
        result_json["exhausted_budget"] = exhausted_budget
        result_json["time_elapsed"] = time_elapsed
        result_json["iterations"] = iterations
        result_json["max_length"] = max_length
        result_json["generator"] = generator_name
        if (
            generator_name == DISTANCE_GENERATOR_NAME
            or generator_name == QGRAMS_GENERATOR_NAME
        ):
            result_json["num_candidates"] = num_candidates
            result_json["diversity_strategy"] = diversity_strategy
            if generator_name == QGRAMS_GENERATOR_NAME:
                result_json["q"] = q
        result_json["app_name"] = app_name
        result_json["budget"] = budget
        result_json["num_covered_targets"] = len(covered_targets)
        result_json["num_uncovered_targets"] = len(uncovered_targets)
        result_json["global_coverage"] = round(
            100 * len(covered_targets) / len(coverage_targets), 3
        )
        result_json["avg_generation_time"] = np.mean(generation_times)
        result_json["avg_execution_time"] = np.mean(execution_times)
        result_json["avg_individual_length"] = np.mean(individual_lengths)
        result_json["generation_times"] = generation_times
        result_json["execution_times"] = execution_times
        result_json["coverage_over_time"] = coverage_over_time
        result_json["individual_lengths"] = individual_lengths

        json_string = json.dumps(result_json, indent=4)

        if (
            generator_name == DISTANCE_GENERATOR_NAME
            or generator_name == QGRAMS_GENERATOR_NAME
        ):
            results_dir = os.path.join(
                os.getcwd(),
                "results",
                app_name,
                generator_name + "_" + diversity_strategy,
            )
        else:
            results_dir = os.path.join(os.getcwd(), "results", app_name, generator_name)

        os.makedirs(results_dir, exist_ok=True)
        result_filename = os.path.join(results_dir, f"{date}_{seed}.json")

        with open(
            os.path.join(results_dir, result_filename), "w+", encoding="utf-8"
        ) as f:
            f.write(json_string)

        test_suite_filename = os.path.join(results_dir, f"{date}_{seed}_test_suite.txt")
        with open(test_suite_filename, "w+", encoding="utf-8") as f:
            f.write(generator.write_final_test_suite(covered_targets=covered_targets))

        covered_targets_filename = os.path.join(
            results_dir, f"{date}_{seed}_covered_targets.pkl"
        )
        with open(covered_targets_filename, "wb") as f:
            pickle.dump(covered_targets, f)

        generator_state = generator.get_state()
        if generator_state is not None:
            generator_state_filename = os.path.join(
                results_dir, f"{date}_{seed}_generator_state.pkl"
            )
            with open(generator_state_filename, "wb") as f:
                pickle.dump(generator_state, f)

        random_state = RandomGenerator.get_instance().rnd_state.get_state()
        random_state_filename = os.path.join(
            results_dir, f"{date}_{seed}_random_state.pkl"
        )
        with open(random_state_filename, "wb") as f:
            pickle.dump(random_state, f)

        final_test_suite = generator.get_final_test_suite()
        final_test_suite_filename = os.path.join(
            results_dir, f"{date}_{seed}_final_test_suite.pkl"
        )
        with open(final_test_suite_filename, "wb") as f:
            pickle.dump(final_test_suite, f)
