secret = 7

guess = int(input("Guess the secret number: "))

if guess == secret:
    print("Correct! You guessed it.")
else:
    print("Wrong! The secret number is", secret)
