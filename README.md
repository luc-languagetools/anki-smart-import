# Anki Smart Import
## Automatically create Note Type when importing deck into Anki

This addon improves upon the Anki CSV import process by automatically mapping columns to fields for files which have a header row.

**Sample file:**

    Chinese,Pinyin,English
    我工作的那一层,wǒ gōngzuò de nà yīcéng,the floor that I work on
    开放办公区,kāifàng bàngōng qū,open office space
    有很多人走来走去,yǒu hěn duō rén zǒu lái zǒuqù,a lot of people are walking > around
    光线不是很好,guāngxiàn bùshì hěn hǎo,the lighting / illumination is not great

## Usage
Smart Import is available from the Anki main screen, under the *Tools* menu. 

1. User is asked to select a file (it must contain a header row)
2. Smart Import shows the field names for confirmation.
3. The addon then looks for a suitable Note Type, which contains at least all of the field names in the file.
4. If no suitable Note Type is found, the user is prompted to create one.
5. Import takes place, with a summary at the end.
6. If needed, the user can then undo the whole import (and potentially note type creation) using the Undo functionality.

## Installation
Smart Import supports both Anki 2.0 and Anki 2.1
### Anki 2.0 installation
Copy **smartimport.py** into your Anki addons folder, restart Anki.

## Configuration
### Anki 2.0
*Sidebar locations* on the import file dialog can be customized. Edit **smartimport.py** and edit the **LOCATIONS** array at the beginning of the file.
