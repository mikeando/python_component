from typing import Dict, Optional, List, NewType, Iterable, Type, TypeVar, Set

ComponentId = NewType("ComponentId", str)


class Component(object):
    def __init__(self):
        self.parent: Optional["ComponentContainer"] = None


T = TypeVar("T")


def _get_types(t: Type) -> Set[Type]:
    result: Set[Type] = set()
    pending: Set[Type] = set()
    pending.add(t)
    while len(pending) > 0:
        v = pending.pop()
        result.add(v)
        v_sub_types = set(v.__bases__)
        v_sub_types -= result
        pending |= v_sub_types
    return result


class ComponentCollection(object):
    class _State(object):
        def __init__(self, typekey, *, is_unique: Optional[bool] = None, count=0):
            self.typekey = typekey
            self.is_unique = is_unique
            self.count = 0

        def can_mark_as(self, is_unique: Optional[bool]) -> Optional[str]:
            def _u(is_unique: bool) -> str:
                return "unique" if is_unique else "non-unique"

            # If we're not trying to enforce anything, or we're enforcing something that has already
            # been enforced, then we can skip it
            if (is_unique is None) or (is_unique == self.is_unique):
                return None

            if self.is_unique is not None:
                # We can only get here when the dont match
                return f"Trying to mark type {self.typekey.__name__} as {_u(is_unique)} but is already marked as {_u(self.is_unique)}"

            # So we must be in the self.is_unique = None case
            # If we're trying to mark it non-unique, thats OK
            if is_unique and self.count > 1:
                return f"Trying to mark type {self.typekey.__name__} as unique, but it already has {self.count} instances"
            return None

        def mark_as(self, is_unique: Optional[bool]):
            mesg = self.can_mark_as(is_unique)
            if mesg is not None:
                raise Exception(mesg)
            if is_unique is not None:
                self.is_unique = is_unique

        def can_add_instance(self):
            return self.count == 0 or not self.is_unique

        def add_instance(self):
            if self.is_unique and self.count != 0:
                raise Exception(
                    f"Trying to add a second instance of unique type {self.typekey.__name__}"
                )
            self.count += 1

    def __init__(self):
        self._components: List[Component] = []
        self._type_map: Dict[Type, ComponentCollection._State] = {}

    # Direct children of any of our parents are our components
    # as are our explicit components, and ourself.
    # But not the children of any of these.
    def components(self) -> Iterable[Component]:
        return self._components

    def get_component(self, component_type: Type[T]) -> T:
        v: List[T] = [x for x in self.components() if isinstance(x, component_type)]
        if len(v) == 0:
            raise Exception(
                f"No component of type {component_type.__name__} in collection"
            )
        if len(v) > 1:
            raise Exception(
                f"More than one component of type {component_type.__name__} in collection"
            )
        return v[0]

    def get_components(self, component_type: Type[T]) -> Iterable[T]:
        return (x for x in self.components() if isinstance(x, component_type))

    def add_component(self, component: Component, *, unique=None):
        if component.parent is not None:
            raise Exception("component already has a parent")

        component_type = type(component)

        # Inserting this element must respect the unique attribute
        # applied by all other inserts

        # Check whether we're overriding a component
        # in the parent chain too.
        base_types = _get_types(component_type)
        base_types -= set([object, Component, component_type])

        # Check pass - should not change anything
        state = self._type_map.get(component_type)
        if state is not None:
            mesg = state.can_mark_as(unique)
            if mesg is not None:
                raise Exception(mesg)
            if not state.can_add_instance():
                raise Exception(
                    f"Unable to add instance of type {component_type.__name__} as it is marked unique and already has a component added"
                )

        for t in base_types:
            state = self._type_map.get(t)
            if state is not None and not state.can_add_instance():
                raise Exception(
                    f"Unable to add instance of type {component_type.__name__} as its base type {t.__name__} is marked unique and a component with that base type has allready been added"
                )

        # We shouldn't get any failures here, as we've already checked
        # We explicitly mark the current type and check
        state = self._type_map.setdefault(
            component_type, ComponentCollection._State(component_type, is_unique=unique)
        )
        state.mark_as(unique)
        state.add_instance()

        # We then add each of the base types without enforcing the count
        for t in base_types:
            state = self._type_map.setdefault(
                component_type, ComponentCollection._State(t, is_unique=None)
            )
            state.add_instance()

        component.parent = self
        self._components.append(component)

    def mark_component_type(self, component_type: Type, is_unique: bool) -> None:
        state = self._type_map.setdefault(
            component_type,
            ComponentCollection._State(component_type, is_unique=is_unique),
        )
        state.mark_as(is_unique)
