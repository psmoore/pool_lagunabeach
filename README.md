# Laguna Beach pool — unofficial preview

A mock-up of [the City of Laguna Beach pool page](https://www.lagunabeachcity.net/government/departments/parks-recreation/pool).
The pool is closed for reconstruction, and the city's map of "nearby pools" is rebuilt as a live board. It shows what's in the
water at each of the eight pools right now, on how many lanes, until when, and how far each is from the Laguna Beach pool.
The schedules come from each operator's own sites, read on October 22, 2026, and live in [Pool Relay](https://www.poolrelay.com).

Not operated by or affiliated with the City of Laguna Beach or any pool listed.

- `build.py`: generates every page. Pool facts, the city's pin text and the corrections all live in `POOLS` there.
- `views.json`: Pool Relay share tokens, one lane-by-lane view per facility. Woollett's is the City of Irvine view.
- `finder.js`: the live board (`#finder`), one pool's day (`#today`) and the computed printable week (`#week`).
- `style.css`: page chrome after the city's theme, plus the finder.
