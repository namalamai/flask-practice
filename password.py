import random

characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

password = ""

for i in range(8):
    password = password + random.choice(characters)

print("Your password is:", password)
