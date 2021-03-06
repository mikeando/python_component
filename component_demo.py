from component import Component, ComponentCollection


class BaseComponent(Component):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"

class DancerComponent(BaseComponent):
    def dance(self):
        print(f"  {self.name} is dancing")

class ManagerComponent(BaseComponent):
    def make_them_dance(self):
        for dancer in self.parent.get_components(DancerComponent):
            print(f"{self.name} is making {dancer.name} dance...")
            dancer.dance()

class ParanoidManagerComponent(ManagerComponent):
    pass


root = ComponentCollection()

print("--- Getting the manager before he's added is an error ---")

try:
    manager = root.get_component(ManagerComponent)
except Exception as e:
    print("Expected Failure!!!")
    print(e)

root.add_component(ManagerComponent("the manager"), unique=True)

print("--- Trying to add a second manager ---")

try:
    root.add_component(ManagerComponent("another manager"))
except Exception as e:
    print("Expected Failure!!!")
    print(e)

print("--- Adding a Paranoid Manager is not OK as its derived from Manager ---")

try:
    root.add_component(ParanoidManagerComponent("another manager"))
except Exception as e:
    print("Expected Failure!!!")
    print(e)

print("--- Adding three dancers is fine since they're not unique ---")

root.add_component(DancerComponent("dancer 1"))
root.add_component(DancerComponent("dancer 2"))
root.add_component(DancerComponent("dancer 3"), unique=False)

print("--- But if we try to add a fourth and make it unqiue - that will fail ---")
try:
    root.add_component(DancerComponent("dancer 4"), unique=True)
except Exception as e:
    print("Expected Failure!!!")
    print(e)

print("--- Getting the dancer when there's more than one is an error ---")
try:
    dancer = root.get_component(DancerComponent)
except Exception as e:
    print("Expected Failure!!!")
    print(e)

print("--- But getting them all is fine ---")
print(f"dancers = {[x for x in root.get_components(DancerComponent)]}")

print("--- equally we can get all components ---")
print(f"components = {[x for x in root.components()]}")

print("--- Calling manager.make_them_dance ---")
root.get_component(ManagerComponent).make_them_dance()

# Because of how we're written the typing on get_component, mypy
# will know it returns a ManagerComponent and so complain that
#
# error: "ManagerComponent" has no attribute "hokey_pokey"
#
#      root.get_component(ManagerComponent).hokey_pokey()

print("--- Everybody dance ---")


def dance_if_able(x):
    if isinstance(x, DancerComponent):
        x.dance()
        return
    if isinstance(x, ManagerComponent):
        print(f"  {x.name} is a manager, and managers dont dance")
        return


for c in root.components():
    dance_if_able(c)

print("--- We can get a component by its class or any of its base classes ---")

c = ComponentCollection()
c.add_component(ParanoidManagerComponent("dude"))

p1 = c.get_component(ParanoidManagerComponent)
p2 = c.get_component(ManagerComponent)

print(f"p1 = c.get_component(ParanoidManagerComponent) = {p1}")
print(f"p2 = c.get_component(ManagerComponent) = {p2}")
print(f"(p1 == p2) = {p1 == p2}")
