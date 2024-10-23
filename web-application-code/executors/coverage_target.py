class CoverageTarget:

    def __init__(
        self, target_type: str, line_number: int, method_name: str, iteration: int = -1
    ):
        assert target_type in ["M", "IF", "ELSE"], f"Invalid target type {target_type}"
        assert isinstance(line_number, int), f"Invalid line number {line_number}"
        assert method_name is None or isinstance(
            method_name, str
        ), f"Invalid method name {method_name}"

        self.target_type = target_type
        self.line_number = line_number
        self.method_name = method_name
        self.iteration = iteration

    def __str__(self):
        if self.iteration != -1:
            return f"{self.target_type}-{self.line_number} {self.method_name} ({self.iteration})"
        return f"{self.target_type}-{self.line_number} {self.method_name}"

    def __eq__(self, other: "CoverageTarget"):
        return (
            self.target_type == other.target_type
            and self.line_number == other.line_number
            and self.method_name == other.method_name
        )

    def __hash__(self) -> int:
        return hash(f"{self.target_type}-{self.line_number} {self.method_name}")

    def clone(self) -> "CoverageTarget":
        return CoverageTarget(
            target_type=self.target_type,
            line_number=self.line_number,
            method_name=self.method_name,
            iteration=self.iteration,
        )
