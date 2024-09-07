from nicegui import ui
from nicegui.events import ValueChangeEventArguments
from read_dict import dictionary

exact_dict = {
    "Exact": True,
    "Like": False
}

def on_button_click(event):
    source_language = source_language_select.value
    destination_language = destination_language_select.value
    input_text = input_textarea.value
    d = dictionary()

    if not input_textarea.value:
        error_label.classes("visible")
        error_label.value = "Give an input"
        return
    try:
        if source_language == "Western Armenian" and destination_language == "Eastern Armenian":
            translated_text = d.get_eastern(input_text, exact_dict[exact.value])# Translator.translate_eastern_to_western(input_text)
        elif source_language == "Eastern Armenian" and destination_language == "Western Armenian":
            translated_text = d.get_western(input_text, exact_dict[exact.value])# Translator.translate_western_to_eastern(input_text)
        else:
            translated_text = "Translation not supported yet."
    except Exception as e:
        translated_text = str(e)


    print(translated_text)
    output_textarea.set_value(translated_text)

ui.label("Western Armenian - Eastern Armenian - German Dictionary")

with ui.grid(columns = 2).classes('w-full'):
    source_language_select = ui.select(label="Source Language", options=["Western Armenian", "Eastern Armenian", "German"], value="Western Armenian")
    destination_language_select = ui.select(label="Destination Language", options=["Western Armenian", "Eastern Armenian", "German"], value="Eastern Armenian")

with ui.grid(columns = 2).classes('w-full'):
    input_textarea  = ui.textarea(label='Input Text', placeholder='Input', on_change=on_button_click)
    output_textarea = ui.textarea(label='Output Text', placeholder='Output')

with ui.grid(columns = 2).classes('w-1/3'):
    exact = ui.select(label="Query Type", options=["Exact", "Like"], value="Exact").classes('w-full')




with ui.row():
    error_label = ui.label("").classes('invisible')

result = ui.label()
ui.button('Translate', on_click=on_button_click)

ui.run()