import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

global xCords
global yCords
global yDelta

xCords = []
yCords = []

def animate(cords):
    print(cords, cords.dtype)
    xCords.append(cords[0])
    yCords.append(cords[1])
    ax1.clear()
    plt.xlabel('seconds')
    plt.ylabel('units')
    if(len(yCords) < 2 or yCords[-1] == yCords[-2]):
        ax1.plot(xCords,yCords, color = 'blue')
    elif(yCords[-1] < yCords[-2]):
        ax1.plot(xCords,yCords, color = 'red')
    elif(yCords[-1] > yCords[-2]):
        ax1.plot(xCords,yCords, color = 'green')
    


STYLE = "seaborn-v0_8-dark"
FILEPATH = "testData/liveData.csv"

cords = pd.read_csv(FILEPATH)
cords = cords.to_numpy()

style.use(STYLE)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


ani = animation.FuncAnimation(fig, animate, frames = cords, interval = 250, repeat = False)
plt.show()

    
