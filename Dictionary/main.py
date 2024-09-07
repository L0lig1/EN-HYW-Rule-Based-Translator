from nicegui import ui
from nicegui.events import ValueChangeEventArguments
from read_dict import dictionary
from converter import convert_to_western

exact_dict = {
    "Exact": True,
    "Like": False
}

def on_button_click(event):
    source_language = source_language_select.value
    destination_language = destination_language_select.value
    input_text = input_textarea.value


    if source_language == "Eastern Armenian" and destination_language == "Western Armenian":
        print("HEHREHRHEHRHER")
        translated_text = convert_to_western(input_text)# Translator.translate_western_to_eastern(input_text)
    else:
        translated_text = "Translation not supported yet."

    print(translated_text)
    output_textarea.set_value(translated_text)

ui.label("Eastern Armenian - Western Armenian Converter")

with ui.grid(columns = 2).classes('w-full'):
    source_language_select = ui.select(label="Source Language", options=["Western Armenian", "Eastern Armenian", "German"], value="Eastern Armenian")
    destination_language_select = ui.select(label="Destination Language", options=["Western Armenian", "Eastern Armenian", "German"], value="Western Armenian")

with ui.grid(columns = 2).classes('w-full'):
    input_textarea = ui.textarea(label='Input Text', placeholder='Input')
    output_textarea  = ui.textarea(label='Output Text', placeholder='Output')



result = ui.label()
ui.button('Translate', on_click=on_button_click)

ui.run()