import PySimpleGUI as sg

sg.theme("DarkBlue3")
sg.set_options(font=("Courier New", 16))

layout = [
    [sg.Input("Enter to generate an event",     key='Input1')],
    [sg.Input("Enter not to generate an event", key='Input2')],
]
window = sg.Window('Title', layout, finalize=True)
window['Input1'].bind("<Return>", "_Enter")

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Input1" + "_Enter":
        print(str(values['Input1']))

window.close()