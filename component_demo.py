from component import Component, ComponentId


class DancerComponent(Component):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def dance(self):
        print(f"A dancing {self.name}")


class ManagerComponent(Component):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def make_c1_dance(self):
        print(f"{self.name} is making child1 dance...")
        c = self.get_component(ComponentId("child1"))
        if c is None:
            print("No child1 to make dance...")
            return
        if not isinstance(c, DancerComponent):
            print(f"Child1 is not a dancer, its a {type(c)}")
            return
        c.dance()


root = ManagerComponent("the root")
child1 = DancerComponent("a child")
child2 = DancerComponent("another child")
manager = ManagerComponent("a manager")
root.add_component(ComponentId("manager"), manager)

print(f"root.components = {root.components}")

manager.make_c1_dance()

root.add_component(ComponentId("child1"), child1)
root.add_component(ComponentId("child2"), child2)

root.make_c1_dance()
manager.make_c1_dance()

root.add_component(ComponentId("child1"), ManagerComponent("ignore me"), replace=True)
# root.add_component(ComponentId("child3"), child2)

manager.make_c1_dance()

print("--- Everybody dance ---")


def dance_if_able(x):
    if isinstance(x, DancerComponent):
        x.dance()
        return
    if isinstance(x, ManagerComponent):
        print(f"{x.name} is a manager, and managers dont dance")
        return


child1.on_components_and_self(dance_if_able)
