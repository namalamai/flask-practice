import random

secret = random.randint(1, 10)
tries = 0

while True:
    guess = int(input("Guess a number (1-10): "))
    tries = tries + 1

    if guess == secret:
        print("🎉 Correct!")
        print("You guessed it in", tries, "tries.")
        break
    elif guess < secret:
        print("Too low!")
    else:
        print("Too high!")
