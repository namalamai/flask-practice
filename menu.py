while True:
    print("\n=== My Menu ===")
    print("1. Say Hello")
    print("2. Show My Name")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        print("Hello! Welcome to Python.")
    elif choice == "2":
        print("My name is Lawan.")
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.")
