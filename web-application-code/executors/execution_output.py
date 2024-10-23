from typing import List, Optional, Tuple
import re

from config import APP_NAMES, DIMESHIFT_NAME
from executors.coverage_target import CoverageTarget
from individuals.individual import Individual
from utils.file_utils import HELPER_FUNCTION_NAME, get_main_class_path


class ExecutionOutput:
    def __init__(self, exit_code: int, output: str):
        self.exit_code = exit_code
        self.output = output

    def get_covered_targets(self) -> List[CoverageTarget]:
        previous_line = None
        targets = []
        for line in self.output.split("\n"):
            match = re.search(r"INFO:\s*(M|IF|ELSE)-\d+", line)
            if match:
                match_split = match.group(0).replace("INFO: ", "").split("-")
                target_type = match_split[0]
                line_number = int(match_split[1])

                match = re.search(r".*ClassUnderTestInstr\s*(\w+)", previous_line)
                method_name = None
                if match:
                    method_name = match.group(1)

                target = CoverageTarget(
                    target_type=target_type,
                    line_number=line_number,
                    method_name=method_name,
                )
                targets.append(target)

            previous_line = line

        return targets

    def _get_uncaught_exception_line(self) -> Optional[int]:
        for line in self.output.split("\n"):
            match = re.search(r".*at main\.Main\.main\(Main\.java:(\d+)\)", line)
            if match:
                return int(match.group(1))
        return None

    def _get_caught_exception_lines(self) -> List[int]:
        exception_lines = []
        for line in self.output.split("\n"):
            match = re.search(
                r".*Exception thrown in method: (\w+) at line: (\d+)", line
            )
            if match:
                exception_lines.append(int(match.group(2)))
        return sorted(exception_lines)

    def get_feasible_prefix(self, app_name: str) -> List[str]:

        assert app_name in APP_NAMES, f"App name {app_name} is not valid"

        code_with_lines_uncaught_exception = self._filter_by_uncaught_exceptions(
            app_name=app_name
        )
        code_caught_exceptions = self._filter_by_caught_exceptions(
            code_with_lines=code_with_lines_uncaught_exception
        )
        return code_caught_exceptions

    def _filter_by_caught_exceptions(
        self, code_with_lines: List[Tuple[int, str]]
    ) -> List[str]:
        exception_lines = self._get_caught_exception_lines()

        code = []

        for code_with_line in code_with_lines:

            if code_with_line[0] not in exception_lines:
                code.append(code_with_line[1])

        return code

    def _filter_by_uncaught_exceptions(self, app_name: str) -> List[Tuple[int, str]]:
        exception_line = self._get_uncaught_exception_line()
        if exception_line is None:
            exception_line = -1

        main_class_path = get_main_class_path(app_name=app_name)
        code_with_lines = []
        append = False
        with open(main_class_path, "r") as f:
            for i, line in enumerate(f.readlines()):

                if line.strip() == "" or line == "}":
                    append = False

                if append:
                    if HELPER_FUNCTION_NAME in line:
                        line_cleaned = (
                            line.strip()
                            .replace(f"{HELPER_FUNCTION_NAME}(() -> ", "")
                            .replace(");", ";")
                        )
                    else:
                        line_cleaned = line.strip()
                    code_with_lines.append((i + 1, line_cleaned))

                if "public static void main(String[] args)" in line:
                    append = True

                if i + 1 == exception_line - 1:
                    break

        return code_with_lines


if __name__ == "__main__":
    app_name = DIMESHIFT_NAME

    output = """
    Sat Jul 13 13:42:28 GMT 2024 WARN: Establishing SSL connection without server's identity verification is not recommended. According to MySQL 5.5.45+, 5.6.26+ and 5.7.6+ requirements SSL connection must be established by default if explicit option isn't set. For compliance with existing applications not using SSL the verifyServerCertificate property is set to 'false'. You need either to explicitly disable SSL by setting useSSL=false, or set useSSL=true and provide truststore for server certificate verification.
    Jul 13, 2024 1:42:28 PM org.openqa.selenium.remote.ProtocolHandshake createSession
    INFO: Detected dialect: OSS
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr addWalletWalletsManagerPage
    INFO: IF-822
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr closeAddWalletPage
    INFO: IF-597
    Exception thrown in method: main at line: 16
    Exception thrown in method: main at line: 18
    Exception thrown in method: main at line: 19
    Exception thrown in method: main at line: 20
    Exception thrown in method: main at line: 22
    Exception thrown in method: main at line: 23
    Exception thrown in method: main at line: 24
    Exception thrown in method: main at line: 27
    Exception thrown in method: main at line: 28
    Exception thrown in method: main at line: 30
    Exception thrown in method: main at line: 31
    Exception thrown in method: main at line: 33
    Exception thrown in method: main at line: 34
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr addWalletWalletsManagerPage
    INFO: IF-822
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr addAddWalletPage
    INFO: IF-578
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr addWalletWalletsManagerPage
    INFO: IF-822
    Jul 13, 2024 1:42:29 PM main.ClassUnderTestInstr addAddWalletPage
    INFO: IF-578
    Jul 13, 2024 1:42:30 PM main.ClassUnderTestInstr manageWalletAccessWalletsManagerPage
    INFO: IF-929
    Jul 13, 2024 1:42:30 PM main.ClassUnderTestInstr removeAccessWalletAccessManagerPage
    INFO: IF-520
    Exception in thread "main" org.openqa.selenium.TimeoutException: Expected condition failed: waiting for presence of element located by: By.xpath: (//div[@class="modal-body modal-body-default"]/div[@class="table-responsive"]//a)[0] (tried for 0 second(s) with 500 MILLISECONDS interval)
            at org.openqa.selenium.support.ui.WebDriverWait.timeoutException(WebDriverWait.java:126)
            at org.openqa.selenium.support.ui.FluentWait.until(FluentWait.java:233)
            at po_utils.Wait.forElementBeingPresentDefaultTimeout(Wait.java:589)
            at po_utils.BasePageObject.getElementOnPageAfterWait(BasePageObject.java:866)
            at po_utils.BasePageObject.findElementSafely(BasePageObject.java:783)
            at po_utils.BasePageObject.clickOn(BasePageObject.java:721)
            at main.ClassUnderTestInstr.removeAccessWalletAccessManagerPage(ClassUnderTestInstr.java:414)
            at main.Main.lambda$main$20(Main.java:44)
            at main.Main.runWithExceptionHandling(Main.java:55)
            at main.Main.main(Main.java:44)
    Caused by: org.openqa.selenium.NoSuchElementException: Cannot locate an element using By.xpath: (//div[@class="modal-body modal-body-default"]/div[@class="table-responsive"]//a)[0]
    For documentation on this error, please visit: http://seleniumhq.org/exceptions/no_such_element.html
    Build info: version: '3.3.1', revision: '', time: '2017-03-19 23:13:04 +0100'
    System info: host: '1d61c04f4f82', ip: '172.17.0.4', os.name: 'Linux', os.arch: 'amd64', os.version: '6.5.0-41-generic', java.version: '1.8.0_362'
    Driver info: driver.version: unknown
            at org.openqa.selenium.support.ui.ExpectedConditions.lambda$findElement$0(ExpectedConditions.java:899)
            at java.util.Optional.orElseThrow(Optional.java:290)
            at org.openqa.selenium.support.ui.ExpectedConditions.findElement(ExpectedConditions.java:898)
            at org.openqa.selenium.support.ui.ExpectedConditions.access$000(ExpectedConditions.java:44)
            at org.openqa.selenium.support.ui.ExpectedConditions$6.apply(ExpectedConditions.java:184)
            at org.openqa.selenium.support.ui.ExpectedConditions$6.apply(ExpectedConditions.java:181)
            at org.openqa.selenium.support.ui.FluentWait.until(FluentWait.java:209)
            ... 8 more
    """

    execution_output = ExecutionOutput(exit_code=0, output=output)
    feasible_statements_strings = execution_output.get_feasible_prefix(
        app_name=app_name
    )
    print("\n".join(feasible_statements_strings))
    print()
    feasible_individual = Individual.parse_statement_strings(
        statement_strings=feasible_statements_strings
    )
    feasible_individual_clone = feasible_individual.clone()
    filtered_statements = Individual.remove_dangling_statements(
        statements=feasible_individual.statements
    )
    feasible_individual_clone.statements = filtered_statements
    print("\n".join(feasible_individual_clone.to_string()))
