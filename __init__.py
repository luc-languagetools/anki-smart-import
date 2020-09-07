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
import random
import string
import os


ADDON_NAME = "Smart Import"

class SmartTextImporter(anki.importing.csvfile.TextImporter):

    def __init__(self, col, file: str) -> None:
        anki.importing.csvfile.TextImporter.__init__(self, col, file)
        self.allowHTML = True

    def foreignNotes(self):
        notes = super().foreignNotes()
        header_note = notes[0]
        notes = notes[1:]
        return notes

    def getHeaderRow(self):
        notes = super().foreignNotes()
        header_note = notes[0]
        return header_note
    
def getFile(parent, title, cb, filter="*.*", dir=None, key=None, multi=False, locations=[]):
    "Ask the user for a file."
    assert not dir or not key
    if not dir:
        dirkey = key + "Directory"
        dir = aqt.mw.pm.profile.get(dirkey, "")
    else:
        dirkey = None
    d = aqt.qt.QFileDialog(parent)
    mode = aqt.qt.QFileDialog.ExistingFiles if multi else aqt.qt.QFileDialog.ExistingFile
    d.setFileMode(mode)
    if os.path.exists(dir):
        d.setDirectory(dir)
    d.setWindowTitle(title)
    d.setNameFilter(filter)
    if len(locations) > 0:
        sidebarurls = [aqt.qt.QUrl.fromLocalFile(x) for x in locations]
        d.setSidebarUrls(sidebarurls)
        print("set sidebar urls")
    ret = []

    def accept():
        files = list(d.selectedFiles())
        if dirkey:
            dir = os.path.dirname(files[0])
            aqt.mw.pm.profile[dirkey] = dir
        result = files if multi else files[0]
        if cb:
            cb(result)
        ret.append(result)

    aqt.qt.qconnect(d.accepted, accept)
    if key:
        aqt.utils.restoreState(d, key)
    d.exec_()
    if key:
        aqt.utils.saveState(d, key)
    return ret and ret[0]

def smartImport():

    # launch import dialog
    # ====================

    # load configuration to access quick locations
    config = mw.addonManager.getConfig(__name__)
    locations = config['locations']
    print(locations)

    # ask user for file
    filt = "*.csv"
    file = getFile(mw, ADDON_NAME, None, key=ADDON_NAME, filter=filt, locations=locations)
    if not file:
        return
    file = str(file)

    # checkpoint so that user can undo
    # ================================
    mw.checkpoint(ADDON_NAME)

    importer = SmartTextImporter(mw.col, file)

    # get headers
    header_note = importer.getHeaderRow()

    field_names_text = "\n".join(header_note.fields)
    field_names_text = ADDON_NAME + ": found the following field names in file:\n" + field_names_text
    aqt.utils.showText(field_names_text)


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
            #print(f"model is eligible: {model_name}")
            eligible_models.append(model)


    # print(f"found eligible models: {str(eligible_models)}")
    if len(eligible_models) > 0:
        # ask user for the model
        model_index_selected = aqt.utils.chooseList(ADDON_NAME + ": Choose Note Type", [eligible_models[0]['name']])
        model_selected = eligible_models[model_index_selected]

    else:
        # create a model, ask user for the name of the model
        random_prefix = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
        (new_note_type_name, retval) = aqt.utils.getText("Enter new Note Type name", title=ADDON_NAME + ": New Note Type", default="New-Note-Type-" + random_prefix)
        #print(f"{new_note_type_name}, {retval}")

        if retval == 0:
            # user clicked cancel
            return

        # create the new note type
        new_model = mw.col.models.new(new_note_type_name)
        # add fields
        for field_name in header_note.fields:
            new_field = mw.col.models.newField(field_name)
            mw.col.models.addField(new_model, new_field)
        # add templates
        default_template = mw.col.models.newTemplate("Default")
        formatted_fields = ['{{' + field_name + '}}' for field_name in header_note.fields]
        formatted_template = ' '.join(formatted_fields)
        default_template['qfmt'] = formatted_template
        default_template['afmt'] = formatted_template
        mw.col.models.addTemplate(new_model, default_template)
        # save changes
        mw.col.models.add(new_model)
        mw.col.models.flush()
        model_selected = new_model

    #print(f"model selected: {str(model_selected)}")

    # indicate which model we want to use
    importer.model = model_selected
    # setup mapping, just need to use the order of the header row
    importer.mapping = header_note.fields

    # deck selection
    # ==============

    # get full list of decks
    all_decks = mw.col.decks.all()
    # ask user to select one
    deck_index_selected = aqt.utils.chooseList(ADDON_NAME + ": Choose Deck", [deck['name'] for deck in all_decks])
    deck_selected = all_decks[deck_index_selected]
 
    # select the target deck in the collection
    #print(f"deck selected: {str(deck_selected)}")
    did = deck_selected['id']
    importer.model["did"] = did
    mw.col.models.save(importer.model, updateReqs=False)
    mw.col.decks.select(did)


    # run importer
    importer.run()

    # show to the user how many notes we imported
    txt = ADDON_NAME + " complete."
    if importer.log:
        txt += "\n".join(importer.log)
    aqt.utils.showText(txt)    

    



# create a new menu item, "test"
action = aqt.QAction(ADDON_NAME + "...", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(smartImport)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
