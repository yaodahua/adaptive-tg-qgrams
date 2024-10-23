from statements.statement import Statement


class ResetStatement(Statement):

    def to_string(self) -> str:
        return "ResetAppState.reset();"

    def clone(self) -> "ResetStatement":
        return ResetStatement()

    @property
    def name(self) -> str:
        return "ResetStatement"

    def from_string(statement_string: str) -> "ResetStatement":
        if statement_string == "ResetAppState.reset();":
            return ResetStatement()
        raise ValueError(f"Unknown statement: {statement_string}")

    def __eq__(self, other: "ResetStatement") -> bool:
        if isinstance(other, ResetStatement):
            return True
        return False
