import os
from datetime import datetime
from datetime import timedelta
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Documentation for network log lines found at https://github.com/quisquous/cactbot/blob/main/docs/LogGuide.md

# establish log folder
logFolder = 'logs'
fileList = os.listdir(logFolder)
print(f'Now reading from folder "{logFolder}"'
      f'\n------------------------------')

# keeps track of variables for each pull
pullStarted = False
pullCount = 0
currentPhase = 1
logNumber = 0

# pull set [[pull number], [pull length], [phase], [log number], [log file name]]
pullSet = [[], [], [], [], []]

# read through each file
for file in fileList:
    with open(f"{logFolder}/{file}", encoding='utf-8') as log:
        # keep track of log number
        logNumber += 1

        for i, line in enumerate(log):
            row = line.split('|')

            # search for Attack event on King Thordan caused by anything other than King Thordan himself
            if not pullStarted and row[0] == '21' and row[7] == 'King Thordan' and row[3] != 'King Thordan':
                pullStarted = True
                # keep track of time the pull started
                pullStartTime = datetime.strptime(row[1][:-14], '%Y-%m-%dT%H:%M:%S')

                currentPhase = 1

            # ignore re-instances
            if pullStarted and row[0] == '01' and row[3] == "Dragonsong's Reprise (Ultimate)":
                pullStarted = False

            # check for phase
            if pullStarted and currentPhase == 1 and row[0] == '21' and row[7] == 'Nidhogg':
                currentPhase = 2
            if pullStarted and currentPhase == 2 and row[0] == '21' and row[7] == 'Right Eye':
                currentPhase = 3
            if pullStarted and currentPhase == 3 and row[0] == '21' and row[7] == 'Ser Charibert':
                currentPhase = 4
            if pullStarted and currentPhase == 4 and row[0] == '21' and row[7] == 'King Thordan':
                currentPhase = 5
            if pullStarted and currentPhase == 5 and row[0] == '21' and row[7] == 'Nidhogg':
                currentPhase = 6
            if pullStarted and currentPhase == 6 and row[0] == '21' and row[7] == 'Dragon-king Thordan':
                currentPhase = 7

            # search for Wipe event
            if pullStarted and row[0] == '33' and row[3] == '40000005':
                pullStarted = False

                # keep track of time the pull ended
                pullEndTime = datetime.strptime(row[1][:-14], '%Y-%m-%dT%H:%M:%S')
                pullLength = pullEndTime - pullStartTime

                # ignore pulls of < 30 seconds, arbitrary number to ignore 'oops' pulls
                if pullLength > timedelta(seconds=30):
                    pullCount += 1

                    # populate pullSet fields
                    pullSet[0].append(pullCount)
                    pullSet[1].append(pullLength)
                    pullSet[2].append(currentPhase)
                    pullSet[3].append(logNumber)
                    pullSet[4].append(file)

    print(f"Reading log {logNumber} of {len(fileList)}")

# graph results
# phase color dictionary
phaseColorDict = {1: 'silver', 2: 'green', 3: 'blue', 4: 'cornflowerblue', 5: 'violet', 6: 'purple', 7: 'orange'}
phaseColor = []
for pull in pullSet[2]:
    phaseColor.append(phaseColorDict[pull])

# convert datetime objects into seconds
pullTimeSeconds = []
for i, time in enumerate(pullSet[1]):
    pullTimeSeconds.append(pullSet[1][i].total_seconds())

# plot pulls vs minutes
plt.figure(figsize=(18, 10))
plt.scatter(pullSet[0], pullTimeSeconds, color=phaseColor, s=25)

plt.xticks(np.arange(0, len(pullSet[0]) + 1, 100))
plt.yticks(np.arange(0, 1081, 120), np.arange(0, 19, 2))

plt.xlim(0, len(pullSet[0]) * 1.01)
plt.ylim(0, 1080)

# background colors for phases, this needs to be manually set
phaseTimings = {1: 205, 2: 345, 3: 440, 4: 482, 5: 685, 6: 900, 7: 1080}

# set the background color of the phases
for i, phase in enumerate(phaseTimings):
    # set first phase to be from 0 to phaseTimings[1]
    if i == 0:
        plt.axhspan(0, phaseTimings[1], color=phaseColorDict[1], alpha=0.2)
    else:
        # set the rest of the phases
        plt.axhspan(phaseTimings[i], phaseTimings[i + 1], color=phaseColorDict[i + 1], alpha=0.15)

# add legend
phaseNames = {1: 'King Thordan', 2: 'Nidhogg', 3: 'Eyes', 4: 'Rewind', 5: 'King Thordan II', 6: 'Double Dragons',
              7: 'The Dragon King'}
legendPatches = []
for i, phase in enumerate(phaseNames):
    legendPatches.append(mpatches.Patch(color=phaseColorDict[i + 1], label=phaseNames[i + 1], alpha=0.4))
legendPatches.reverse()

plt.grid(axis='x')
plt.legend(handles=legendPatches, loc=2, fontsize='x-large')

plt.xlabel('Pull Count')
plt.ylabel('Minutes')

plt.savefig('graph.jpg')
plt.show()

print(f"------------------------------\n"
      f"Parsing done! Graph output to 'graph.jpg'")
