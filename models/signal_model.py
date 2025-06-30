from typing import Optional, List

class SignalObject:
    def __init__(
        self,
        name: str,
        data_type: str,
        entry_type: str,
        description: str,
        comment: Optional[str],
        deprecation: Optional[str],
        unit: Optional[str],
        min_value: Optional[float],
        max_value: Optional[float],
        allowed_values: Optional[List[str]]
    ):
        self.name = name
        self.data_type = data_type
        self.entry_type = entry_type
        self.description = description
        self.comment = comment
        self.deprecation = deprecation
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values

        # Derived attribute
        self.is_enum = self.data_type == "STRING" and self.allowed_values is not None

        # Value is optional and not yet fetched
        self.value = None

    def __str__(self):
        enum_info = f" [ENUM: {self.allowed_values}]" if self.is_enum else ""
        return (
            f"{self.name} [{self.data_type}] ({self.entry_type})"
            f"{enum_info} | Desc: {self.description}"
        )
