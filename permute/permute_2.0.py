"""
Function to find the number of unique permutations of a word
This is given by the total permutations, n!, divided by the product
of all the repeat letter factorials
"""

import math

word = raw_input("Input a word: ")
wordList = list(word.lower())  #create list of word characters, all lowercase
multipleList = list(word)  #a list to record how many times each character appears
count = 0  #temporary variable to count number of appearances
divisor = 1  #variable to form divisor for final calculation

for i in range(0,len(word)): #scan word
    for j in range(0,len(word)): #comparing to each letter in turn
        if wordList[i] == wordList[j]:
            count += 1 #increment count if a match is found
    multipleList[i] = count #record number of matches
    count = 0

print multipleList

for i in range(1,len(word)+1): #construct the divisor
    print i, multipleList.count(i)
    if multipleList.count(i) != 0:
        divisor *= math.factorial(i)**(multipleList.count(i)/(i))

print 'There are',math.factorial(len(word))/divisor,'unique permutations of the word',word
