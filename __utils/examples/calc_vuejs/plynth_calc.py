import os
import plynth
import plynth.js as js


document, window, console = js.document, js.window, js.console


class IntCalculator:
    def __init__(self):
        self._val = 0

    def current_value(self):
        return self._val
    
    def set_value(self, val):
        self._val = val


    def add(self, val):
        self._val += val

    def subtract(self, val):
        self._val -= val

    def multiply(self, val):
        self._val *= val

    def divide(self, val):
        self._val /= val


class CalcApp:
    def __init__(self):
        self.number_builder = ""
        self.op = ""
        self.calculator = IntCalculator()

        self.vue = js.Vue(dict(
            el="#calc-app",
            data=dict(
                mainText="0",
                subText=""
            ),
            methods = {"click_num":self.click_num, "click_op":self.click_op}
        ))
    

    def click_num(self, e):
        self.number_builder += e.target.dataset.num
        self.vue.mainText = self.number_builder

    def click_op(self, e):
        last_value = self.calculator.current_value()
        last_op = self.op
        self.op = e.target.dataset.op

        if self.number_builder.isdigit():
            new_num = int(self.number_builder)
            if last_op == "x":
                self.calculator.multiply(new_num)
            elif last_op == "+":
                self.calculator.add(new_num)
            elif last_op == "-":
                self.calculator.subtract(new_num)
            elif last_op == "/":
                self.calculator.divide(new_num)
            else:
                self.calculator.set_value(new_num)

        self.number_builder = ""

        if self.op == "c":
            self.vue.subText = f""
            self.calculator.set_value(0)
        elif self.op == "=":
            self.vue.subText = f"[ {str(last_value)} {last_op} {str(new_num)} ]"
        else:
            self.vue.subText = f"[ {str(self.calculator.current_value())} {self.op} ]"

        self.vue.mainText = str(self.calculator.current_value())



