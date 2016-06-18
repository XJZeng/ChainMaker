# ChainMaker
Maya script to make chains


How to use:

1. Copy and paste script into python tab in script editor.

2. Make your curve (for the chain to go over) and single chain link geo. Make sure that:
  - The pivot of chain link geo is centered and geo is at world origins.
  - Freeze Transform applied to both curve and geo
   
3. Input name of curve into script text field.
4. Select the two tip vertices of the INNER RING of the chain link geo.
    - the reason should be obvious, but if you need an explanation, message me.
5. Hit Run
6. The chain is rigged to the spliine curve, so you can move it about by moving the control points


* copy and paste the code from chain_maker.py
**Refer to the attached SS.jpg for a visual explanation.
