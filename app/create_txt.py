with open("file.txt", "w") as file:
    for i in range(0,409):
        file.write("/home/carlo/Desktop/BlockchainApp/blocks/block"+`i`+".json\n")