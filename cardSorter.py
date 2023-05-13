from requests import get
from sys import argv
from easygui import fileopenbox
import asyncio

FIELDS_TO_SORT_BY_STRING = "power toughness cmc"

NO_FILE = 1
INVALID_CARD_FIELD = 2
INVALID_CARD_NAME = 3
INVALID_FILE_FORMATTING = 4
REQUEST_FAILED = 5

class Card:
    name = ""
    value = None

    def __init__(self, name: str, value):
        self.name = name
        self.value = value

def pauseWithMessage(message: str):
    input(str(message))

def getFieldToSortBy():
    fieldsList = "    "+FIELDS_TO_SORT_BY_STRING.replace(" ", "\n    ")
    toPrint = f"Sort by:\n{(fieldsList)}\n"
    chosenField = input(toPrint)
    if chosenField not in FIELDS_TO_SORT_BY_STRING.split(" "):
        pauseWithMessage("Invalid field selected. Press any key to close...")
        exit(INVALID_CARD_FIELD)
    return chosenField

def isFileValid(firstFileLine: str):
    request = get("https://api.scryfall.com/cards/named", params={"exact": firstFileLine.strip('\n')})
    if request.status_code == 200:
        return True
    return False

def saveListToFile():
    pass

def printCardList(cardList: list, fieldName: str):
    minCardValue = cardList[0].value
    stringToPrintForCategory = f"{fieldName.capitalize()}: {minCardValue}"
    print(stringToPrintForCategory)
    for card in cardList:
        if card.value > minCardValue:
            print()
            minCardValue = card.value
            stringToPrintForCategory = f"{fieldName.upper()}: {str(card.value)}"
            print(stringToPrintForCategory)
        stringToPrintPerLine = f"    {card.name}"
        print(stringToPrintPerLine)

async def requestCard(cardName, fieldToSortBy, cards):
    request = get("https://api.scryfall.com/cards/named", params={"exact": cardName})
    if request.status_code == 200:
        cardDict = request.json()
        card = Card(cardDict["name"], cardDict[fieldToSortBy])
        cards.append(card)
    elif request.status_code == 404:
        pauseWithMessage(f'Request returned status code {request.status_code} while processing card named "{cardName}"\nCard not found\nPress any key to continue...')
        exit(INVALID_CARD_NAME)
    else:
        pauseWithMessage(f"Request returned status code {request.status_code}. Press any key to continue...")
        exit(REQUEST_FAILED)


async def main():
    if len(argv) > 1:
        print(argv)
    else:
        filePath = fileopenbox("Choose .txt file to parse", title='"File selection"', filetypes=['*.txt' ])
        file = open(filePath)
        if not file:
            pauseWithMessage('No file selected. Press any key to close...')
            exit(NO_FILE)
        cardNames = file.readlines()
        if len(cardNames) == 1 and not isFileValid(cardNames):
            pauseWithMessage('File is not correctly formatted. Press any key to close...')
            exit(INVALID_FILE_FORMATTING)
        fieldToSortBy = getFieldToSortBy()
        cards = []

        async with asyncio.TaskGroup() as tg:
            for cardName in cardNames:
                tg.create_task(
                    requestCard(cardName,fieldToSortBy, cards)
                )
        
        cards.sort(key=lambda card: card.value)
        printCardList(cards, fieldToSortBy)

if __name__ == "__main__":
    asyncio.run(main())