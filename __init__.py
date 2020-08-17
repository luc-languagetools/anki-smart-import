# import the main window object (mw) from aqt
import aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
#from aqt.utils import getFile
import aqt.utils
import anki.lang
# import all of the Qt GUI library
import aqt.importing
from anki import hooks
from aqt import gui_hooks
import anki.importing.csvfile 


class SmartTextImporter(anki.importing.csvfile.TextImporter):

    def __init__(self, col, file: str) -> None:
        anki.importing.csvfile.TextImporter.__init__(self, col, file)

    def foreignNotes(self):
        notes = super().foreignNotes()
        header_note = notes[0]
        notes = notes[1:]
        return notes

    def getHeaderRow(self):
        notes = super().foreignNotes()
        header_note = notes[0]
        return header_note
    

def smartImport():
    # launch import dialog

    # ask user for file
    filt = "*.csv"
    file = aqt.utils.getFile(mw, anki.lang._("Smart Import"), None, key="import", filter=filt)
    if not file:
        return
    file = str(file)

    importer = SmartTextImporter(mw.col, file)
    # diag = SmartImportDialog(mw, importer)

    # try to get all of the headers in the file
    note_list = importer.foreignNotes()
    # grab the first one
    note = note_list[0]
    first_field = note.fields[0]

    # get headers
    header_note = importer.getHeaderRow()

    # aqt.utils.showInfo(str(first_field))
    # aqt.utils.showInfo(f"columns: {', '.join(header_note.fields)}")

    # look at existing models
    # mw.col.models <-- this is a ModelManager


    # model / note type selection
    # ===========================

    eligible_models = []

    all_models = mw.col.models.all()
    for model in all_models:
        # print(str(model))
        model_id = model['id']
        model_name = model['name']
        model_fields = model['flds']

        field_names = [x['name'] for x in model_fields]

        # iterate over the header note
        is_eligible = True
        for wanted_field in header_note.fields:
            if wanted_field not in field_names:
                # field not found
                is_eligible = False
        
        if is_eligible:
            print(f"model is eligible: {model_name}")
            eligible_models.append(model)

    print(f"found eligible models: {str(eligible_models)}")

    # ask user for the model
    model_index_selected = aqt.utils.chooseList("Smart Import: Choose Note Type", [eligible_models[0]['name']])
    model_selected = eligible_models[model_index_selected]
    print(f"model selected: {str(model_selected)}")

    # indicate which model we want to use
    importer.model = model_selected
    # setup mapping, just need to use the order of the header row
    importer.mapping = header_note.fields

    # deck selection
    # ==============

    # get full list of decks
    all_decks = mw.col.decks.all()
    # ask user to select one
    deck_index_selected = aqt.utils.chooseList("Smart Import: Choose Deck", [deck['name'] for deck in all_decks])
    deck_selected = all_decks[deck_index_selected]
 
    # select the target deck in the collection
    print(f"deck selected: {str(deck_selected)}")
    did = deck_selected['id']
    importer.model["did"] = did
    mw.col.decks.select(did)


    # checkpoint so that user can undo
    # ================================
    mw.checkpoint(f"Smart Import into deck {deck_selected['name']}")

    # run importer
    importer.run()



    



# create a new menu item, "test"
action = aqt.QAction("Smart Import...", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(smartImport)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
