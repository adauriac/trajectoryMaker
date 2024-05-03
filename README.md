# trajMaker
Following the plasmaGUI scheme create a trajectory for the robot
-------------------------------------------------------------------------------
A trajectory is a ordrered list of section.
A section is a string of words. There are at least 1+3+2 words.
- The first is the type of the trajectory
- The 3 following words are the coordonnates of the end point of the section
- The before the last is the speed
- The last indicates if the plasma is on
- There are as many words as wanted between word 4 end word -2, depending on the type

  
There is *no* duplicated information. Only the frame.grid holds the values.
Column and row start from 0. For exmaple my.grid.frame.gride_slaves(row=0,column=2)
holds the final x coordonnate of the first section.

tester.py can be usefull for arc2 and arc3 but is just for development
