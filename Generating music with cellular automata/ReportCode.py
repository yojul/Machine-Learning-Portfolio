import numpy as np
import itertools
import random as r
from midiutil import MIDIFile
import seaborn as sns
import matplotlib.pyplot as plt

## Generate Rules and Seed for automata

def generate3statesRandomRule(r_size,states_nb) :
    x = list(range(states_nb))
    w = [ 0.5/(len(x)-1) for i in range(states_nb)]
    w[0] =0.5
    permutation = [p for p in itertools.product(x, repeat=2*r_size+1)]
    rule = {}
    for i in permutation :
        rule[i] = r.choices(x,weights = w)[0]
    return(rule)

def generateRandomRule(r_size) :
    x = [0,1]
    permutation = [p for p in itertools.product(x, repeat=2*r_size+1)]
    rule = {}
    for i in permutation :
        rule[i] = r.choices([0,1],weights = [0.55,0.45])[0]
    return(rule)


def generateSingleSeed(size) :
    seed = [ 0 for i in range(size)]
    seed[r.randint(0,size-1)] = 1
    return(seed)

def generateSeed(size,seed_density) :
    return([ r.choices([0,1], weights = [1- seed_density, seed_density])[0] for i in range(size)])

def simpleSingleSeed(size) :
    seed = [ 0 for i in range(size)]
    seed[size//2] = 1
    return(seed)

def random_sum_to(n, num_terms = None):
    num_terms = (num_terms or r.randint(2, n)) - 1
    a = r.sample(range(1, n), num_terms) + [0, n]
    list.sort(a)
    return [a[i+1] - a[i] for i in range(len(a) - 1)]

rule60 = { (1,1,1) : 0 , (1,1,0) : 0 , (1,0,1): 1 , (1,0,0) : 1, (0,1,1) : 1, (0,1,0) : 1, (0,0,1) : 0 , (0,0,0) : 0 }
rule62 = { (1,1,1) : 0 , (1,1,0) : 0 , (1,0,1): 1 , (1,0,0) : 1, (0,1,1) : 1, (0,1,0) : 1, (0,0,1) : 1 , (0,0,0) : 0 }
rule54 = { (1,1,1) : 0 , (1,1,0) : 0 , (1,0,1): 1 , (1,0,0) : 1, (0,1,1) : 0, (0,1,0) : 1, (0,0,1) : 1 , (0,0,0) : 0 }
rule30 = { (1,1,1) : 0 , (1,1,0) : 0 , (1,0,1): 0 , (1,0,0) : 1, (0,1,1) : 1, (0,1,0) : 1, (0,0,1) : 1 , (0,0,0) : 0 }
rule109 = { (1,1,1) : 0 , (1,1,0) : 1 , (1,0,1): 1 , (1,0,0) : 0, (0,1,1) : 1, (0,1,0) : 1, (0,0,1) : 0 , (0,0,0) : 1 }

# TO TEST : 105 & 109


## Generate automata


def generateAutomata(timeStepNumber,seed,rule) :
    #seed = generateSeed(size,0.01)
    #rule = generateRandomRule(r)
    r = len(list(rule.items())[0][0])//2
    print(r)
    size = len(seed)
    score = [seed]

    for t in range(timeStepNumber) :
        seed_plus =  [rule[tuple(seed[j+k - (j+k)//size * size] for k in range(-r,r+1))] for j in range(size) ]
        score.append(seed_plus)
        seed = seed_plus

    return(score)

## Visualization function

def plotAutomata(score) :
    sns.heatmap(score)
    plt.show()

""" Musical Part """

## Musical parameters

majorScaleInterval = [0,2,4,5,7,9,11] #Defines a Major scale
diatonicMajScaleInterval = [9,4,0,7,11,5]
minorScaleInterval = [0,2,3,5,7,9,10] #Defines a Minor scale
pentatonicScaleInterval = [0,3,5,7,9]
drumScale = [0,3,5,7,9]
chromaticScaleInterval = list(range(12))

## Convert Score to midi

def midiConverter2(interval, score, height, root_note,file_name,centernote_position = 0) :

    """
    Convert automata output into midi by specifying the scale, the root note and the amplitude of the melody (size of the window)
    """

    if centernote_position == 0 :
        centernote_position = len(score[0])//2

    scale = [ root_note + (i//len(interval))*12 +interval[i - i//len(interval)*len(interval)]  for i in range(height) ]

    score = np.array(score)
    score = score[:,centernote_position-height//2:centernote_position+height//2]*scale # MIDI note number

    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 150   # In BPM
    #volume   = 100   # 0-127, as per the MIDI standard
    timeStep = 0.5

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)
    CAraw = score
    score = score.transpose()

    print(score)

    for i,c in enumerate(score) :
        noteLength = 0
        note = False
        for j,n in enumerate(c) :
            if n != 0 :
                pitch = n
                noteLength+=1
                if noteLength == 1 :
                    start = j
                note = True
            if note and (n == 0 or j == len(list(c))-1 ) :
                Zero_rate = (list(CAraw[start]).count(0))/len(list(CAraw[start]))
                velocity =round((Zero_rate + (1-Zero_rate)*0.25)*127)
                print(start)
                MyMIDI.addNote(0, channel,pitch ,(start-1)*timeStep,noteLength*timeStep,velocity)
                #print(pitch , time + noteLength*(j),noteLength*timeStep)
                noteLength = 0
                note = False

    with open(file_name, "wb") as output_file:
        MyMIDI.writeFile(output_file)

    sns.heatmap(score)
    plt.show()

    return(score)


def midi3statesConverter(interval,score,height,root_note) :
    """
    Function that creates a midi with 2 tracks using 3 states in Automata
    """

    scale = [ root_note + (i//len(interval))*12 +interval[i - i//len(interval)*len(interval)]  for i in range(height) ]

    score = np.array(score)
    score = score[:,len(score[0])//2-height//2:len(score[0])//2+height//2] # MIDI note number
    track1 = score//2 * scale
    track2 = (score - (score//2)* 2)*scale
    track1_rythm = createRandomRythm(len(score))
    track2_rythm = createRandomRythm(len(score))

    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 150   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(2)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, c in enumerate(score):
        for p in range(len(score[i])) :
            if track1[i][p] != 0 :
                MyMIDI.addNote(0, channel,track1[i][p] , time + np.sum(track1_rythm[:i])/4, track1_rythm[i]/4, volume)
            if track2[i][p] != 0 :
                MyMIDI.addNote(1, channel,track2[i][p], time + np.sum(track2_rythm[:i])/4, track2_rythm[i]/4, volume)

    with open("test.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

## Multi-track composition using several windows

def MultiWindowGenerator() :
    score = generateAutomata(100,generateSeed(200,0.05),generateRandomRule(2))
    scale1 = r.sample(pentatonicScaleInterval,5)
    scale2 = r.sample(pentatonicScaleInterval,5)
    scale3 = r.sample(pentatonicScaleInterval,5)
    midiConverter2(scale1,score,6,54,'voice1.mid',centernote_position = 250)
    midiConverter2(scale2,score,6,54,'voice2.mid',centernote_position = 500)
    midiConverter2(scale3,score,10,54,'voice3.mid',centernote_position = 750)

def MultiStatesGenerator(n) :
    scoreRaw = np.array(generateAutomata(100,generateSeed(200,0.05),generate3statesRandomRule(2,n)))
    score = scoreRaw[:,len(scoreRaw[0])//2-20//2:len(scoreRaw[0])//2+20//2]
    sns.heatmap(np.transpose(score))
    plt.show()

    def ComputeMaxTrack(score,state) :
        scoreTrack = score//state
        return(scoreTrack,score - state*scoreTrack)

    track = []
    scale1 = pentatonicScaleInterval

    for i in range(1,n) :
        t,scoreRaw = ComputeMaxTrack(scoreRaw,n-i)
        track.append(t)
        midiConverter2(scale1,t,8,54,'voice'+str(i)+'.mid')