import matplotlib.pyplot as plt

def parseLineForPrice(line):
    price = line.partition(',')[-1].rstrip(')\n')
    return float(price)

def plotPriceList(pricelist):
    plt.figure()
    plt.grid()
    # plt.hold() - is depricated
    hexmax = 16777215
    hexinc = int(hexmax / len(pricelist))
    hexcolor = hexmax
    graymax = 1.0
    grayinc = 1.0/len(pricelist)
    graycolor = graymax + grayinc
    for price in pricelist:
        hexcolor -= hexinc  # 1.0/length
        hexscale = str(hex(hexcolor)).replace('0x', '')
        hexscale = '#{0:0>6}'.format(hexscale)
        graycolor -= grayinc
        grayscale = (graycolor, graycolor, graycolor)
        print(grayscale)
        plt.plot(price, 'o', color=grayscale, label=str(grayscale))  # color=hexscale, marker='o', linewidth=0, label=str(color))
        plt.legend()
    #plt.show()

def main():
    file_name = 'C:\\Users\\StrebDM\\Downloads\\debug (3).log'
    priceList = []
    with open(file_name, 'r') as f:
        for l in f:
            if(l.startswith('loop')):
                if(priceList):
                    plotPriceList(priceList)
                priceList.clear()
                priceList.append([])
            if(l.startswith('price:')):
                priceList[-1].append(parseLineForPrice(l))
            if(l.startswith('*****')):
                priceList.append([])
    plt.show()


if __name__ == '__main__':
    main()