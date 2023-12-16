import os
def generate_negative_description_file():
    with open('neg.txt','w') as f:
        for filename in os.listdir('negative'):
            f.write('negative/' + filename + '\n')
    return

def generate_positive_description_file():
    with open('pos.txt','w') as f:
        for filename in os.listdir('positive'):
            f.write('negative/' + filename +'\n')
    return
generate_negative_description_file()
generate_positive_description_file()