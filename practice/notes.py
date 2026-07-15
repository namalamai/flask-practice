note = input("Write a note: ")

with open("mynotes.txt", "a") as file:
    file.write(note + "\n")

print("Note saved!")

