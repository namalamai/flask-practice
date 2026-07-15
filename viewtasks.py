print("My To-Do List")
print("----------------")

with open("tasks.txt", "r") as file:
    for task in file:
        print(task.strip())
