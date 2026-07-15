print("Mini Calculator")

num1 = int(input("First number: "))
num2 = int(input("Second number: "))

print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")

choice = input("Choose (1-4): ")

if choice == "1":
    print("Answer:", num1 + num2)
elif choice == "2":
    print("Answer:", num1 - num2)
elif choice == "3":
    print("Answer:", num1 * num2)
elif choice == "4":
    print("Answer:", num1 / num2)
else:
    print("Invalid choice")
