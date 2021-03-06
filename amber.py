from pippi import dsp
from pippi import tune
import glob
import drums
import rhodes

speeds = [ 1.0, 1.5, 2.0 ]
scale = tune.fromdegrees([1, 4, 5, 3, 6, 8, 9], octave=2, root='e')
envs = ['line', 'tri', 'hann', 'phasor', 'impulse']
wforms = ['tri', 'saw', 'impulse', 'square']

notes = [ rhodes.rhodes(dsp.stf(dsp.rand(4, 7)), freq, 0.3) for freq in scale ]

layer = [ dsp.randchoose(notes) for i in range(40) ]
layer = [ dsp.pan(note, dsp.rand()) for note in layer ]
layer = [ dsp.amp(note, dsp.rand(0.1, 0.7)) for note in layer ]
layer = [ dsp.transpose(note, dsp.randchoose(speeds)) for note in layer ]
layer = [ dsp.pad(note, 0, dsp.mstf(dsp.rand(500, 2000))) for note in layer ]
layer = ''.join(layer)

out = ''

themes = [ [ dsp.transpose(note, dsp.randchoose(speeds)) for note in notes * 2 ] for theme in range(8) ]

arpsPlay, leadPlay, hatsPlay, blipsPlay, foldsPlay, kicksPlay, clapsPlay, bassPlay, themePlay = 0,0,0, 0,0,0, 0,0,0

intro_drone_pad_length, intro_drone_length, outro_drone_pad_length, outro_drone_length = 0,0,0,0


vary_sections = [ dsp.randint(7, 12) for vs in range(2) ]

def canPlay(section_name='none', index=0):
    if section_name == 'intro':
        return False
        #return index >= 0 and index <= 4

    if section_name == 'development':
        return index >= 0 and index <= 7 

    if section_name == 'jam':
        return index >= 8 and index <= 11

    if section_name == 'breakdown':
        return index >= 12 and index <= 15 

    if section_name == 'outro':
        return index >= 16 and index <= 18

    if section_name == 'ending':
        return index == 18

    if section_name == 'vary':
        return index in vary_sections

    if section_name == 'folds':
        return index >= 0 and index <= 18

    if section_name == 'blips':
        return index >= 4 and index <= 18

    if section_name == 'grains':
        return (index >= 3 and index <= 7) or (index >= 11 and index <= 17)

    if section_name == 'theme':
        return index >= 0 and index <= 18


    return True

sections = []

for bigoldsection in range(19):
    print 'Section index:', bigoldsection
    section = ''

    # Defaults
    numpoints = 20 
    numdests = 3 
    minvary = 10
    maxvary = 1800
    minfloor = 5
    maxfloor = 500

    if canPlay('intro', bigoldsection):
        numpoints = 40 
        numdests = 20
        minvary = 10
        maxvary = 800
        minfloor = 5
        maxfloor = 500

    if canPlay('development', bigoldsection):
        numpoints = 60 
        numdests = 20 
        minvary = 1
        maxvary = 200
        minfloor = 1 
        maxfloor = 200

    if canPlay('jam', bigoldsection):
        numpoints = 200
        numdests = 60
        minvary = 1
        maxvary = 35
        minfloor = 190
        maxfloor = 230

    if canPlay('breakdown', bigoldsection):
        numpoints = 100
        numdests = 90
        minvary = 1
        maxvary = 800
        minfloor = 20 
        maxfloor = 250

    if canPlay('outro', bigoldsection):
        numpoints = 50
        numdests = 10
        minvary = 10
        maxvary = 800
        minfloor = 5
        maxfloor = 200

    if canPlay('vary', bigoldsection):
        numpoints = dsp.randint(8, 100)
        numdests = numpoints / dsp.randint(2, 4)
        minvary = dsp.randint(1, 100)
        maxvary = dsp.randint(100, 300)
        minfloor = dsp.randint(10, 50)
        maxfloor = dsp.randint(50, 200)


    numpoints *= 3
    numdests *= 3

    lcurve = dsp.breakpoint([ dsp.rand() for l in range(numdests) ], numpoints)
    lvary = dsp.rand(minvary, maxvary)
    lfloor = dsp.rand(minfloor, maxfloor)
    lcurve = [ dsp.mstf(length * lvary + lfloor) for length in lcurve ]

# Break curve into variable size groups
    segments = []
    count = 0
    minseg = 1
    maxseg = 20
    while count < len(lcurve):
        segsize = dsp.randint(minseg, maxseg)
        seg = lcurve[count : count + segsize]
        segments += [ seg ]

        count += segsize

    print 'num segments in section:', len(segments)

    speeds = [ 1.0, 1.5, 1.25, 1.333 ]

    for seg_index, seg in enumerate(segments):
        tlen = sum(seg)
        layers = []

        def mixdrift(snd):
            if dsp.randint(0, 4) == 0:
                dsnd = dsp.drift(snd, dsp.rand(0.001, 0.04))
                snd = dsp.mix([ snd, dsp.amp(dsnd, 0.5) ])

            return snd

        if canPlay('folds', bigoldsection):
            if dsp.randint(0,1) == 0 or canPlay('jam', bigoldsection):
                # Guitar folds
                segsounds = []
                for length in seg:
                    sounds = [ dsp.cut(layer, dsp.randint(0, dsp.flen(layer) - length), length) for s in range(6) ]
                    sounds = dsp.mix(sounds)
                    segsounds += [ sounds ]

                segsounds = ''.join(segsounds)
                segsounds = mixdrift(segsounds)

                foldsPlay += 1
                layers += [ segsounds ]


        if canPlay('blips', bigoldsection):
            if dsp.randint(0,1) == 0 or canPlay('jam', bigoldsection):
                # Blips
                blips = []

                the_blip = dsp.amp(dsp.transpose(notes[0], 2.0 * dsp.randint(1, 3)), 0.4)
                blip = dsp.mix([ the_blip, dsp.amp(dsp.transpose(notes[0], 1.5 * dsp.randint(1, 4)), 0.4) ])

                for length in seg:
                    ba = dsp.cut(blip, dsp.randint(0, dsp.flen(blip) / 4), length / 2)
                    bb = dsp.cut(blip, dsp.randint(0, dsp.flen(blip) / 4), length / 2)

                    b = dsp.mix([dsp.pan(ba, dsp.rand()), dsp.pan(bb, dsp.rand())])

                    blips += [ dsp.pad(b, 0, length / 2) ]

                blips = dsp.alias(''.join(blips))
                blips = mixdrift(blips)

                blipsPlay += 1
                layers += [ blips ]


        single = [1] + ([0] * (len(seg) - 1))

        if canPlay('jam', bigoldsection) or canPlay('breakdown', bigoldsection):
            # Hats
            if len(seg) >= 2:
                if bigoldsection > 11:
                    maxbeats = dsp.randint(len(seg) / 2, len(seg))
                    hatpat = drums.eu(len(seg), maxbeats)
                else:
                    hatpat = [1] * len(seg)

                hats = drums.make(drums.hihat, hatpat, seg)
                hats = dsp.amp(hats, 0.3)
                hats = mixdrift(hats)

                if dsp.randint(0, 3) == 0:
                    hats = dsp.pine(hats, tlen, dsp.randchoose(scale))

                if canPlay('breakdown', bigoldsection):
                    hats = mixdrift(hats)

                hatsPlay += 1
                layers += [ hats ]

            # Percussion
            if bigoldsection > 9:
                kpat = single
            else:
                kpat = dsp.rotate(single, vary=True)

            kicks = drums.make(drums.kick, kpat, seg)

            if dsp.randint(0, 3) == 0:
                if dsp.randint(0,1):
                    kicks = dsp.pine(kicks, tlen, dsp.randchoose(scale))
                else:
                    kdivs = dsp.randint(2, 4)
                    kicks = dsp.pine(kicks, tlen / kdivs, dsp.randchoose(scale)) * kdivs


            if canPlay('breakdown', bigoldsection):
                kicks = mixdrift(kicks)

            kicksPlay += 1
            layers += [ dsp.amp(kicks, 0.4) ]

            if len(seg) > 4:
                maxbeats = dsp.randint(2, len(seg) / 2)
                clappat = drums.eu(len(seg), maxbeats)
                claps = drums.make(drums.clap, dsp.rotate(clappat, vary=True), seg)

                if dsp.randint(0, 3) == 0:
                    if dsp.randint(0,1):
                        claps = dsp.pine(claps, tlen, dsp.randchoose(scale))
                    else:
                        cdivs = dsp.randint(2, 4)
                        claps = dsp.pine(claps, tlen / cdivs, dsp.randchoose(scale)) * cdivs

                if canPlay('breakdown', bigoldsection):
                    claps = mixdrift(claps)

                clapsPlay += 1
                layers += [ dsp.amp(claps, 0.4) ]


        if canPlay('jam', bigoldsection) or canPlay('breakdown', bigoldsection):
            if dsp.randint(0,1) == 0 or canPlay('jam', bigoldsection):
                # Base
                def bass(amp, length, oct=2):
                    if amp == 0:
                        return dsp.pad('', 0, length)

                    #bass_note = ['d', 'g', 'a', 'b'][ bassPlay % 4 ]
                    bass_note = ['e', 'a', 'b', 'c#'][ bassPlay % 4 ]

                    out = dsp.tone(length, wavetype='square', freq=tune.ntf(bass_note, oct), amp=amp*0.2)
                    out = dsp.env(out, 'random')

                    return out

                if bassPlay % 5 == 0:
                    basses = bass(0.5, tlen, 1)
                else:
                    basses = drums.make(bass, dsp.rotate(single, vary=True), seg)

                bassPlay += 1
                layers += [ basses ]

            if dsp.randint(0,1) == 0 or canPlay('jam', bigoldsection):
                # Lead synth
                #lead_note = ['d', 'g', 'a', 'b'][ leadPlay % 4 ]
                lead_note = ['e', 'a', 'b', 'c#'][ leadPlay % 4 ]

                lead = dsp.tone(tlen / 2, wavetype='tri', freq=tune.ntf(lead_note, 4), amp=0.2)
                lead = dsp.env(lead, 'phasor')

                leadPlay += 1
                layers += [ lead ]

        def makeArps(seg, oct=3, reps=4):
            arp_degrees = [1,2,3,5,8,9,10]
            if dsp.randint(0,1) == 0:
                arp_degrees.reverse()

            arp_degrees = dsp.rotate(arp_degrees, vary=True)
            arp_notes = tune.fromdegrees(arp_degrees[:reps], oct, 'e')

            arps = ''

            arp_count = 0
            for arp_length in seg:
                arp_length /= 2
                arp_pair = arp_notes[ arp_count % len(arp_notes) ], arp_notes[ (arp_count + 1) % len(arp_notes) ]

                arp_one = dsp.tone(arp_length, wavetype='tri', freq=arp_pair[0], amp=0.075)
                arp_one = dsp.env(arp_one, 'random')

                arp_two = dsp.tone(arp_length, wavetype='tri', freq=arp_pair[1], amp=0.08)
                arp_two = dsp.env(arp_two, 'random')

                arps += arp_one + arp_two
                arp_count += 2

            arps = dsp.env(arps, 'random')
            arps = dsp.pan(arps, dsp.rand())

            return arps

        if canPlay('jam', bigoldsection) and dsp.randint(0,1) == 0:
            # Lead synth
            arpsPlay += 1
            arps = dsp.mix([ makeArps(seg, dsp.randint(1,3), dsp.randint(3, 4)) for a in range(dsp.randint(1, 4)) ]) 
            arps = mixdrift(arps)
            layers += [ arps ]

        if canPlay('breakdown', bigoldsection) and dsp.randint(0,1):
            # Lead synth
            arpsPlay += 1
            layers += [ makeArps(seg, dsp.randint(1, 3), dsp.randint(3, 6)) ]


        # Theme
        theme = dsp.randchoose(themes)
        theme_note = theme[i % len(theme)]

        if canPlay('theme', bigoldsection):
            if dsp.randint(0, 3) == 0 or not canPlay('intro', bigoldsection):
                note = dsp.alias(theme_note)
            else:
                note = theme_note

            if dsp.randint(0, 5) != 0:
                #if canPlay('intro', bigoldsection):
                    #tlen = dsp.flen(note)

                note = dsp.fill(note, tlen, silence=True)
            else:
                if tlen > dsp.flen(note) and not canPlay('jam', bigoldsection):
                    tlen = dsp.flen(note)
                else:
                    tlen = tlen * dsp.randint(1, 2)

            themePlay += 1
            layers += [ note ]


        # Grains
        def makeGrains(out, length=None, env=None):
            envs = ['tri', 'line', 'flat', 'sine', 'hann']
            out = dsp.vsplit(out, dsp.mstf(20), dsp.mstf(90))

            out = [ dsp.env(grain, 'hann') for grain in out ]
            out = [ dsp.pan(grain, dsp.rand()) for grain in out ]

            out = dsp.randshuffle(out)
            out = ''.join(out)
            out = dsp.env(out, dsp.randchoose(envs))

            return out

        if canPlay('grains', bigoldsection):
            #if dsp.randint(0,1) == 0 or canPlay('breakdown', bigoldsection):
            if dsp.randint(0,2) == 0:
                if canPlay('breakdown', bigoldsection) and dsp.randint(0,1) == 0:
                    gnote = dsp.transpose(theme_note, 1.5)
                else:
                    gnote = theme_note

                grains = [ makeGrains(gnote) for g in range(dsp.randint(4, 10)) ]
                for gi, grain in enumerate(grains):
                    if dsp.randint(0,1) == 0:
                        grains[gi] = dsp.transpose(grain, 2) * 2

                grains = dsp.mix(grains)
                grains = dsp.amp(grains, dsp.rand(0.25, 0.55))
                grains = mixdrift(grains)

                layers += [ grains ]

        sounds = dsp.fill(dsp.mix(layers), tlen)

        if canPlay('ending', bigoldsection):
            sounds = dsp.vsplit(sounds, dsp.mstf(1), dsp.mstf(200))
            sounds = [ dsp.pad(s, 0, dsp.mstf(dsp.rand(50, 250))) for s in sounds ]
            sounds = ''.join(sounds)

        subsection_length = dsp.flen(sounds)
        print 'subsection length:', dsp.fts(subsection_length), seg_index
         
        section += sounds


    section_length = dsp.flen(section)
    print 'section length:', dsp.fts(section_length)

    sections += [ section ]
    print

print 

out = ''.join(sections)

dsp.write(out, 'amber', timestamp=True)
