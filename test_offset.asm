INCLUDE "constants/hardware_constants.asm"
INCLUDE "constants/wram_constants.asm"

SECTION "Test", ROM0
test:
    PRINTLN "wTilemap = {wTilemap}"
    PRINTLN "wAttrmap = {wAttrmap}"
    PRINTLN "wAttrmap - wTilemap = {d:wAttrmap - wTilemap}"
    PRINTLN "Hex: {wAttrmap - wTilemap}"
