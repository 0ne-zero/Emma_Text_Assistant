from operator import truediv
# e = core.emma.Emma()
# while 1:
#     e.processing()


class O():
    def o(self):
        return 'o'
    def e(self):
        print(self.ev)
class E(O):
    def __init__(self) -> None:
        self.ov = super().o()
        self.e()
        self.ev ='e'

    def print_o(self):
        print(self.o)
e = E()
e.print_o()