from dataclasses import dataclass
from typing import Any

try:
    from typing import dataclass_transform
except ImportError:
    # For Python < 3.11
    def dataclass_transform(**kwargs):
        def decorator(cls):
            return cls
        return decorator


@dataclass_transform(
    frozen_default=True,
    kw_only_default=True,
)
class _MaximusTypeMetaClass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[Any, ...],
        namespace: dict[str, Any],
    ) -> Any:
        class_ = super().__new__(cls, name, bases, namespace)
        if "__slots__" in namespace:
            return class_

        return dataclass(
            slots=True,
            frozen=True,
            kw_only=True,
        )(class_)


class MaximusType(metaclass=_MaximusTypeMetaClass):
    """Base type for all Maximus types."""
    pass