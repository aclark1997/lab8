1. I just looked at manually looked for some key links until all of them showed up, then went through and check them with finer detail.

 crawlAsync took 6.983 seconds to complete. <- batch_size=5
 crawlAsync took 4.472 seconds to complete. <- batch_size=20

 Notice we get a little bit of an improvement in speed when we look at 20 links at a time instead of 5. Probably we would
 continue to get better results the higher our batch_size until we reach the thread pool limit or whatever.
