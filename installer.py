"""
Igatahes ma tahan programmi/skripti/koodi, mis
1. Listiks kõik failid teatud kaustas (nt Documents kaustas)
2. Küsiks kasutjaalt, mis .img faili ta tahab kasutada
3. Listiks kasutajale kõik kettad, v.a sda,
sest see on süsteemiketas ja seda pole vaja näppida
4. Küsiks kasutajalt, milliseid kettaid ta tahab kasutada
5. DD-ga .img kettale
"""
import os
from subprocess import run, PIPE
# from pathlib import Path


def listImages(folders: list) -> list:
    imageList = []
    for folder in folders:
        for file in os.listdir(folder):
            if file.endswith(".img"):
                imageList.append(
                    {"name": file, "path": os.path.join(folder, file)})
    return imageList


def selectImage(images: list) -> str:
    print("Which image would you like to use?: ")
    for i in range(len(images)):
        print(str(i) + ". " + images[i].get("name"))
    choice = input(
        "You can use a number or name of the file (0 or ubuntu.img):\n")
    if validateUser(choice, images):
        if choice.isdigit():
            return images[int(choice)].get("path")
        else:
            return next(image for image in images if image["name"] == choice).get("path")

    else:
        exit()


def validateUser(choice: str, images: list) -> bool:
    if choice.isdigit() and 0 <= int(choice) <= len(images)-1:
        return True
    elif any(d['name'] == choice for d in images):
        return True
    else:
        return False


def listDisks(excludedDisk: str) -> list:
    output = run('/bin/lsblk -d -o name'.split(), stdout=PIPE)
    disks = []
    for disk in output.stdout.decode('utf-8').split('\n'):
        if excludedDisk not in disk:
            if disk not in disks:
                if not (next((s for s in disks if disk in s), None)):
                    disks.append(disk)
    disks.remove('NAME')
    return disks


def selectDisks(disks: list) -> list:
    choice = []
    print("Select Disk(s) to write your image onto:")
    for i in range(len(disks)):
        print(str(i) + ". " + disks[i])
    userInput = input(" You can use numbers (0 or 0, 1, 2 or 0-2):\n")
    if validateDisks(disks, userInput):
        if userInput.isdigit():
            choice.append("/dev/" + disks[int(userInput)])
        elif "-" in userInput:
            i = 0
            for number in range(int(userInput.split("-")[0]),
                                int(userInput.split("-")[1])):
                choice.append("/dev/" + disks[int(number)])
        elif "," in userInput:
            for number in userInput.replace(" ", "").split(","):
                choice.append("/dev/" + disks[int(number)])
        else:
            exit()
        return choice
    else:
        exit()


def validateDisks(disks: list, userInput: str) -> bool:
    if userInput.isdigit() and 0 <= int(userInput) <= len(disks)-1:
        return True
    elif "-" in userInput:
        if (userInput.split("-")[0].isdigit() and
                userInput.split("-")[1].isdigit()):
            return True
    elif "," in userInput:
        for number in userInput.replace(" ", "").split(","):
            if (not number.isdigit() or
                    0 > int(number) or int(number) > len(disks)-1):
                return False
        return True
    else:
        return False


def writeImages(image: str, disks: list):
    cmd = "dcfldd if=" + image
    for disk in disks:
        cmd = cmd.__add__(" of=" + disk)

    print("Starting to write to disks, this may take a while")
    run(cmd.split(), stdout=PIPE).stdout.decode('UTF-8')
    print("Program finished")


if __name__ == "__main__":
    folders = ["/home/rasmus/Desktop/Images"]
    images = listImages(folders)
    image = selectImage(images)
    disks = listDisks("sda")
    userDisks = selectDisks(disks)
    writeImages(image, userDisks)
