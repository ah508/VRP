This code was never intended to be seen by anyone other than me. 
I was going to rewrite it all in Rust after the related project was done, 
but the project got shot by covid and I had other things to worry about.
Since there was no reason to complete it, it never got cleaned up - hence
the mess.

I can't guarantee that everything works, nor that everything is perfectly
consistent. In particular, anything that involved the maps API will break if
you don't have a key, and could break even if you do depending on when the specs
were last updated. I wouldn't recommend trying to use any of that.

To start the program, run operate.py and cc to "demo2" (the only example client).
Not all of the displayed options will actually work, of course, but they're staying
for posterity.