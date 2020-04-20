#!/usr/bin/python3

stringOfWords = raw_input("Type in a bunch of words separated by a space: ")
listOfWords = stringOfWords.split(' ')

for word in listOfWords:
    longestWord = str()
    if len(word) > len(longestWord):
        longestWord = word

print("Th longest word is " + longestWord + " and it's length of characters is " + str(len(longestWord)) + ".")