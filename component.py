from typing import Optional, List, NewType, cast, Iterable, Tuple

ComponentId = NewType("ComponentId", str)


class Component(object):
    def __init__(self):
        self._parent: Optional["Component"] = None
        self._components: Dict[ComponentId, "Component"] = {}

    # Direct children of any of our parents are our components
    # as are our explicit components, and ourself.
    # But not the children of any of these.
    def components(self) -> Iterable[Tuple[Optional[ComponentId], "Component"]]:
        # TODO: We should check for infinite loops here.
        # But we can't get an infinite loop unless someone is
        # mucking with the parent pointers directly.
        p: "Component" = self
        while True:
            for cid, c in p._components.items():
                yield (cid, c)
            if p._parent is None:
                break
            p = p._parent
        yield (None, p)

    def get_component(self, cid: ComponentId) -> Optional["Component"]:
        return next((v for k, v in self.components() if k == cid), None)

    def add_component(self, id: ComponentId, component: "Component"):
        if component._parent is not None:
            raise Exception("component already has a parent")
        component._parent = self
        self._components[id] = component

    def find_components(self, fn):
        return next((v for k, v in self.components() if fn(k, v)), None)

    def on_components_and_self(self, fn):
        for k, v in self.components():
            fn(v)
