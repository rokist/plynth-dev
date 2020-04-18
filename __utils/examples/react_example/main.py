import sys
import plynth
import plynth.js as js

R = js.React.createElement

def main():
    root = js.document.getElementById("react-root")
    js.ReactDOM.render(R(ReactApp.JsClass, None), root)


@plynth.js_class(superclass=js.React.Component)
class ReactApp:
    def __init__(self):
        self.this = plynth.js_this()

    def render(self):
        return R(
            'div', {}, '',
                R('h1', {}, "React Example"),
                R(MyComponent.JsClass, {"title": "Title1"}),
                R(MyComponent.JsClass, {"title": "Title2"})
        )


@plynth.js_class(superclass=js.React.Component)
class MyComponent:
    def __init__(self):
        self.this = plynth.js_this()
        self.this.state = {'num': 0}

    def render(self):
        this = self.this
        return R(
            'div', {}, '',
                R('h2', {}, this.props.title),
                R('button', {'className':'comp-button', 'onClick': this.onClick.bind(this)}, "Push"),
                R('div', {'className':'comp-num'}, this.state.num),
                R('hr'),
        )

    def onClick(self, e):
        this = self.this
        this.setState(lambda state: {'num': state.num+1})

